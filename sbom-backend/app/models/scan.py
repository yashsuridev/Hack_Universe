from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Float, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(ScanStatus), default=ScanStatus.PENDING, nullable=False)
    scan_type = Column(String(50), default="full", nullable=False)
    
    total_dependencies = Column(Integer, default=0)
    direct_dependencies = Column(Integer, default=0)
    transitive_dependencies = Column(Integer, default=0)
    dev_dependencies = Column(Integer, default=0)
    
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW")
    
    sbom_json = Column(JSON, nullable=True)
    scan_metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    project = relationship("Project", back_populates="scans")
    dependencies = relationship("Dependency", back_populates="scan", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    risk_findings = relationship("RiskFinding", back_populates="scan", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_scans_project_status", "project_id", "status"),
        Index("ix_scans_created_at", "created_at"),
    )