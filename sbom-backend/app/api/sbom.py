from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database.database import get_db
from app.models.scan import Scan
from app.models.sbom import SBOM
from app.models.dependency import Dependency
from app.models.vulnerability import Vulnerability
from app.schemas.sbom import SBOMResponse, SBOMExplorerFilters, SBOMExplorerResponse
from app.services.sbom_generator import SBOMGenerator
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sbom", tags=["sbom"])


@router.get("/scan/{scan_id}", response_model=SBOMResponse)
async def get_sbom(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    sbom_record = db.query(SBOM).filter(SBOM.scan_id == scan_id).first()
    if sbom_record and sbom_record.components:
        return SBOMResponse(
            bomFormat=sbom_record.bom_format,
            specVersion=sbom_record.spec_version,
            serialNumber=sbom_record.serial_number,
            version=sbom_record.version,
            metadata=sbom_record.metadata,
            components=sbom_record.components,
            services=sbom_record.services,
            dependencies=sbom_record.dependencies,
            compositions=sbom_record.compositions,
            vulnerabilities=sbom_record.vulnerabilities,
        )
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
    
    generator = SBOMGenerator()
    sbom_json = generator.generate(scan_id, dependencies, vulnerabilities, scan.project.name if scan.project else "unknown")
    
    return SBOMResponse(**sbom_json)


@router.get("/scan/{scan_id}/download")
async def download_sbom(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    dependencies = db.query(Dependency).filter(Dependency.scan_id == scan_id).all()
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
    
    generator = SBOMGenerator()
    sbom_json = generator.generate(scan_id, dependencies, vulnerabilities, scan.project.name if scan.project else "unknown")
    
    project_name = scan.project.name if scan.project else "project"
    filename = f"{project_name}-sbom.json"
    
    return Response(
        content=json.dumps(sbom_json, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/scan/{scan_id}/explorer", response_model=SBOMExplorerResponse)
async def explore_sbom(
    scan_id: int,
    ecosystem: Optional[str] = None,
    dependency_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    has_vulnerabilities: Optional[bool] = None,
    license: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
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
    if search:
        query = query.filter(Dependency.name.ilike(f"%{search}%"))
    if has_vulnerabilities is not None:
        if has_vulnerabilities:
            query = query.filter(Dependency.vulnerabilities.any())
        else:
            query = query.filter(~Dependency.vulnerabilities.any())
    if license:
        query = query.filter(Dependency.license.ilike(f"%{license}%"))
    
    total = query.count()
    dependencies = query.offset((page - 1) * page_size).limit(page_size).all()
    
    components = []
    for dep in dependencies:
        vulns = db.query(Vulnerability).filter(Vulnerability.dependency_id == dep.id).all()
        components.append({
            "id": dep.id,
            "name": dep.name,
            "version": dep.resolved_version or dep.declared_version,
            "ecosystem": dep.ecosystem,
            "dependency_type": dep.dependency_type.value,
            "purl": dep.purl,
            "license": dep.license,
            "status": dep.status.value,
            "vulnerabilities_count": len(vulns),
            "vulnerabilities": [v.osv_id for v in vulns],
            "latest_version": dep.latest_version,
            "recommended_version": dep.recommended_version,
            "has_lifecycle_scripts": dep.has_lifecycle_scripts,
            "typosquatting_flag": dep.typosquatting_flag,
        })
    
    filters = SBOMExplorerFilters(
        ecosystem=ecosystem,
        dependency_type=dependency_type,
        status=status,
        search=search,
        has_vulnerabilities=has_vulnerabilities,
        license=license,
    )
    
    return SBOMExplorerResponse(
        components=components,
        total=total,
        page=page,
        page_size=page_size,
        filters=filters,
    )