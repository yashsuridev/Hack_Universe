from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    scans = relationship("Scan", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_projects_status_created", "status", "created_at"),
    )


class Ecosystem(str, enum.Enum):
    NPM = "npm"
    PYPI = "pypi"
    MAVEN = "maven"
    UNKNOWN = "unknown"


class ProjectEcosystem(Base):
    __tablename__ = "project_ecosystems"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    ecosystem = Column(SQLEnum(Ecosystem), nullable=False)
    manifest_path = Column(String(500), nullable=False)
    lockfile_path = Column(String(500), nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    project = relationship("Project", backref="ecosystems")
    
    __table_args__ = (
        Index("ix_project_ecosystems_project_eco", "project_id", "ecosystem", unique=True),
    )