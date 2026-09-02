from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "SBOM Auditor"
    app_version: str = "1.0.0"
    debug: bool = True
    
    database_url: str = "sqlite:///./sbom_auditor_v2.db"
    
    upload_max_size: int = 50 * 1024 * 1024
    upload_dir: str = "./uploads"
    temp_dir: str = "./temp_scans"
    
    osv_api_base_url: str = "https://api.osv.dev/v1"
    osv_batch_size: int = 100
    osv_timeout: int = 30
    
    npm_registry_url: str = "https://registry.npmjs.org"
    pypi_api_url: str = "https://pypi.org/pypi"
    maven_central_url: str = "https://search.maven.org/solrsearch/select"
    
    cache_ttl_hours: int = 24
    risk_score_weights: dict = {
        "critical_vuln": 25,
        "high_vuln": 15,
        "medium_vuln": 8,
        "low_vuln": 3,
        "outdated_dep": 2,
        "lifecycle_script": 5,
        "typosquatting": 10,
        "unknown_license": 3,
        "unpinned_dep": 4,
        "transitive_vuln": 5,
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()