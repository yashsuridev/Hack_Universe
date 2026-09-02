from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from pathlib import Path

from app.database.database import get_db
from app.models.project import Project, ProjectStatus
from app.models.scan import Scan, ScanStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse, ProjectEcosystemResponse, ScanSummaryResponse
from app.schemas.scan import ScanResponse, ScanCreate
from app.services.project_scanner import scan_project
from app.utils.file_security import validate_zip_file
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    logger.info("Project created", project_id=db_project.id, name=db_project.name)
    return db_project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.status != ProjectStatus.DELETED).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.status != ProjectStatus.DELETED).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    latest_scan = db.query(Scan).filter(Scan.project_id == project_id).order_by(Scan.created_at.desc()).first()
    
    ecosystems = []
    for eco in project.ecosystems:
        ecosystems.append(ProjectEcosystemResponse(
            id=eco.id,
            ecosystem=eco.ecosystem,
            manifest_path=eco.manifest_path,
            lockfile_path=eco.lockfile_path,
            detected_at=eco.detected_at,
        ))
    
    scan_summary = None
    if latest_scan:
        scan_summary = ScanSummaryResponse(
            id=latest_scan.id,
            status=latest_scan.status.value,
            risk_score=latest_scan.risk_score,
            risk_level=latest_scan.risk_level,
            total_dependencies=latest_scan.total_dependencies,
            critical_count=latest_scan.critical_count,
            high_count=latest_scan.high_count,
            medium_count=latest_scan.medium_count,
            low_count=latest_scan.low_count,
            created_at=latest_scan.created_at,
        )
    
    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        ecosystems=ecosystems,
        scan_count=db.query(Scan).filter(Scan.project_id == project_id).count(),
        latest_scan=scan_summary,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.status != ProjectStatus.DELETED).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    logger.info("Project updated", project_id=project.id)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.status = ProjectStatus.DELETED
    db.commit()
    logger.info("Project deleted", project_id=project_id)


@router.post("/{project_id}/upload", response_model=ScanResponse)
async def upload_and_scan(
    project_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id, Project.status != ProjectStatus.DELETED).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")
    
    file_size = 0
    chunk_size = 8192
    temp_filename = f"{uuid.uuid4().hex}.zip"
    temp_path = UPLOAD_DIR / temp_filename
    
    try:
        with open(temp_path, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                if file_size > settings.upload_max_size:
                    raise HTTPException(status_code=413, detail=f"File too large. Max size: {settings.upload_max_size / (1024*1024)}MB")
                buffer.write(chunk)
    except HTTPException:
        if temp_path.exists():
            temp_path.unlink()
        raise
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    valid, msg = validate_zip_file(str(temp_path))
    if not valid:
        temp_path.unlink()
        raise HTTPException(status_code=400, detail=f"Invalid ZIP file: {msg}")
    
    scan = Scan(project_id=project_id, status=ScanStatus.PENDING, scan_type="full")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    background_tasks.add_task(run_scan_task, scan.id, str(temp_path))
    
    logger.info("Scan queued", scan_id=scan.id, project_id=project_id)
    return scan


async def run_scan_task(scan_id: int, zip_path: str):
    from app.database.database import SessionLocal
    from app.services.project_scanner import scan_project
    
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            await scan_project(db, scan.project_id, zip_path, scan_id)
    except Exception as e:
        logger.error("Background scan failed", scan_id=scan_id, error=str(e))
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            db.commit()
    finally:
        db.close()
        if os.path.exists(zip_path):
            os.unlink(zip_path)


@router.post("/{project_id}/scan", response_model=ScanResponse)
async def create_scan(project_id: int, scan_create: ScanCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.status != ProjectStatus.DELETED).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    scan = Scan(project_id=project_id, scan_type=scan_create.scan_type, status=ScanStatus.PENDING)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    logger.info("Scan created", scan_id=scan.id, project_id=project_id)
    return scan


@router.get("/{project_id}/scans", response_model=List[ScanResponse])
async def list_scans(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.status != ProjectStatus.DELETED).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    scans = db.query(Scan).filter(Scan.project_id == project_id).order_by(Scan.created_at.desc()).all()
    return scans


@router.get("/{project_id}/scans/latest", response_model=ScanResponse)
async def get_latest_scan(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.status != ProjectStatus.DELETED).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    scan = db.query(Scan).filter(Scan.project_id == project_id).order_by(Scan.created_at.desc()).first()
    if not scan:
        raise HTTPException(status_code=404, detail="No scans found for this project")
    
    return scan