from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models.dependency import Dependency
from app.models.vulnerability import Vulnerability
from app.schemas.dependency import DependencyDetailResponse, DependencyStatusResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dependencies", tags=["dependencies"])


@router.get("/{dependency_id}", response_model=DependencyDetailResponse)
async def get_dependency(dependency_id: int, db: Session = Depends(get_db)):
    dep = db.query(Dependency).filter(Dependency.id == dependency_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Dependency not found")
    
    vulns = db.query(Vulnerability).filter(Vulnerability.dependency_id == dependency_id).all()
    
    return DependencyDetailResponse(
        id=dep.id,
        scan_id=dep.scan_id,
        name=dep.name,
        ecosystem=dep.ecosystem,
        declared_version=dep.declared_version,
        resolved_version=dep.resolved_version,
        latest_version=dep.latest_version,
        recommended_version=dep.recommended_version,
        dependency_type=dep.dependency_type,
        purl=dep.purl,
        license=dep.license,
        license_url=dep.license_url,
        status=dep.status,
        risk_score=dep.risk_score,
        has_lifecycle_scripts=dep.has_lifecycle_scripts,
        lifecycle_scripts=dep.lifecycle_scripts,
        typosquatting_flag=dep.typosquatting_flag,
        typosquatting_details=dep.typosquatting_details,
        package_metadata=dep.package_metadata,
        dependency_path=dep.dependency_path,
        created_at=dep.created_at,
        updated_at=dep.updated_at,
        vulnerabilities=vulns,
        license_info=dep.license_info,
        relationships=dep.relationships,
    )


@router.get("/scan/{scan_id}/status-table", response_model=List[DependencyStatusResponse])
async def get_dependency_status_table(scan_id: int, db: Session = Depends(get_db)):
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    
    result = []
    for dep in dependencies:
        vulns = db.query(Vulnerability).filter(Vulnerability.dependency_id == dep.id).all()
        
        if dep.status.value == 'vulnerable':
            security = "Vulnerable"
            severity = max([v.severity.value for v in vulns]) if vulns else "unknown"
            fixed_version = min([v.fixed_version for v in vulns if v.fixed_version], default=None)
        elif dep.resolved_version and dep.latest_version and dep.resolved_version != dep.latest_version:
            from app.utils.version_utils import compare_versions
            if compare_versions(dep.resolved_version, dep.latest_version) < 0:
                security = "Review"
                severity = "info"
                fixed_version = None
            else:
                security = "Safe"
                severity = "none"
                fixed_version = None
        else:
            security = "Safe"
            severity = "none"
            fixed_version = None
        
        result.append(DependencyStatusResponse(
            package=dep.name,
            type=dep.dependency_type.value,
            declared=dep.declared_version,
            installed=dep.resolved_version,
            latest=dep.latest_version,
            security=security,
            severity=severity,
            fixed_version=fixed_version,
            risk=dep.risk_score,
            purl=dep.purl,
            license=dep.license,
            has_lifecycle_scripts=dep.has_lifecycle_scripts,
            typosquatting_flag=dep.typosquatting_flag,
            dependency_path=dep.dependency_path,
        ))
    
    return result