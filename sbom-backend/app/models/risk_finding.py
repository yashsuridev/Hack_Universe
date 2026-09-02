from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON, Index, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class RiskFindingType(str, enum.Enum):
    VULNERABILITY = "vulnerability"
    OUTDATED_DEPENDENCY = "outdated_dependency"
    LIFECYCLE_SCRIPT = "lifecycle_script"
    TYPOSQUATTING = "typosquatting"
    UNKNOWN_LICENSE = "unknown_license"
    UNPINNED_DEPENDENCY = "unpinned_dependency"
    TRANSITIVE_VULNERABILITY = "transitive_vulnerability"
    DEPENDENCY_CONFUSION = "dependency_confusion"
    MALICIOUS_PACKAGE = "malicious_package"
    SUPPLY_CHAIN_COMPROMISE = "supply_chain_compromise"
    UNMAINTAINED_PACKAGE = "unmaintained_package"
    VERSION_ANOMALY = "version_anomaly"


class RiskSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskFinding(Base):
    __tablename__ = "risk_findings"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    dependency_id = Column(Integer, ForeignKey("dependencies.id", ondelete="SET NULL"), nullable=True, index=True)
    
    finding_type = Column(SQLEnum(RiskFindingType), nullable=False)
    severity = Column(SQLEnum(RiskSeverity), default=RiskSeverity.INFO, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    
    evidence = Column(JSON, nullable=True)
    affected_versions = Column(String(200), nullable=True)
    fixed_version = Column(String(100), nullable=True)
    
    cve_ids = Column(JSON, nullable=True)
    osv_ids = Column(JSON, nullable=True)
    
    score_contribution = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    scan = relationship("Scan", back_populates="risk_findings")
    dependency = relationship("Dependency", backref="risk_findings")
    
    __table_args__ = (
        Index("ix_risk_findings_scan_type", "scan_id", "finding_type"),
        Index("ix_risk_findings_scan_severity", "scan_id", "severity"),
    )