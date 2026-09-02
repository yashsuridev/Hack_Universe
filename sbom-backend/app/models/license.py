from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class LicenseType(str, enum.Enum):
    SPDX = "spdx"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class LicenseRiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class LicenseInfo(Base):
    __tablename__ = "license_info"
    
    id = Column(Integer, primary_key=True, index=True)
    dependency_id = Column(Integer, ForeignKey("dependencies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    license_type = Column(SQLEnum(LicenseType), default=LicenseType.SPDX, nullable=False)
    spdx_id = Column(String(100), nullable=True, index=True)
    name = Column(String(200), nullable=True)
    url = Column(String(500), nullable=True)
    text = Column(Text, nullable=True)
    
    risk_level = Column(SQLEnum(LicenseRiskLevel), default=LicenseRiskLevel.UNKNOWN, nullable=False)
    is_osi_approved = Column(Boolean, default=False)
    is_fsf_libre = Column(Boolean, default=False)
    
    license_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    dependency = relationship("Dependency", back_populates="license_info")
    
    __table_args__ = (
        Index("ix_license_info_dep_spdx", "dependency_id", "spdx_id"),
    )


class KnownLicense(Base):
    __tablename__ = "known_licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    spdx_id = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=True)
    is_osi_approved = Column(Boolean, default=False)
    is_fsf_libre = Column(Boolean, default=False)
    risk_level = Column(SQLEnum(LicenseRiskLevel), default=LicenseRiskLevel.LOW, nullable=False)
    category = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)