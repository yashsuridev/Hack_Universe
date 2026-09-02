import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import httpx
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class OSVQuery:
    package: Dict[str, str]
    version: str


@dataclass
class OSVVulnerability:
    id: str
    summary: Optional[str]
    details: Optional[str]
    severity: List[Dict[str, Any]]
    affected: List[Dict[str, Any]]
    references: List[Dict[str, Any]]
    published: Optional[str]
    modified: Optional[str]
    schema_version: str


class OSVCache:
    def __init__(self, ttl_hours: int = 24):
        self.cache: Dict[str, tuple] = {}
        self.ttl_seconds = ttl_hours * 3600
    
    def _make_key(self, ecosystem: str, name: str, version: str) -> str:
        return f"{ecosystem}:{name}@{version}"
    
    def get(self, ecosystem: str, name: str, version: str) -> Optional[List[Dict]]:
        key = self._make_key(ecosystem, name, version)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, ecosystem: str, name: str, version: str, data: List[Dict]):
        key = self._make_key(ecosystem, name, version)
        self.cache[key] = (data, time.time())


class OSVClient:
    def __init__(self, cache: Optional[OSVCache] = None):
        self.base_url = settings.osv_api_base_url
        self.batch_size = settings.osv_batch_size
        self.timeout = settings.osv_timeout
        self.cache = cache or OSVCache(settings.cache_ttl_hours)
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def close(self):
        await self.client.aclose()
    
    async def query_batch(self, queries: List[OSVQuery]) -> Dict[str, List[Dict]]:
        results = {}
        uncached_queries = []
        
        # Build lookup from key to OSVQuery
        key_to_query = {}
        for query in queries:
            key = f"{query.package['ecosystem']}:{query.package['name']}@{query.version}"
            key_to_query[key] = query
            cached = self.cache.get(query.package['ecosystem'], query.package['name'], query.version)
            if cached is not None:
                results[key] = cached
            else:
                uncached_queries.append(query)
        
        if not uncached_queries:
            return results
        
        for i in range(0, len(uncached_queries), self.batch_size):
            batch = uncached_queries[i:i + self.batch_size]
            batch_results = await self._query_batch_internal(batch)
            
            for key, vulns in batch_results.items():
                if key in key_to_query:
                    query = key_to_query[key]
                    self.cache.set(query.package['ecosystem'], query.package['name'], query.version, vulns)
                results[key] = vulns
        
        return results
    
    async def _query_batch_internal(self, queries: List[OSVQuery]) -> Dict[str, List[Dict]]:
        payload = {
            "queries": [
                {
                    "package": {
                        "ecosystem": q.package['ecosystem'],
                        "name": q.package['name'],
                    },
                    "version": q.version,
                }
                for q in queries
            ]
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/querybatch",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            
            results = {}
            for i, result in enumerate(data.get('results', [])):
                query = queries[i]
                key = f"{query.package['ecosystem']}:{query.package['name']}@{query.version}"
                vulns = result.get('vulns', [])
                results[key] = vulns
            
            return results
        
        except httpx.HTTPError as e:
            logger.error("OSV batch query failed", error=str(e))
            return {f"{q.package['ecosystem']}:{q.package['name']}@{q.version}": [] for q in queries}
    
    async def get_vulnerability(self, vuln_id: str) -> Optional[Dict]:
        try:
            response = await self.client.get(f"{self.base_url}/vulns/{vuln_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to fetch vulnerability details", vuln_id=vuln_id, error=str(e))
            return None
    
    def parse_vulnerability(self, vuln_data: Dict) -> OSVVulnerability:
        return OSVVulnerability(
            id=vuln_data.get('id', ''),
            summary=vuln_data.get('summary'),
            details=vuln_data.get('details'),
            severity=vuln_data.get('severity', []),
            affected=vuln_data.get('affected', []),
            references=vuln_data.get('references', []),
            published=vuln_data.get('published'),
            modified=vuln_data.get('modified'),
            schema_version=vuln_data.get('schema_version', '1.0.0'),
        )
    
    def extract_vulnerability_info(self, vuln_data: Dict) -> Dict:
        osv_vuln = self.parse_vulnerability(vuln_data)
        
        severity = "unknown"
        cvss_score = None
        cvss_vector = None
        
        db_specific = vuln_data.get('database_specific', {})
        if isinstance(db_specific, dict) and 'severity' in db_specific:
            db_sev = str(db_specific['severity']).lower()
            if db_sev in ['critical', 'high', 'medium', 'low']:
                severity = db_sev
            elif db_sev == 'moderate':
                severity = 'medium'
        
        for sev in osv_vuln.severity:
            if sev.get('type') == 'CVSS_V3':
                cvss_vector = sev.get('score')
                break
            elif sev.get('type') == 'CVSS_V2' and not cvss_vector:
                cvss_vector = sev.get('score')
        
        if cvss_score is None:
            if severity == 'critical':
                cvss_score = 9.5
            elif severity == 'high':
                cvss_score = 7.5
            elif severity == 'medium':
                cvss_score = 5.5
            elif severity == 'low':
                cvss_score = 2.5
            else:
                severity = 'medium'
                cvss_score = 5.0
        
        fixed_version = None
        affected_versions = []
        
        for affected in osv_vuln.affected:
            for range_info in affected.get('ranges', []):
                if range_info.get('type') in ['ECOSYSTEM', 'SEMVER']:
                    for event in range_info.get('events', []):
                        if 'fixed' in event:
                            fixed_version = event['fixed']
                        if 'introduced' in event:
                            affected_versions.append(f">= {event['introduced']}")
                        if 'last_affected' in event:
                            affected_versions.append(f"<= {event['last_affected']}")
        
        cve_id = None
        ghsa_id = None
        
        for ref in osv_vuln.references:
            if ref.get('type') == 'ADVISORY':
                url = ref.get('url', '')
                if 'cve' in url.lower() or 'CVE-' in url:
                    cve_id = url.split('/')[-1]
                elif 'ghsa' in url.lower() or 'GHSA-' in url:
                    ghsa_id = url.split('/')[-1]
        
        if not cve_id and osv_vuln.id.startswith('CVE-'):
            cve_id = osv_vuln.id
        if not ghsa_id and osv_vuln.id.startswith('GHSA-'):
            ghsa_id = osv_vuln.id
        
        return {
            'osv_id': osv_vuln.id,
            'cve_id': cve_id,
            'ghsa_id': ghsa_id,
            'severity': severity,
            'cvss_score': cvss_score,
            'cvss_vector': cvss_vector,
            'summary': osv_vuln.summary,
            'details': osv_vuln.details,
            'affected_versions': ', '.join(affected_versions) if affected_versions else None,
            'fixed_version': fixed_version,
            'references': osv_vuln.references,
            'published_at': osv_vuln.published,
            'modified_at': osv_vuln.modified,
        }


osv_client = OSVClient()