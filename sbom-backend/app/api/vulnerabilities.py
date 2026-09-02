from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models.vulnerability import Vulnerability
from app.models.dependency import Dependency
from app.schemas.vulnerability import VulnerabilityDetailResponse, VulnerabilityStatsResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("/{vulnerability_id}", response_model=VulnerabilityDetailResponse)
async def get_vulnerability(vulnerability_id: int, db: Session = Depends(get_db)):
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    return VulnerabilityDetailResponse(
        id=vuln.id,
        scan_id=vuln.scan_id,
        dependency_id=vuln.dependency_id,
        osv_id=vuln.osv_id,
        cve_id=vuln.cve_id,
        ghsa_id=vuln.ghsa_id,
        severity=vuln.severity,
        cvss_score=vuln.cvss_score,
        cvss_vector=vuln.cvss_vector,
        summary=vuln.summary,
        details=vuln.details,
        affected_versions=vuln.affected_versions,
        fixed_version=vuln.fixed_version,
        references=vuln.references,
        published_at=vuln.published_at,
        modified_at=vuln.modified_at,
        created_at=vuln.created_at,
        dependency=None,
    )


@router.get("/scan/{scan_id}/stats", response_model=VulnerabilityStatsResponse)
async def get_vulnerability_stats(scan_id: int, db: Session = Depends(get_db)):
    vulns = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
    
    stats = {
        "total": len(vulns),
        "critical": sum(1 for v in vulns if v.severity.value == 'critical'),
        "high": sum(1 for v in vulns if v.severity.value == 'high'),
        "medium": sum(1 for v in vulns if v.severity.value == 'medium'),
        "low": sum(1 for v in vulns if v.severity.value == 'low'),
        "unknown": sum(1 for v in vulns if v.severity.value == 'unknown'),
        "by_ecosystem": {},
        "by_severity": {},
    }
    
    for v in vulns:
        eco = v.dependency.ecosystem if v.dependency else "unknown"
        sev = v.severity.value
        
        if eco not in stats["by_ecosystem"]:
            stats["by_ecosystem"][eco] = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
        stats["by_ecosystem"][eco][sev] += 1
        
        stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
    
    return VulnerabilityStatsResponse(**stats)