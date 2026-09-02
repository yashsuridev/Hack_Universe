from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.scan import ScanStatus


class ScanBase(BaseModel):
    scan_type: str = Field(default="full", pattern="^(full|quick|incremental)$")


class ScanCreate(ScanBase):
    pass


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    status: ScanStatus
    scan_type: str
    
    total_dependencies: int
    direct_dependencies: int
    transitive_dependencies: int
    dev_dependencies: int
    
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    
    risk_score: float
    risk_level: str
    
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class ScanDetailResponse(ScanResponse):
    scan_metadata: Optional[Dict[str, Any]] = None
    dependencies: List["DependencySummaryResponse"] = []
    vulnerabilities: List["VulnerabilitySummaryResponse"] = []
    risk_findings: List["RiskFindingSummaryResponse"] = []


class ScanComparisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    scan_1: ScanResponse
    scan_2: ScanResponse
    
    new_dependencies: List["DependencySummaryResponse"] = []
    removed_dependencies: List["DependencySummaryResponse"] = []
    new_vulnerabilities: List["VulnerabilitySummaryResponse"] = []
    resolved_vulnerabilities: List["VulnerabilitySummaryResponse"] = []
    version_changes: List[Dict[str, Any]] = []
    risk_score_change: float = 0.0


class DependencySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    ecosystem: str
    declared_version: Optional[str]
    resolved_version: Optional[str]
    latest_version: Optional[str]
    recommended_version: Optional[str]
    dependency_type: str
    purl: Optional[str]
    license: Optional[str]
    status: str
    risk_score: float
    has_lifecycle_scripts: bool
    typosquatting_flag: bool


class VulnerabilitySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    dependency_id: int
    dependency_name: str
    osv_id: str
    cve_id: Optional[str]
    ghsa_id: Optional[str]
    severity: str
    cvss_score: Optional[float]
    affected_versions: Optional[str]
    fixed_version: Optional[str]
    published_at: Optional[datetime]


class RiskFindingSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    finding_type: str
    severity: str
    title: str
    description: str
    recommendation: Optional[str]
    score_contribution: float


ScanDetailResponse.model_rebuild()
ScanComparisonResponse.model_rebuild()