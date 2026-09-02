import asyncio
from typing import Dict, List, Optional, Any
import httpx
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class VersionChecker:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.cache: Dict[str, str] = {}
    
    async def close(self):
        await self.client.aclose()
    
    async def get_latest_version(self, ecosystem: str, name: str) -> Optional[str]:
        cache_key = f"{ecosystem}:{name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        version = None
        try:
            if ecosystem == 'npm':
                version = await self._get_npm_latest(name)
            elif ecosystem == 'pypi':
                version = await self._get_pypi_latest(name)
            elif ecosystem == 'maven':
                version = await self._get_maven_latest(name)
        except Exception as e:
            logger.warning("Failed to get latest version", ecosystem=ecosystem, name=name, error=str(e))
        
        if version:
            self.cache[cache_key] = version
        
        return version
    
    async def _get_npm_latest(self, name: str) -> Optional[str]:
        try:
            response = await self.client.get(
                f"{settings.npm_registry_url}/{name}",
                headers={"Accept": "application/vnd.npm.install-v1+json"}
            )
            response.raise_for_status()
            data = response.json()
            return data.get('dist-tags', {}).get('latest')
        except Exception as e:
            logger.warning("Failed to get npm latest version", name=name, error=str(e))
            return None
    
    async def _get_pypi_latest(self, name: str) -> Optional[str]:
        try:
            response = await self.client.get(f"{settings.pypi_api_url}/{name}/json")
            response.raise_for_status()
            data = response.json()
            return data.get('info', {}).get('version')
        except Exception as e:
            logger.warning("Failed to get PyPI latest version", name=name, error=str(e))
            return None
    
    async def _get_maven_latest(self, name: str) -> Optional[str]:
        try:
            if ':' in name:
                group_id, artifact_id = name.split(':', 1)
            else:
                return None
            
            params = {
                'q': f'g:{group_id} AND a:{artifact_id}',
                'core': 'gav',
                'rows': 1,
                'wt': 'json'
            }
            response = await self.client.get(settings.maven_central_url, params=params)
            response.raise_for_status()
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            if docs:
                return docs[0].get('latestVersion')
        except Exception as e:
            logger.warning("Failed to get Maven latest version", name=name, error=str(e))
            return None
    
    async def check_multiple(self, dependencies: List[Dict]) -> Dict[str, str]:
        results = {}
        semaphore = asyncio.Semaphore(10)
        
        async def check_one(dep):
            async with semaphore:
                version = await self.get_latest_version(dep['ecosystem'], dep['name'])
                if version:
                    results[f"{dep['ecosystem']}:{dep['name']}"] = version
        
        await asyncio.gather(*[check_one(dep) for dep in dependencies])
        return results


version_checker = VersionChecker()