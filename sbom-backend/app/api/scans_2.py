from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models.scan import Scan
from app.models.dependency import Dependency, DependencyRelationship
from app.models.vulnerability import Vulnerability
from app.models.risk_finding import RiskFinding
from app.schemas.dependency import DependencyTreeNode
from app.schemas.scan import ScanComparisonResponse
from app.schemas.vulnerability import VulnerabilitySummaryResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/scans", tags=["scans"])


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
            children.append(build_tree(child_id))
        
        return DependencyTreeNode(
            id=dep.id,
            name=dep.name,
            version=dep.resolved_version or dep.declared_version or "unknown",
            ecosystem=dep.ecosystem,
            dependency_type=dep.dependency_type.value,
            status=dep.status.value,
            risk_score=dep.risk_score,
            vulnerabilities_count=vuln_count,
            children=children,
            parent_id=None,
        )
    
    root_deps = [d for d in dependencies if d.dependency_type.value in ('direct', 'development')]
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
            severity=v.severity.value,
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
        ftype = finding.finding_type.value
        if ftype not in breakdown:
            breakdown[ftype] = 0
        breakdown[ftype] += finding.score_contribution
    
    return {
        "score": scan.risk_score,
        "level": scan.risk_level,
        "max_score": 100.0,
        "breakdown": breakdown,
        "findings": [
            {
                "id": f.id,
                "type": f.finding_type.value,
                "severity": f.severity.value,
                "title": f.title,
                "description": f.description,
                "recommendation": f.recommendation,
                "score_contribution": f.score_contribution,
            }
            for f in risk_findings
        ],
    }


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
        risk_score_change=scan_2.risk_score - scan_1.risk_score,
    )