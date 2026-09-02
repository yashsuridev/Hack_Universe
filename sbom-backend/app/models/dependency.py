from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean, JSON, Index, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class DependencyType(str, enum.Enum):
    DIRECT = "direct"
    TRANSITIVE = "transitive"
    DEVELOPMENT = "development"
    OPTIONAL = "optional"
    PEER = "peer"


class DependencyStatus(str, enum.Enum):
    SAFE = "safe"
    VULNERABLE = "vulnerable"
    REVIEW = "review"
    UNKNOWN = "unknown"


class Dependency(Base):
    __tablename__ = "dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False, index=True)
    ecosystem = Column(String(50), nullable=False, index=True)
    
    declared_version = Column(String(100), nullable=True)
    resolved_version = Column(String(100), nullable=True, index=True)
    latest_version = Column(String(100), nullable=True)
    recommended_version = Column(String(100), nullable=True)
    
    dependency_type = Column(SQLEnum(DependencyType), default=DependencyType.DIRECT, nullable=False)
    purl = Column(String(500), nullable=True, index=True)
    
    license = Column(String(100), nullable=True)
    license_url = Column(String(500), nullable=True)
    
    status = Column(SQLEnum(DependencyStatus), default=DependencyStatus.UNKNOWN, nullable=False)
    risk_score = Column(Float, default=0.0)
    
    has_lifecycle_scripts = Column(Boolean, default=False)
    lifecycle_scripts = Column(JSON, nullable=True)
    typosquatting_flag = Column(Boolean, default=False)
    typosquatting_details = Column(JSON, nullable=True)
    
    package_metadata = Column(JSON, nullable=True)
    dependency_path = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    scan = relationship("Scan", back_populates="dependencies")
    vulnerabilities = relationship("Vulnerability", back_populates="dependency", cascade="all, delete-orphan")
    license_info = relationship("LicenseInfo", back_populates="dependency", cascade="all, delete-orphan")
    relationships = relationship(
        "DependencyRelationship",
        foreign_keys="DependencyRelationship.dependency_id",
        back_populates="dependency",
        cascade="all, delete-orphan"
    )
    reverse_relationships = relationship(
        "DependencyRelationship",
        foreign_keys="DependencyRelationship.parent_dependency_id",
        back_populates="parent_dependency",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_dependencies_scan_ecosystem", "scan_id", "ecosystem"),
        Index("ix_dependencies_scan_type", "scan_id", "dependency_type"),
        Index("ix_dependencies_scan_status", "scan_id", "status"),
        Index("ix_dependencies_name_version", "name", "resolved_version"),
    )


class DependencyRelationship(Base):
    __tablename__ = "dependency_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    dependency_id = Column(Integer, ForeignKey("dependencies.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_dependency_id = Column(Integer, ForeignKey("dependencies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relationship_type = Column(String(50), default="depends_on")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    dependency = relationship("Dependency", foreign_keys=[dependency_id], back_populates="relationships")
    parent_dependency = relationship("Dependency", foreign_keys=[parent_dependency_id], back_populates="reverse_relationships")
    
    __table_args__ = (
        Index("ix_dep_rel_scan_dep", "scan_id", "dependency_id"),
        Index("ix_dep_rel_scan_parent", "scan_id", "parent_dependency_id"),
    )