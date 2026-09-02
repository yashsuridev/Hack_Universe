from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.database.database import get_db
from app.models.scan import Scan
from app.models.dependency import Dependency
from app.models.vulnerability import Vulnerability
from app.models.risk_finding import RiskFinding
from app.models.project import Project
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/scan/{scan_id}/json")
async def download_json_report(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
    risk_findings = db.query(RiskFinding).filter(RiskFinding.scan_id == scan_id).all()
    
    project = scan.project
    
    report = {
        "report_metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "report_version": "1.0",
            "generator": "SBOM Auditor",
        },
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
        },
        "scan": {
            "id": scan.id,
            "status": scan.status.value,
            "scan_type": scan.scan_type,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            "total_dependencies": scan.total_dependencies,
            "direct_dependencies": scan.direct_dependencies,
            "transitive_dependencies": scan.transitive_dependencies,
            "dev_dependencies": scan.dev_dependencies,
            "critical_count": scan.critical_count,
            "high_count": scan.high_count,
            "medium_count": scan.medium_count,
            "low_count": scan.low_count,
            "risk_score": scan.risk_score,
            "risk_level": scan.risk_level,
        },
        "dependencies": [
            {
                "id": d.id,
                "name": d.name,
                "ecosystem": d.ecosystem,
                "declared_version": d.declared_version,
                "resolved_version": d.resolved_version,
                "latest_version": d.latest_version,
                "recommended_version": d.recommended_version,
                "dependency_type": d.dependency_type.value,
                "purl": d.purl,
                "license": d.license,
                "status": d.status.value,
                "risk_score": d.risk_score,
                "has_lifecycle_scripts": d.has_lifecycle_scripts,
                "typosquatting_flag": d.typosquatting_flag,
                "dependency_path": d.dependency_path,
            }
            for d in dependencies
        ],
        "vulnerabilities": [
            {
                "id": v.id,
                "dependency_id": v.dependency_id,
                "dependency_name": v.dependency.name if v.dependency else "unknown",
                "osv_id": v.osv_id,
                "cve_id": v.cve_id,
                "ghsa_id": v.ghsa_id,
                "severity": v.severity.value,
                "cvss_score": v.cvss_score,
                "cvss_vector": v.cvss_vector,
                "summary": v.summary,
                "details": v.details,
                "affected_versions": v.affected_versions,
                "fixed_version": v.fixed_version,
                "references": v.references,
                "published_at": v.published_at.isoformat() if v.published_at else None,
                "modified_at": v.modified_at.isoformat() if v.modified_at else None,
            }
            for v in vulnerabilities
        ],
        "risk_findings": [
            {
                "id": f.id,
                "finding_type": f.finding_type.value,
                "severity": f.severity.value,
                "title": f.title,
                "description": f.description,
                "recommendation": f.recommendation,
                "evidence": f.evidence,
                "score_contribution": f.score_contribution,
            }
            for f in risk_findings
        ],
    }
    
    filename = f"{project.name}-scan-{scan_id}-report.json"
    
    return Response(
        content=json.dumps(report, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/scan/{scan_id}/summary")
async def get_report_summary(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
    risk_findings = db.query(RiskFinding).filter(RiskFinding.scan_id == scan_id).all()
    
    project = scan.project
    
    by_ecosystem = {}
    for d in dependencies:
        if d.ecosystem not in by_ecosystem:
            by_ecosystem[d.ecosystem] = {"total": 0, "direct": 0, "transitive": 0, "dev": 0}
        by_ecosystem[d.ecosystem]["total"] += 1
        if d.dependency_type.value == "direct":
            by_ecosystem[d.ecosystem]["direct"] += 1
        elif d.dependency_type.value == "transitive":
            by_ecosystem[d.ecosystem]["transitive"] += 1
        elif d.dependency_type.value == "development":
            by_ecosystem[d.ecosystem]["dev"] += 1
    
    vuln_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    for v in vulnerabilities:
        vuln_by_severity[v.severity.value] += 1
    
    risk_by_type = {}
    for f in risk_findings:
        ftype = f.finding_type.value
        if ftype not in risk_by_type:
            risk_by_type[ftype] = {"count": 0, "total_score": 0}
        risk_by_type[ftype]["count"] += 1
        risk_by_type[ftype]["total_score"] += f.score_contribution
    
    return {
        "project": {"id": project.id, "name": project.name},
        "scan": {
            "id": scan.id,
            "risk_score": scan.risk_score,
            "risk_level": scan.risk_level,
            "total_dependencies": scan.total_dependencies,
        },
        "dependency_stats": {
            "by_ecosystem": by_ecosystem,
            "by_type": {
                "direct": scan.direct_dependencies,
                "transitive": scan.transitive_dependencies,
                "development": scan.dev_dependencies,
            },
        },
        "vulnerability_stats": vuln_by_severity,
        "risk_findings_summary": risk_by_type,
        "top_recommendations": _generate_recommendations(vulnerabilities, risk_findings, dependencies),
    }


def _generate_recommendations(vulnerabilities: List[Vulnerability], risk_findings: List[RiskFinding], dependencies: List[Dependency]) -> List[dict]:
    recommendations = []
    
    critical_vulns = [v for v in vulnerabilities if v.severity.value == 'critical']
    if critical_vulns:
        for v in critical_vulns[:3]:
            recommendations.append({
                "priority": "critical",
                "action": f"Upgrade {v.dependency.name} to {v.fixed_version or 'latest fixed version'}",
                "reason": f"Critical vulnerability {v.osv_id} ({v.cve_id or 'N/A'})",
                "package": v.dependency.name,
                "current_version": v.dependency.resolved_version,
                "fixed_version": v.fixed_version,
            })
    
    high_vulns = [v for v in vulnerabilities if v.severity.value == 'high']
    if high_vulns:
        for v in high_vulns[:5]:
            recommendations.append({
                "priority": "high",
                "action": f"Upgrade {v.dependency.name} to {v.fixed_version or 'latest fixed version'}",
                "reason": f"High vulnerability {v.osv_id} ({v.cve_id or 'N/A'})",
                "package": v.dependency.name,
                "current_version": v.dependency.resolved_version,
                "fixed_version": v.fixed_version,
            })
    
    typo_findings = [f for f in risk_findings if f.finding_type.value == 'typosquatting']
    for f in typo_findings[:3]:
        recommendations.append({
            "priority": "high",
            "action": f"Verify {f.evidence.get('package', 'package')} is the intended package",
            "reason": f"Potential typosquatting of {f.evidence.get('similar_to', 'popular package')}",
            "package": f.evidence.get('package', 'unknown'),
        })
    
    lifecycle_findings = [f for f in risk_findings if f.finding_type.value == 'lifecycle_script']
    for f in lifecycle_findings[:3]:
        recommendations.append({
            "priority": "medium",
            "action": f"Review lifecycle scripts in {f.evidence.get('scripts', {}).keys() if f.evidence else 'package'}",
            "reason": "Package contains installation scripts that execute arbitrary code",
            "package": f.dependency.name if f.dependency else "unknown",
        })
    
    return recommendations[:10]