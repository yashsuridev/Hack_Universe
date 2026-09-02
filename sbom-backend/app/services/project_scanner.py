import os
import uuid
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectEcosystem, ProjectStatus, Ecosystem
from app.models.scan import Scan, ScanStatus
from app.models.dependency import Dependency, DependencyType, DependencyStatus, DependencyRelationship
from app.models.vulnerability import Vulnerability
from app.models.risk_finding import RiskFinding
from app.models.sbom import SBOM
from app.services.dependency_analyzer import DependencyAnalyzer
from app.services.vulnerability_scanner import VulnerabilityScanner
from app.services.version_checker import VersionChecker
from app.services.license_analyzer import LicenseAnalyzer
from app.services.supply_chain_analyzer import SupplyChainAnalyzer
from app.services.typosquatting_detector import TyposquattingDetector
from app.services.sbom_generator import SBOMGenerator
from app.services.risk_engine import RiskEngine
from app.utils.file_security import safe_extract_zip, cleanup_temp_dir, validate_zip_file
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ProjectScanner:
    def __init__(self, db: Session):
        self.db = db
        self.temp_base = Path("./temp_scans")
        self.temp_base.mkdir(parents=True, exist_ok=True)
    
    async def scan_project(self, project_id: int, zip_path: str, scan_id: Optional[int] = None) -> Scan:
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        if scan_id:
            scan = self.db.query(Scan).filter(Scan.id == scan_id, Scan.project_id == project_id).first()
            if not scan:
                raise ValueError(f"Scan {scan_id} not found for project {project_id}")
        else:
            scan = Scan(
                project_id=project_id,
                status=ScanStatus.PENDING,
                scan_type="full",
            )
            self.db.add(scan)
            self.db.commit()
            self.db.refresh(scan)
        
        temp_dir = self.temp_base / f"scan_{scan.id}_{uuid.uuid4().hex[:8]}"
        
        try:
            scan.status = ScanStatus.RUNNING
            scan.started_at = datetime.utcnow()
            self.db.commit()
            
            valid, msg = validate_zip_file(zip_path)
            if not valid:
                raise ValueError(f"Invalid ZIP file: {msg}")
            
            success, msg, extracted_files = safe_extract_zip(zip_path, str(temp_dir))
            if not success:
                raise ValueError(f"Failed to extract ZIP: {msg}")
            
            logger.info("Project extracted", scan_id=scan.id, files=len(extracted_files), temp_dir=str(temp_dir))
            
            analyzer = DependencyAnalyzer(str(temp_dir))
            analysis_result = analyzer.analyze()
            
            ecosystems = analysis_result.get('ecosystems', [])
            manifests = analysis_result.get('manifests', [])
            dependencies_data = analysis_result.get('dependencies', [])
            
            for eco_info in manifests:
                eco = Ecosystem(eco_info['ecosystem'])
                proj_eco = ProjectEcosystem(
                    project_id=project.id,
                    ecosystem=eco,
                    manifest_path=eco_info['manifest_path'],
                    lockfile_path=eco_info['lockfile_path'],
                )
                self.db.add(proj_eco)
            
            dependencies = self._save_dependencies(scan.id, dependencies_data, analyzer)
            
            self.db.commit()
            
            vulnerability_scanner = VulnerabilityScanner(self.db)
            vulnerabilities = await vulnerability_scanner.scan_dependencies(dependencies)
            
            for vuln in vulnerabilities:
                self.db.add(vuln)
            
            self.db.commit()
            
            version_checker = VersionChecker()
            await self._update_latest_versions(dependencies, version_checker)
            await version_checker.close()
            
            license_analyzer = LicenseAnalyzer(self.db)
            for dep in dependencies:
                if dep.license:
                    license_analyzer.save_license_info(dep.id, dep.license)
            
            self._build_dependency_relationships(scan.id, dependencies, analyzer)
            
            supply_chain_analyzer = SupplyChainAnalyzer(self.db)
            risk_findings = supply_chain_analyzer.analyze(dependencies, vulnerabilities)
            
            for finding in risk_findings:
                self.db.add(finding)
            
            self.db.commit()
            
            # Generate SBOM - handle gracefully
            sbom_json = None
            try:
                sbom_generator = SBOMGenerator()
                sbom_json = sbom_generator.generate(scan.id, dependencies, vulnerabilities, project.name)
            except Exception as e:
                logger.error("SBOM generation failed", scan_id=scan.id, error=str(e))
                sbom_json = None
            
            # Create SBOM record
            if sbom_json:
                sbom_record = SBOM(
                    scan_id=scan.id,
                    metadata=sbom_json.get('metadata'),
                    components=sbom_json.get('components'),
                    services=sbom_json.get('services'),
                    dependencies=sbom_json.get('dependencies'),
                    compositions=sbom_json.get('compositions'),
                    vulnerabilities=sbom_json.get('vulnerabilities'),
                )
                self.db.add(sbom_record)
            
            risk_engine = RiskEngine(self.db)
            risk_result = risk_engine.calculate_risk_score(scan, risk_findings, dependencies, vulnerabilities)
            risk_engine.update_scan_risk(scan, risk_result)
            
            scan.total_dependencies = len(dependencies)
            scan.direct_dependencies = sum(1 for d in dependencies if d.dependency_type == DependencyType.DIRECT)
            scan.transitive_dependencies = sum(1 for d in dependencies if d.dependency_type == DependencyType.TRANSITIVE)
            scan.dev_dependencies = sum(1 for d in dependencies if d.dependency_type == DependencyType.DEVELOPMENT)
            
            scan.critical_count = sum(1 for v in vulnerabilities if v.severity.value == 'critical')
            scan.high_count = sum(1 for v in vulnerabilities if v.severity.value == 'high')
            scan.medium_count = sum(1 for v in vulnerabilities if v.severity.value == 'medium')
            scan.low_count = sum(1 for v in vulnerabilities if v.severity.value == 'low')
            
            scan.status = ScanStatus.COMPLETED
            scan.completed_at = datetime.utcnow()
            
            # Assign SBOM JSON to scan - handle both dict and string formats
            if sbom_json and isinstance(sbom_json, dict):
                scan.sbom_json = sbom_json
            elif sbom_json:
                scan.sbom_json = sbom_json
            
            self.db.commit()
            self.db.refresh(scan)
            
            logger.info("Scan completed", scan_id=scan.id, risk_score=scan.risk_score, risk_level=scan.risk_level)
            
            return scan
        
        except Exception as e:
            logger.error("Scan failed", scan_id=scan.id, error=str(e))
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            scan.completed_at = datetime.utcnow()
            self.db.commit()
            raise
        
        finally:
            cleanup_temp_dir(str(temp_dir))
    
    def _save_dependencies(self, scan_id: int, dependencies_data: List[Dict], analyzer: DependencyAnalyzer) -> List[Dependency]:
        dependencies = []
        
        for dep_data in dependencies_data:
            dep = Dependency(
                scan_id=scan_id,
                name=dep_data['name'],
                ecosystem=dep_data['ecosystem'],
                declared_version=dep_data.get('declared_version'),
                resolved_version=dep_data.get('resolved_version'),
                dependency_type=DependencyType(dep_data.get('dependency_type', 'direct')),
                purl=dep_data.get('purl'),
                license=dep_data.get('license'),
                package_metadata=dep_data.get('package_metadata'),
                status=DependencyStatus.UNKNOWN,
            )
            
            if dep.ecosystem == 'npm' and dep.resolved_version:
                pass
            
            self.db.add(dep)
            dependencies.append(dep)
        
        self.db.flush()
        
        if 'npm' in [d.ecosystem for d in dependencies]:
            self._enrich_npm_dependencies(dependencies, analyzer)
        
        return dependencies
    
    def _enrich_npm_dependencies(self, dependencies: List[Dependency], analyzer: DependencyAnalyzer):
        from app.services.npm_parser import NPMParser
        
        npm_deps = [d for d in dependencies if d.ecosystem == 'npm']
        if not npm_deps:
            return
        
        primary_manifest = analyzer.detector.get_primary_manifest(Ecosystem.NPM)
        lockfile = analyzer.detector.get_lockfile(Ecosystem.NPM)
        
        if primary_manifest:
            parser = NPMParser(analyzer.project_root)
            parser.parse(str(primary_manifest), str(lockfile) if lockfile else None)
            
            for dep in npm_deps:
                scripts = parser.get_lifecycle_scripts(dep.name)
                if scripts:
                    dep.has_lifecycle_scripts = True
                    dep.lifecycle_scripts = scripts
                    
                    from app.services.lifecycle_script_analyzer import LifecycleScriptAnalyzer
                    lifecycle_analyzer = LifecycleScriptAnalyzer()
                    analysis = lifecycle_analyzer.analyze(scripts)
                    dep.package_metadata = dep.package_metadata or {}
                    dep.package_metadata['lifecycle_analysis'] = analysis
                
                from app.services.typosquatting_detector import TyposquattingDetector
                typosquatting_detector = TyposquattingDetector()
                typo_result = typosquatting_detector.check(dep.name, 'npm')
                if typo_result:
                    dep.typosquatting_flag = True
                    dep.typosquatting_details = typo_result
    
    async def _update_latest_versions(self, dependencies: List[Dependency], version_checker: VersionChecker):
        dep_groups = {}
        for dep in dependencies:
            key = f"{dep.ecosystem}:{dep.name}"
            if key not in dep_groups:
                dep_groups[key] = []
            dep_groups[key].append(dep)
        
        for key, deps in dep_groups.items():
            ecosystem, name = key.split(':', 1)
            latest = await version_checker.get_latest_version(ecosystem, name)
            if latest:
                for dep in deps:
                    dep.latest_version = latest
                    
                    if dep.resolved_version and dep.resolved_version != latest:
                        from app.utils.version_utils import compare_versions, get_fixed_version
                        if compare_versions(dep.resolved_version, latest) < 0:
                            if not dep.recommended_version:
                                dep.recommended_version = latest
    
    def _build_dependency_relationships(self, scan_id: int, dependencies: List[Dependency], analyzer: DependencyAnalyzer):
        if not dependencies:
            return
        
        npm_deps = [d for d in dependencies if d.ecosystem == 'npm']
        if npm_deps:
            primary_manifest = analyzer.detector.get_primary_manifest(Ecosystem.NPM)
            lockfile = analyzer.detector.get_lockfile(Ecosystem.NPM)
            
            if primary_manifest:
                from app.services.npm_parser import NPMParser
                parser = NPMParser(analyzer.project_root)
                parser.parse(str(primary_manifest), str(lockfile) if lockfile else None)
                tree = parser.build_dependency_tree()
                
                dep_map = {d.name: d for d in npm_deps}
                
                for parent_name, children_names in tree.items():
                    parent = dep_map.get(parent_name)
                    if not parent:
                        continue
                    
                    for child_name in children_names:
                        child = dep_map.get(child_name)
                        if not child:
                            continue
                        
                        rel = DependencyRelationship(
                            scan_id=scan_id,
                            dependency_id=child.id,
                            parent_dependency_id=parent.id,
                            relationship_type="depends_on",
                        )
                        self.db.add(rel)
                        
                        if not child.dependency_path:
                            child.dependency_path = []
                        child.dependency_path.append(parent_name)
        
        for dep in dependencies:
            if dep.dependency_type == DependencyType.TRANSITIVE and not dep.dependency_path:
                dep.dependency_path = ["transitive"]


async def scan_project(db: Session, project_id: int, zip_path: str, scan_id: Optional[int] = None) -> Scan:
    scanner = ProjectScanner(db)
    return await scanner.scan_project(project_id, zip_path, scan_id)