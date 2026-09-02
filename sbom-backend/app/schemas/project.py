from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.project import ProjectStatus, Ecosystem


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectEcosystemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ecosystem: Ecosystem
    manifest_path: str
    lockfile_path: Optional[str]
    detected_at: datetime


class ProjectDetailResponse(ProjectResponse):
    ecosystems: List[ProjectEcosystemResponse] = []
    scan_count: int = 0
    latest_scan: Optional["ScanSummaryResponse"] = None


class ScanSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    risk_score: float
    risk_level: str
    total_dependencies: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    created_at: datetime


ProjectDetailResponse.model_rebuild()