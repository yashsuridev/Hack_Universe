from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.dependency import DependencyType, DependencyStatus


class DependencyBase(BaseModel):
    name: str
    ecosystem: str
    declared_version: Optional[str] = None
    resolved_version: Optional[str] = None
    latest_version: Optional[str] = None
    recommended_version: Optional[str] = None
    dependency_type: DependencyType
    purl: Optional[str] = None
    license: Optional[str] = None
    license_url: Optional[str] = None
    status: DependencyStatus = DependencyStatus.UNKNOWN
    risk_score: float = 0.0
    has_lifecycle_scripts: bool = False
    lifecycle_scripts: Optional[Dict[str, Any]] = None
    typosquatting_flag: bool = False
    typosquatting_details: Optional[Dict[str, Any]] = None
    package_metadata: Optional[Dict[str, Any]] = None
    dependency_path: Optional[List[Dict[str, Any]]] = None


class DependencyCreate(DependencyBase):
    scan_id: int


class DependencyResponse(DependencyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    scan_id: int
    created_at: datetime
    updated_at: datetime
    vulnerabilities: List["VulnerabilityDetailResponse"] = []
    license_info: Optional["LicenseInfoResponse"] = None
    relationships: List["DependencyRelationshipResponse"] = []


class DependencyDetailResponse(DependencyResponse):
    pass


class DependencyStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    package: str
    type: str
    declared: Optional[str]
    installed: Optional[str]
    latest: Optional[str]
    security: str
    severity: Optional[str]
    fixed_version: Optional[str]
    risk: float
    purl: Optional[str]
    license: Optional[str]
    has_lifecycle_scripts: bool
    typosquatting_flag: bool
    dependency_path: Optional[List[str]]


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


class DependencyTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    version: str
    ecosystem: str
    dependency_type: str
    status: str
    risk_score: float
    vulnerabilities_count: int
    children: List["DependencyTreeNode"] = []
    parent_id: Optional[int] = None


class DependencyRelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    dependency_id: int
    parent_dependency_id: int
    relationship_type: str


class LicenseInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    spdx_id: Optional[str]
    name: Optional[str]
    url: Optional[str]
    risk_level: str
    is_osi_approved: bool
    is_fsf_libre: bool


class VulnerabilityDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    osv_id: str
    cve_id: Optional[str]
    ghsa_id: Optional[str]
    severity: str
    cvss_score: Optional[float]
    cvss_vector: Optional[str]
    summary: Optional[str]
    affected_versions: Optional[str]
    fixed_version: Optional[str]
    references: Optional[List[Dict[str, Any]]]
    published_at: Optional[datetime]
    modified_at: Optional[datetime]


DependencyTreeNode.model_rebuild()
DependencyResponse.model_rebuild()