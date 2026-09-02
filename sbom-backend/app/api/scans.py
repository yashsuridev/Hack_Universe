from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.database import get_db
from app.models.scan import Scan, ScanStatus
from app.models.dependency import Dependency
from app.models.vulnerability import Vulnerability
from app.models.risk_finding import RiskFinding
from app.schemas.scan import ScanResponse, ScanDetailResponse, ScanComparisonResponse
from app.schemas.dependency import DependencySummaryResponse, DependencyTreeNode
from app.schemas.vulnerability import VulnerabilitySummaryResponse
from app.schemas.risk import RiskFindingSummaryResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/scans", tags=["scans"])


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
    risk_findings = db.query(RiskFinding).filter(RiskFinding.scan_id == scan_id).all()
    
    dep_summaries = [
        DependencySummaryResponse(
            id=d.id,
            name=d.name,
            ecosystem=d.ecosystem,
            declared_version=d.declared_version,
            resolved_version=d.resolved_version,
            latest_version=d.latest_version,
            recommended_version=d.recommended_version,
            dependency_type=d.dependency_type.value,
            purl=d.purl,
            license=d.license,
            status=d.status.value,
            risk_score=d.risk_score,
            has_lifecycle_scripts=d.has_lifecycle_scripts,
            typosquatting_flag=d.typosquatting_flag,
        )
        for d in dependencies
    ]
    
    vuln_summaries = [
        VulnerabilitySummaryResponse(
            id=v.id,
            dependency_id=v.dependency_id,
            dependency_name=v.dependency.name if v.dependency else "unknown",
            osv_id=v.osv_id,
            cve_id=v.cve_id,
            ghsa_id=v.ghsa_id,
            severity=v.severity.value,
            cvss_score=v.cvss_score,
            affected_versions=v.affected_versions,
            fixed_version=v.fixed_version,
            published_at=v.published_at,
        )
        for v in vulnerabilities
    ]
    
    risk_summaries = [
        RiskFindingSummaryResponse(
            id=f.id,
            finding_type=f.finding_type.value,
            severity=f.severity.value,
            title=f.title,
            description=f.description,
            recommendation=f.recommendation,
            score_contribution=f.score_contribution,
        )
        for f in risk_findings
    ]
    
    return ScanDetailResponse(
        id=scan.id,
        project_id=scan.project_id,
        status=scan.status,
        scan_type=scan.scan_type,
        total_dependencies=scan.total_dependencies,
        direct_dependencies=scan.direct_dependencies,
        transitive_dependencies=scan.transitive_dependencies,
        dev_dependencies=scan.dev_dependencies,
        critical_count=scan.critical_count,
        high_count=scan.high_count,
        medium_count=scan.medium_count,
        low_count=scan.low_count,
        risk_score=scan.risk_score,
        risk_level=scan.risk_level,
        error_message=scan.error_message,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        created_at=scan.created_at,
        scan_metadata=scan.scan_metadata,
        dependencies=dep_summaries,
        vulnerabilities=vuln_summaries,
        risk_findings=risk_summaries,
    )


@router.get("/{scan_id}/dependencies", response_model=List[DependencySummaryResponse])
async def get_scan_dependencies(
    scan_id: int,
    ecosystem: Optional[str] = None,
    dependency_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    query = db.query(Dependency).filter(Dependency.scan_id == scan_id)
    
    if ecosystem:
        query = query.filter(Dependency.ecosystem == ecosystem)
    if dependency_type:
        query = query.filter(Dependency.dependency_type == dependency_type)
    if status:
        query = query.filter(Dependency.status == status)
    
    dependencies = query.all()
    
    return [
        DependencySummaryResponse(
            id=d.id,
            name=d.name,
            ecosystem=d.ecosystem,
            declared_version=d.declared_version,
            resolved_version=d.resolved_version,
            latest_version=d.latest_version,
            recommended_version=d.recommended_version,
            dependency_type=d.dependency_type.value,
            purl=d.purl,
            license=d.license,
            status=d.status.value,
            risk_score=d.risk_score,
            has_lifecycle_scripts=d.has_lifecycle_scripts,
            typosquatting_flag=d.typosquatting_flag,
        )
        for d in dependencies
    ]


@router.get("/{scan_id}/dependency-status", response_model=List[dict])
async def get_dependency_status(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    
    result = []
    for dep in dependencies:
        vulns = db.query(Vulnerability).filter(Vulnerability.dependency_id == dep.id).all()
        
        # Determine security status
        has_known_vulns = len(vulns) > 0
        has_resolved = dep.resolved_version is not None
        has_latest = dep.latest_version is not None
        is_outdated = has_resolved and has_latest and compare_versions(dep.resolved_version, dep.latest_version) < 0
        
        # Check for risk indicators
        has_lifecycle = dep.has_lifecycle_scripts
        is_unpinned = not dep.declared_version or dep.declared_version in ('*', 'latest', '')
        typosquatting = dep.typosquatting_flag
        
        if has_known_vulns:
            # Package has known vulnerabilities - classify as Vulnerable
            security = "Vulnerable"
            severity = max([v.severity.value for v in vulns]) if vulns else "unknown"
            fixed_version = min([v.fixed_version for v in vulns if v.fixed_version], default=None)
        elif is_outdated:
            # No known vulnerabilities, but installed version is outdated
            # Check if there are update available indicators
            security = "Review"
            severity = "info"
            fixed_version = dep.latest_version
        elif has_lifecycle or is_unpinned or typosquatting:
            # No known vulnerabilities, but has risk indicators
            security = "Review"
            severity = "info"
            fixed_version = None
        else:
            # No known vulnerabilities, current version is up to date
            security = "Safe"
            severity = "none"
            fixed_version = None
        
        dep_path = " -> ".join(dep.dependency_path) if dep.dependency_path else "Direct"
        
        result.append({
            "package": dep.name,
            "type": dep.dependency_type.value,
            "declared": dep.declared_version,
            "installed": dep.resolved_version,
            "latest": dep.latest_version,
            "security": security,
            "severity": severity,
            "fixed_version": fixed_version,
            "risk": dep.risk_score,
            "purl": dep.purl,
            "license": dep.license,
            "has_lifecycle_scripts": dep.has_lifecycle_scripts,
            "typosquatting_flag": dep.typosquatting_flag,
            "dependency_path": dep_path,
        })
    
    return result