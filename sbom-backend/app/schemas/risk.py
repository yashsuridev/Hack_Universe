from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.risk_finding import RiskFindingType, RiskSeverity
from app.models.license import LicenseRiskLevel


class RiskFindingBase(BaseModel):
    finding_type: RiskFindingType
    severity: RiskSeverity
    title: str
    description: str
    recommendation: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    affected_versions: Optional[str] = None
    fixed_version: Optional[str] = None
    cve_ids: Optional[List[str]] = None
    osv_ids: Optional[List[str]] = None
    score_contribution: float = 0.0


class RiskFindingCreate(RiskFindingBase):
    scan_id: int
    dependency_id: Optional[int] = None


class RiskFindingResponse(RiskFindingBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    scan_id: int
    dependency_id: Optional[int]
    created_at: datetime
    dependency_name: Optional[str] = None


class RiskScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    score: float
    level: str
    max_score: float = 100.0
    breakdown: Dict[str, float] = {}
    findings: List[RiskFindingResponse] = []
    summary: str = ""


class RiskTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    scan_id: int
    date: datetime
    risk_score: float
    risk_level: str
    total_dependencies: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class SupplyChainRiskIndicator(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    indicator_type: str
    severity: RiskSeverity
    title: str
    description: str
    affected_packages: List[str] = []
    evidence: Dict[str, Any] = {}
    recommendation: str = ""


class LicenseFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    dependency_name: str
    dependency_version: str
    spdx_id: Optional[str]
    license_name: Optional[str]
    risk_level: LicenseRiskLevel
    is_unknown: bool
    recommendation: str = ""


class RiskFindingSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    finding_type: str
    severity: str
    title: str
    description: str
    recommendation: Optional[str] = None
    score_contribution: float = 0.0