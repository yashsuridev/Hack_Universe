from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.database import get_db
from app.models.scan import Scan, ScanStatus
from app.models.dependency import Dependency, DependencyRelationship
from app.models.vulnerability import Vulnerability
from app.models.risk_finding import RiskFinding
from app.schemas.scan import ScanResponse, ScanDetailResponse, ScanComparisonResponse
from app.schemas.dependency import DependencySummaryResponse, DependencyTreeNode
from app.schemas.vulnerability import VulnerabilitySummaryResponse
from app.schemas.risk import RiskFindingSummaryResponse
from app.utils.version_utils import compare_versions
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/scans", tags=["scans"])


def _enum_val(v, default=""):
    if v is None:
        return default
    return v.value if hasattr(v, "value") else str(v)


@router.get("/{scan_id}")
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
    risk_findings = db.query(RiskFinding).filter(RiskFinding.scan_id == scan_id).all()
    
    dep_summaries = [
        {
            "id": d.id,
            "name": d.name,
            "ecosystem": d.ecosystem,
            "declared_version": d.declared_version,
            "resolved_version": d.resolved_version,
            "latest_version": d.latest_version,
            "recommended_version": d.recommended_version,
            "dependency_type": _enum_val(d.dependency_type, "direct"),
            "purl": d.purl,
            "license": d.license,
            "status": _enum_val(d.status, "unknown"),
            "risk_score": d.risk_score or 0.0,
            "has_lifecycle_scripts": d.has_lifecycle_scripts or False,
            "typosquatting_flag": d.typosquatting_flag or False,
        }
        for d in dependencies
    ]
    
    vuln_summaries = [
        {
            "id": v.id,
            "dependency_id": v.dependency_id,
            "dependency_name": v.dependency.name if v.dependency else "unknown",
            "osv_id": v.osv_id,
            "cve_id": v.cve_id,
            "ghsa_id": v.ghsa_id,
            "severity": _enum_val(v.severity, "unknown"),
            "cvss_score": v.cvss_score,
            "affected_versions": v.affected_versions,
            "fixed_version": v.fixed_version,
            "published_at": v.published_at.isoformat() if v.published_at else None,
        }
        for v in vulnerabilities
    ]
    
    risk_summaries = [
        {
            "id": f.id,
            "finding_type": _enum_val(f.finding_type, "unknown"),
            "severity": _enum_val(f.severity, "low"),
            "title": f.title,
            "description": f.description,
            "recommendation": f.recommendation,
            "score_contribution": f.score_contribution or 0.0,
        }
        for f in risk_findings
    ]
    
    return {
        "id": scan.id,
        "project_id": scan.project_id,
        "status": _enum_val(scan.status, "pending"),
        "scan_type": scan.scan_type or "full",
        "total_dependencies": scan.total_dependencies or 0,
        "direct_dependencies": scan.direct_dependencies or 0,
        "transitive_dependencies": scan.transitive_dependencies or 0,
        "dev_dependencies": scan.dev_dependencies or 0,
        "critical_count": scan.critical_count or 0,
        "high_count": scan.high_count or 0,
        "medium_count": scan.medium_count or 0,
        "low_count": scan.low_count or 0,
        "risk_score": scan.risk_score or 0.0,
        "risk_level": scan.risk_level or "LOW",
        "error_message": scan.error_message,
        "started_at": scan.started_at.isoformat() if scan.started_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "scan_metadata": scan.scan_metadata,
        "dependencies": dep_summaries,
        "vulnerabilities": vuln_summaries,
        "risk_findings": risk_summaries,
    }


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
            dependency_type=_enum_val(d.dependency_type, "direct"),
            purl=d.purl,
            license=d.license,
            status=_enum_val(d.status, "unknown"),
            risk_score=d.risk_score or 0.0,
            has_lifecycle_scripts=d.has_lifecycle_scripts or False,
            typosquatting_flag=d.typosquatting_flag or False,
        )
        for d in dependencies
    ]


@router.get("/{scan_id}/dependency-tree", response_model=List[DependencyTreeNode])
async def get_dependency_tree(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    relationships = db.query(DependencyRelationship).filter(DependencyRelationship.scan_id == scan_id).all()
    
    dep_map = {d.id: d for d in dependencies}
    children_map = {}
    
    for rel in relationships:
        if rel.parent_dependency_id not in children_map:
            children_map[rel.parent_dependency_id] = []
        children_map[rel.parent_dependency_id].append(rel.dependency_id)
    
    def build_tree(dep_id: int) -> DependencyTreeNode:
        dep = dep_map[dep_id]
        vuln_count = db.query(Vulnerability).filter(Vulnerability.dependency_id == dep_id).count()
        
        children = []
        for child_id in children_map.get(dep_id, []):
            if child_id in dep_map:
                children.append(build_tree(child_id))
        
        return DependencyTreeNode(
            id=dep.id,
            name=dep.name,
            version=dep.resolved_version or dep.declared_version or "unknown",
            ecosystem=dep.ecosystem,
            dependency_type=_enum_val(dep.dependency_type, "direct"),
            status=_enum_val(dep.status, "unknown"),
            risk_score=dep.risk_score or 0.0,
            vulnerabilities_count=vuln_count,
            children=children,
            parent_id=None,
        )
    
    root_deps = [d for d in dependencies if _enum_val(d.dependency_type, "direct") in ('direct', 'development')]
    tree = [build_tree(d.id) for d in root_deps]
    
    return tree


@router.get("/{scan_id}/vulnerabilities", response_model=List[VulnerabilitySummaryResponse])
async def get_scan_vulnerabilities(
    scan_id: int,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    query = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id)
    
    if severity:
        query = query.filter(Vulnerability.severity == severity)
    
    vulnerabilities = query.all()
    
    return [
        VulnerabilitySummaryResponse(
            id=v.id,
            dependency_id=v.dependency_id,
            dependency_name=v.dependency.name if v.dependency else "unknown",
            osv_id=v.osv_id,
            cve_id=v.cve_id,
            ghsa_id=v.ghsa_id,
            severity=_enum_val(v.severity, "unknown"),
            cvss_score=v.cvss_score,
            affected_versions=v.affected_versions,
            fixed_version=v.fixed_version,
            published_at=v.published_at,
        )
        for v in vulnerabilities
    ]


@router.get("/{scan_id}/risk", response_model=dict)
async def get_scan_risk(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    risk_findings = db.query(RiskFinding).filter(RiskFinding.scan_id == scan_id).all()
    
    breakdown = {}
    for finding in risk_findings:
        ftype = _enum_val(finding.finding_type, "unknown")
        if ftype not in breakdown:
            breakdown[ftype] = 0
        breakdown[ftype] += (finding.score_contribution or 0.0)
    
    return {
        "score": scan.risk_score or 0.0,
        "level": scan.risk_level or "LOW",
        "max_score": 100.0,
        "breakdown": breakdown,
        "findings": [
            {
                "id": f.id,
                "type": _enum_val(f.finding_type, "unknown"),
                "severity": _enum_val(f.severity, "low"),
                "title": f.title,
                "description": f.description,
                "recommendation": f.recommendation,
                "score_contribution": f.score_contribution or 0.0,
            }
            for f in risk_findings
        ],
    }


@router.get("/{scan_id}/dependency-status", response_model=List[dict])
async def get_dependency_status(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    
    result = []
    for dep in dependencies:
        vulns = db.query(Vulnerability).filter(Vulnerability.dependency_id == dep.id).all()
        
        has_known_vulns = len(vulns) > 0
        has_resolved = dep.resolved_version is not None
        has_latest = dep.latest_version is not None
        is_outdated = has_resolved and has_latest and compare_versions(dep.resolved_version, dep.latest_version) < 0
        
        has_lifecycle = dep.has_lifecycle_scripts
        is_unpinned = not dep.declared_version or dep.declared_version in ('*', 'latest', '')
        typosquatting = dep.typosquatting_flag
        
        if has_known_vulns:
            security = "Vulnerable"
            severity = max([_enum_val(v.severity, "unknown") for v in vulns]) if vulns else "unknown"
            fixed_version = min([v.fixed_version for v in vulns if v.fixed_version], default=None)
        elif is_outdated:
            security = "Review"
            severity = "info"
            fixed_version = dep.latest_version
        elif has_lifecycle or is_unpinned or typosquatting:
            security = "Review"
            severity = "info"
            fixed_version = None
        else:
            security = "Safe"
            severity = "none"
            fixed_version = None
        
        dep_path = " -> ".join(dep.dependency_path) if dep.dependency_path else "Direct"
        
        result.append({
            "package": dep.name,
            "type": _enum_val(dep.dependency_type, "direct"),
            "declared": dep.declared_version,
            "installed": dep.resolved_version,
            "latest": dep.latest_version,
            "security": security,
            "severity": severity,
            "fixed_version": fixed_version,
            "risk": dep.risk_score or 0.0,
            "purl": dep.purl,
            "license": dep.license,
            "has_lifecycle_scripts": dep.has_lifecycle_scripts or False,
            "typosquatting_flag": dep.typosquatting_flag or False,
            "dependency_path": dep_path,
        })
    
    return result


@router.post("/compare", response_model=ScanComparisonResponse)
async def compare_scans(scan_1_id: int, scan_2_id: int, db: Session = Depends(get_db)):
    scan_1 = db.query(Scan).filter(Scan.id == scan_1_id).first()
    scan_2 = db.query(Scan).filter(Scan.id == scan_2_id).first()
    
    if not scan_1 or not scan_2:
        raise HTTPException(status_code=404, detail="One or both scans not found")
    
    deps_1 = {f"{d.name}@{d.resolved_version}": d for d in db.query(Dependency).filter(Dependency.scan_id == scan_1_id).all()}
    deps_2 = {f"{d.name}@{d.resolved_version}": d for d in db.query(Dependency).filter(Dependency.scan_id == scan_2_id).all()}
    
    new_deps = [d for k, d in deps_2.items() if k not in deps_1]
    removed_deps = [d for k, d in deps_1.items() if k not in deps_2]
    
    vulns_1 = {v.osv_id: v for v in db.query(Vulnerability).filter(Vulnerability.scan_id == scan_1_id).all()}
    vulns_2 = {v.osv_id: v for v in db.query(Vulnerability).filter(Vulnerability.scan_id == scan_2_id).all()}
    
    new_vulns = [v for k, v in vulns_2.items() if k not in vulns_1]
    resolved_vulns = [v for k, v in vulns_1.items() if k not in vulns_2]
    
    version_changes = []
    for k, d1 in deps_1.items():
        if k in deps_2:
            d2 = deps_2[k]
            if d1.resolved_version != d2.resolved_version:
                version_changes.append({
                    "package": d1.name,
                    "old_version": d1.resolved_version,
                    "new_version": d2.resolved_version,
                })
    
    return ScanComparisonResponse(
        scan_1=scan_1,
        scan_2=scan_2,
        new_dependencies=new_deps,
        removed_dependencies=removed_deps,
        new_vulnerabilities=new_vulns,
        resolved_vulnerabilities=resolved_vulns,
        version_changes=version_changes,
        risk_score_change=(scan_2.risk_score or 0.0) - (scan_1.risk_score or 0.0),
    )