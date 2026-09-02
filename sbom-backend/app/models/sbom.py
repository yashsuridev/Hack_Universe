from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class SBOM(Base):
    __tablename__ = "sboms"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)

    bom_format = Column(String(50), default="CycloneDX", nullable=False)
    spec_version = Column(String(20), default="1.6", nullable=False)
    serial_number = Column(String(100), nullable=True)
    version = Column(Integer, default=1, nullable=False)

    sbom_data = Column(JSON, nullable=True)
    components = Column(JSON, nullable=True)
    services = Column(JSON, nullable=True)
    dependencies = Column(JSON, nullable=True)
    compositions = Column(JSON, nullable=True)
    vulnerabilities = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    scan = relationship("Scan", backref="sbom_record")

    __table_args__ = (
        Index("ix_sboms_scan_id", "scan_id"),
    )