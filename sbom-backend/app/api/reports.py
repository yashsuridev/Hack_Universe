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
            "id": project.id if project else scan.project_id,
            "name": project.name if project else "Project",
            "description": project.description if project else None,
        },
        "scan": {
            "id": scan.id,
            "status": _enum_val(scan.status, "completed"),
            "scan_type": scan.scan_type or "full",
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
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
                "dependency_type": _enum_val(d.dependency_type, "direct"),
                "purl": d.purl,
                "license": d.license,
                "status": _enum_val(d.status, "unknown"),
                "risk_score": d.risk_score or 0.0,
                "has_lifecycle_scripts": d.has_lifecycle_scripts or False,
                "typosquatting_flag": d.typosquatting_flag or False,
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
                "severity": _enum_val(v.severity, "unknown"),
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
                "finding_type": _enum_val(f.finding_type, "unknown"),
                "severity": _enum_val(f.severity, "low"),
                "title": f.title,
                "description": f.description,
                "recommendation": f.recommendation,
                "evidence": f.evidence,
                "score_contribution": f.score_contribution or 0.0,
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


def _enum_val(v, default=""):
    if v is None:
        return default
    return v.value if hasattr(v, "value") else str(v)


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
        eco = d.ecosystem or "unknown"
        if eco not in by_ecosystem:
            by_ecosystem[eco] = {"total": 0, "direct": 0, "transitive": 0, "dev": 0}
        by_ecosystem[eco]["total"] += 1
        dtype = _enum_val(d.dependency_type, "direct").lower()
        if dtype == "direct":
            by_ecosystem[eco]["direct"] += 1
        elif dtype == "transitive":
            by_ecosystem[eco]["transitive"] += 1
        elif dtype in ("development", "dev"):
            by_ecosystem[eco]["dev"] += 1
    
    vuln_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    for v in vulnerabilities:
        sev = _enum_val(v.severity, "unknown").lower()
        if sev in vuln_by_severity:
            vuln_by_severity[sev] += 1
        else:
            vuln_by_severity["unknown"] += 1
    
    risk_by_type = {}
    for f in risk_findings:
        ftype = _enum_val(f.finding_type, "unknown")
        if ftype not in risk_by_type:
            risk_by_type[ftype] = {"count": 0, "total_score": 0}
        risk_by_type[ftype]["count"] += 1
        risk_by_type[ftype]["total_score"] += (f.score_contribution or 0.0)
    
    return {
        "project": {"id": project.id if project else scan.project_id, "name": project.name if project else "Project"},
        "scan": {
            "id": scan.id,
            "status": _enum_val(scan.status, "completed"),
            "risk_score": scan.risk_score or 0.0,
            "risk_level": scan.risk_level or "LOW",
            "total_dependencies": scan.total_dependencies or 0,
        },
        "dependency_stats": {
            "by_ecosystem": by_ecosystem,
            "by_type": {
                "direct": scan.direct_dependencies or 0,
                "transitive": scan.transitive_dependencies or 0,
                "development": scan.dev_dependencies or 0,
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
            dep_name = v.dependency.name if v.dependency else "package"
            dep_version = v.dependency.resolved_version if v.dependency else "unknown"
            recommendations.append({
                "priority": "critical",
                "action": f"Upgrade {dep_name} to {v.fixed_version or 'latest fixed version'}",
                "reason": f"Critical vulnerability {v.osv_id} ({v.cve_id or 'N/A'})",
                "package": dep_name,
                "current_version": dep_version,
                "fixed_version": v.fixed_version,
            })
    
    high_vulns = [v for v in vulnerabilities if v.severity.value == 'high']
    if high_vulns:
        for v in high_vulns[:5]:
            dep_name = v.dependency.name if v.dependency else "package"
            dep_version = v.dependency.resolved_version if v.dependency else "unknown"
            recommendations.append({
                "priority": "high",
                "action": f"Upgrade {dep_name} to {v.fixed_version or 'latest fixed version'}",
                "reason": f"High vulnerability {v.osv_id} ({v.cve_id or 'N/A'})",
                "package": dep_name,
                "current_version": dep_version,
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