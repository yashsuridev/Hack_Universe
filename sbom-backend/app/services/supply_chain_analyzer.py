from typing import Dict, List, Optional, Any, Set
from sqlalchemy.orm import Session
from app.models.dependency import Dependency
from app.models.risk_finding import RiskFinding, RiskFindingType, RiskSeverity
from app.services.typosquatting_detector import TyposquattingDetector
from app.services.lifecycle_script_analyzer import LifecycleScriptAnalyzer
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SupplyChainAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self.typosquatting_detector = TyposquattingDetector()
        self.lifecycle_analyzer = LifecycleScriptAnalyzer()
    
    def analyze(self, dependencies: List[Dependency], vulnerabilities: List[Any]) -> List[RiskFinding]:
        findings = []
        
        findings.extend(self._analyze_vulnerabilities(dependencies, vulnerabilities))
        findings.extend(self._analyze_outdated_dependencies(dependencies))
        findings.extend(self._analyze_lifecycle_scripts(dependencies))
        findings.extend(self._analyze_typosquatting(dependencies))
        findings.extend(self._analyze_licenses(dependencies))
        findings.extend(self._analyze_unpinned_dependencies(dependencies))
        findings.extend(self._analyze_transitive_vulnerabilities(dependencies, vulnerabilities))
        findings.extend(self._analyze_dependency_complexity(dependencies))
        
        return findings
    
    def _analyze_vulnerabilities(self, dependencies: List[Dependency], vulnerabilities: List[Any]) -> List[RiskFinding]:
        findings = []
        vuln_by_dep = {}
        
        for vuln in vulnerabilities:
            dep_id = vuln.dependency_id
            if dep_id not in vuln_by_dep:
                vuln_by_dep[dep_id] = []
            vuln_by_dep[dep_id].append(vuln)
        
        for dep in dependencies:
            dep_vulns = vuln_by_dep.get(dep.id, [])
            if not dep_vulns:
                continue
            
            critical = sum(1 for v in dep_vulns if v.severity.value == 'critical')
            high = sum(1 for v in dep_vulns if v.severity.value == 'high')
            medium = sum(1 for v in dep_vulns if v.severity.value == 'medium')
            low = sum(1 for v in dep_vulns if v.severity.value == 'low')
            
            if critical > 0:
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.VULNERABILITY,
                    severity=RiskSeverity.CRITICAL,
                    title=f"Critical vulnerabilities in {dep.name}",
                    description=f"Found {critical} critical, {high} high, {medium} medium, {low} low vulnerabilities in {dep.name}@{dep.resolved_version}",
                    recommendation=f"Upgrade {dep.name} to a version that addresses these vulnerabilities. Check fixed versions for each vulnerability.",
                    evidence={'vulnerabilities': [v.osv_id for v in dep_vulns]},
                    cve_ids=[v.cve_id for v in dep_vulns if v.cve_id],
                    osv_ids=[v.osv_id for v in dep_vulns],
                    score_contribution=critical * 25 + high * 15 + medium * 8 + low * 3,
                ))
            elif high > 0:
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.VULNERABILITY,
                    severity=RiskSeverity.HIGH,
                    title=f"High severity vulnerabilities in {dep.name}",
                    description=f"Found {high} high, {medium} medium, {low} low vulnerabilities in {dep.name}@{dep.resolved_version}",
                    recommendation=f"Upgrade {dep.name} to address high severity vulnerabilities.",
                    evidence={'vulnerabilities': [v.osv_id for v in dep_vulns]},
                    cve_ids=[v.cve_id for v in dep_vulns if v.cve_id],
                    osv_ids=[v.osv_id for v in dep_vulns],
                    score_contribution=high * 15 + medium * 8 + low * 3,
                ))
            elif medium > 0:
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.VULNERABILITY,
                    severity=RiskSeverity.MEDIUM,
                    title=f"Medium severity vulnerabilities in {dep.name}",
                    description=f"Found {medium} medium, {low} low vulnerabilities in {dep.name}@{dep.resolved_version}",
                    recommendation=f"Consider upgrading {dep.name} to address medium severity vulnerabilities.",
                    evidence={'vulnerabilities': [v.osv_id for v in dep_vulns]},
                    cve_ids=[v.cve_id for v in dep_vulns if v.cve_id],
                    osv_ids=[v.osv_id for v in dep_vulns],
                    score_contribution=medium * 8 + low * 3,
                ))
            elif low > 0:
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.VULNERABILITY,
                    severity=RiskSeverity.LOW,
                    title=f"Low severity vulnerabilities in {dep.name}",
                    description=f"Found {low} low vulnerabilities in {dep.name}@{dep.resolved_version}",
                    recommendation=f"Monitor {dep.name} for future updates addressing these vulnerabilities.",
                    evidence={'vulnerabilities': [v.osv_id for v in dep_vulns]},
                    cve_ids=[v.cve_id for v in dep_vulns if v.cve_id],
                    osv_ids=[v.osv_id for v in dep_vulns],
                    score_contribution=low * 3,
                ))
        
        return findings
    
    def _analyze_outdated_dependencies(self, dependencies: List[Dependency]) -> List[RiskFinding]:
        findings = []
        
        for dep in dependencies:
            if not dep.resolved_version or not dep.latest_version:
                continue
            
            if dep.resolved_version == dep.latest_version:
                continue
            
            from app.utils.version_utils import compare_versions
            if compare_versions(dep.resolved_version, dep.latest_version) < 0:
                severity = RiskSeverity.LOW
                if dep.dependency_type.value == 'direct':
                    severity = RiskSeverity.MEDIUM
                
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.OUTDATED_DEPENDENCY,
                    severity=severity,
                    title=f"Outdated dependency: {dep.name}",
                    description=f"{dep.name} is at version {dep.resolved_version}, but {dep.latest_version} is available",
                    recommendation=f"Consider upgrading {dep.name} to {dep.latest_version} after testing for compatibility.",
                    evidence={'current_version': dep.resolved_version, 'latest_version': dep.latest_version},
                    score_contribution=2 if severity == RiskSeverity.LOW else 4,
                ))
        
        return findings
    
    def _analyze_lifecycle_scripts(self, dependencies: List[Dependency]) -> List[RiskFinding]:
        findings = []
        
        for dep in dependencies:
            if not dep.has_lifecycle_scripts or not dep.lifecycle_scripts:
                continue
            
            scripts = dep.lifecycle_scripts
            script_names = list(scripts.keys())
            
            findings.append(RiskFinding(
                scan_id=dep.scan_id,
                dependency_id=dep.id,
                finding_type=RiskFindingType.LIFECYCLE_SCRIPT,
                severity=RiskSeverity.MEDIUM,
                title=f"Lifecycle scripts detected in {dep.name}",
                description=f"Package {dep.name}@{dep.resolved_version} contains lifecycle scripts: {', '.join(script_names)}. These scripts execute during installation and could perform arbitrary actions.",
                recommendation=f"Review the lifecycle scripts in {dep.name} to ensure they don't perform malicious actions. Consider using --ignore-scripts flag during installation if scripts are not needed.",
                evidence={'scripts': scripts},
                score_contribution=5,
            ))
        
        return findings
    
    def _analyze_typosquatting(self, dependencies: List[Dependency]) -> List[RiskFinding]:
        findings = []
        
        for dep in dependencies:
            if dep.typosquatting_flag and dep.typosquatting_details:
                details = dep.typosquatting_details
                similar_to = details.get('similar_to', 'unknown')
                similarity = details.get('similarity', 0)
                
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.TYPOSQUATTING,
                    severity=RiskSeverity.HIGH,
                    title=f"Potential typosquatting: {dep.name}",
                    description=f"Package name '{dep.name}' is suspiciously similar to popular package '{similar_to}' (similarity: {similarity:.2f}). This could indicate a typosquatting attempt.",
                    recommendation=f"Verify that {dep.name} is the intended package. Check the package maintainer, repository, and download statistics before using.",
                    evidence=details,
                    score_contribution=10,
                ))
        
        return findings
    
    def _analyze_licenses(self, dependencies: List[Dependency]) -> List[RiskFinding]:
        findings = []
        
        for dep in dependencies:
            if not dep.license:
                continue
            
            from app.services.license_analyzer import normalize_license
            normalized = normalize_license(dep.license)
            
            from app.services.license_analyzer import SPDX_LICENSES
            if normalized not in SPDX_LICENSES:
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.UNKNOWN_LICENSE,
                    severity=RiskSeverity.LOW,
                    title=f"Unknown or non-standard license: {dep.name}",
                    description=f"Package {dep.name} uses license '{dep.license}' which is not a recognized SPDX license. This may require legal review.",
                    recommendation="Verify the license terms with legal counsel. Consider replacing with a package that uses a standard license.",
                    evidence={'license': dep.license},
                    score_contribution=3,
                ))
        
        return findings
    
    def _analyze_unpinned_dependencies(self, dependencies: List[Dependency]) -> List[RiskFinding]:
        findings = []
        
        for dep in dependencies:
            if not dep.declared_version or dep.declared_version in ('*', 'latest', ''):
                findings.append(RiskFinding(
                    scan_id=dep.scan_id,
                    dependency_id=dep.id,
                    finding_type=RiskFindingType.UNPINNED_DEPENDENCY,
                    severity=RiskSeverity.MEDIUM,
                    title=f"Unpinned dependency: {dep.name}",
                    description=f"Dependency {dep.name} has no version constraint (declared: {dep.declared_version}). This can lead to unpredictable builds and automatic inclusion of breaking changes.",
                    recommendation=f"Pin {dep.name} to a specific version or version range in your manifest file.",
                    evidence={'declared_version': dep.declared_version, 'resolved_version': dep.resolved_version},
                    score_contribution=4,
                ))
        
        return findings
    
    def _analyze_transitive_vulnerabilities(self, dependencies: List[Dependency], vulnerabilities: List[Any]) -> List[RiskFinding]:
        findings = []
        
        vuln_by_dep = {}
        for vuln in vulnerabilities:
            dep_id = vuln.dependency_id
            if dep_id not in vuln_by_dep:
                vuln_by_dep[dep_id] = []
            vuln_by_dep[dep_id].append(vuln)
        
        for dep in dependencies:
            if dep.dependency_type.value != 'transitive':
                continue
            
            dep_vulns = vuln_by_dep.get(dep.id, [])
            if not dep_vulns:
                continue
            
            findings.append(RiskFinding(
                scan_id=dep.scan_id,
                dependency_id=dep.id,
                finding_type=RiskFindingType.TRANSITIVE_VULNERABILITY,
                severity=RiskSeverity.HIGH,
                title=f"Vulnerable transitive dependency: {dep.name}",
                description=f"Transitive dependency {dep.name}@{dep.resolved_version} has {len(dep_vulns)} known vulnerabilities. This dependency was pulled in by other packages in your dependency tree.",
                recommendation=f"Identify which direct dependency brings in {dep.name} and consider updating that direct dependency, or adding an override/resolution to use a fixed version of {dep.name}.",
                evidence={'vulnerabilities': [v.osv_id for v in dep_vulns], 'dependency_path': dep.dependency_path},
                osv_ids=[v.osv_id for v in dep_vulns],
                score_contribution=5,
            ))
        
        return findings
    
    def _analyze_dependency_complexity(self, dependencies: List[Dependency]) -> List[RiskFinding]:
        findings = []
        
        total_deps = len(dependencies)
        direct_deps = sum(1 for d in dependencies if d.dependency_type.value == 'direct')
        transitive_deps = sum(1 for d in dependencies if d.dependency_type.value == 'transitive')
        
        if total_deps > 500:
            findings.append(RiskFinding(
                scan_id=dependencies[0].scan_id if dependencies else 0,
                dependency_id=None,
                finding_type=RiskFindingType.DEPENDENCY_CONFUSION,
                severity=RiskSeverity.MEDIUM,
                title="Large dependency tree",
                description=f"Project has {total_deps} total dependencies ({direct_deps} direct, {transitive_deps} transitive). Large dependency trees increase attack surface and maintenance burden.",
                recommendation="Audit direct dependencies for necessity. Consider replacing heavy dependencies with lighter alternatives or native implementations.",
                evidence={'total': total_deps, 'direct': direct_deps, 'transitive': transitive_deps},
                score_contribution=5,
            ))
        elif total_deps > 200:
            findings.append(RiskFinding(
                scan_id=dependencies[0].scan_id if dependencies else 0,
                dependency_id=None,
                finding_type=RiskFindingType.DEPENDENCY_CONFUSION,
                severity=RiskSeverity.LOW,
                title="Moderate dependency tree size",
                description=f"Project has {total_deps} total dependencies ({direct_deps} direct, {transitive_deps} transitive).",
                recommendation="Review direct dependencies for potential consolidation.",
                evidence={'total': total_deps, 'direct': direct_deps, 'transitive': transitive_deps},
                score_contribution=2,
            ))
        
        return findings