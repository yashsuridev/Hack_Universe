from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class SBOMComponent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    type: str
    name: str
    version: str
    purl: Optional[str] = None
    description: Optional[str] = None
    licenses: Optional[List[Dict[str, Any]]] = None
    hashes: Optional[List[Dict[str, str]]] = None
    external_references: Optional[List[Dict[str, Any]]] = None
    properties: Optional[Dict[str, Any]] = None


class SBOMDependency(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    ref: str
    depends_on: List[str] = []


class SBOMVulnerability(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    source: Optional[Dict[str, Any]] = None
    ratings: Optional[List[Dict[str, Any]]] = None
    cwes: Optional[List[int]] = None
    description: Optional[str] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    advisories: Optional[List[Dict[str, Any]]] = None
    affects: Optional[List[Dict[str, Any]]] = None
    properties: Optional[Dict[str, Any]] = None


class SBOMMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    timestamp: str
    tools: Optional[List[Dict[str, Any]]] = None
    authors: Optional[List[Dict[str, Any]]] = None
    component: Optional[SBOMComponent] = None
    manufacture: Optional[Dict[str, Any]] = None
    supplier: Optional[Dict[str, Any]] = None
    licenses: Optional[List[Dict[str, Any]]] = None
    properties: Optional[Dict[str, Any]] = None


class SBOMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    bomFormat: str = "CycloneDX"
    specVersion: str = "1.6"
    serialNumber: Optional[str] = None
    version: int = 1
    metadata: Optional[SBOMMetadata] = None
    components: List[SBOMComponent] = []
    services: List[Any] = []
    dependencies: List[SBOMDependency] = []
    compositions: List[Any] = []
    vulnerabilities: List[SBOMVulnerability] = []


class SBOMExplorerFilters(BaseModel):
    ecosystem: Optional[str] = None
    dependency_type: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    has_vulnerabilities: Optional[bool] = None
    license: Optional[str] = None


class SBOMExplorerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    components: List[Dict[str, Any]] = []
    total: int
    page: int
    page_size: int
    filters: SBOMExplorerFilters