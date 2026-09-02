from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.scan import Scan
from app.models.risk_finding import RiskFinding, RiskSeverity
from app.models.dependency import Dependency
from app.models.vulnerability import Vulnerability
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RiskEngine:
    def __init__(self, db: Session):
        self.db = db
        self.weights = settings.risk_score_weights
    
    def calculate_risk_score(self, scan: Scan, findings: List[RiskFinding], dependencies: List[Dependency], vulnerabilities: List[Vulnerability]) -> Dict[str, Any]:
        breakdown = {}
        total_score = 0.0
        reasons = []
        
        vuln_score, vuln_reasons = self._calculate_vulnerability_score(vulnerabilities)
        breakdown['vulnerabilities'] = vuln_score
        total_score += vuln_score
        reasons.extend(vuln_reasons)
        
        outdated_score, outdated_reasons = self._calculate_outdated_score(dependencies)
        breakdown['outdated_dependencies'] = outdated_score
        total_score += outdated_score
        reasons.extend(outdated_reasons)
        
        lifecycle_score, lifecycle_reasons = self._calculate_lifecycle_score(findings)
        breakdown['lifecycle_scripts'] = lifecycle_score
        total_score += lifecycle_score
        reasons.extend(lifecycle_reasons)
        
        typosquatting_score, typo_reasons = self._calculate_typosquatting_score(findings)
        breakdown['typosquatting'] = typosquatting_score
        total_score += typosquatting_score
        reasons.extend(typo_reasons)
        
        license_score, license_reasons = self._calculate_license_score(dependencies)
        breakdown['unknown_licenses'] = license_score
        total_score += license_score
        reasons.extend(license_reasons)
        
        unpinned_score, unpinned_reasons = self._calculate_unpinned_score(dependencies)
        breakdown['unpinned_dependencies'] = unpinned_score
        total_score += unpinned_score
        reasons.extend(unpinned_reasons)
        
        transitive_score, transitive_reasons = self._calculate_transitive_vuln_score(findings)
        breakdown['transitive_vulnerabilities'] = transitive_score
        total_score += transitive_score
        reasons.extend(transitive_reasons)
        
        complexity_score, complexity_reasons = self._calculate_complexity_score(dependencies)
        breakdown['dependency_complexity'] = complexity_score
        total_score += complexity_score
        reasons.extend(complexity_reasons)
        
        total_score = min(total_score, 100.0)
        
        if total_score >= 71:
            risk_level = "CRITICAL"
        elif total_score >= 41:
            risk_level = "HIGH"
        elif total_score >= 21:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'score': round(total_score, 1),
            'level': risk_level,
            'max_score': 100.0,
            'breakdown': breakdown,
            'reasons': reasons,
            'summary': self._generate_summary(total_score, risk_level, reasons),
        }
    
    def _calculate_vulnerability_score(self, vulnerabilities: List[Vulnerability]) -> tuple:
        score = 0.0
        reasons = []
        
        critical = sum(1 for v in vulnerabilities if v.severity.value == 'critical')
        high = sum(1 for v in vulnerabilities if v.severity.value == 'high')
        medium = sum(1 for v in vulnerabilities if v.severity.value == 'medium')
        low = sum(1 for v in vulnerabilities if v.severity.value == 'low')
        
        if critical > 0:
            score += critical * self.weights.get('critical_vuln', 25)
            reasons.append(f"{critical} critical vulnerabilities")
        if high > 0:
            score += high * self.weights.get('high_vuln', 15)
            reasons.append(f"{high} high vulnerabilities")
        if medium > 0:
            score += medium * self.weights.get('medium_vuln', 8)
            reasons.append(f"{medium} medium vulnerabilities")
        if low > 0:
            score += low * self.weights.get('low_vuln', 3)
            reasons.append(f"{low} low vulnerabilities")
        
        return score, reasons
    
    def _calculate_outdated_score(self, dependencies: List[Dependency]) -> tuple:
        score = 0.0
        reasons = []
        
        outdated_count = 0
        for dep in dependencies:
            if dep.resolved_version and dep.latest_version and dep.resolved_version != dep.latest_version:
                from app.utils.version_utils import compare_versions
                if compare_versions(dep.resolved_version, dep.latest_version) < 0:
                    outdated_count += 1
        
        if outdated_count > 0:
            score += outdated_count * self.weights.get('outdated_dep', 2)
            reasons.append(f"{outdated_count} outdated dependencies")
        
        return score, reasons
    
    def _calculate_lifecycle_score(self, findings: List[RiskFinding]) -> tuple:
        score = 0.0
        reasons = []
        
        lifecycle_findings = [f for f in findings if f.finding_type.value == 'lifecycle_script']
        if lifecycle_findings:
            count = len(lifecycle_findings)
            score += count * self.weights.get('lifecycle_script', 5)
            reasons.append(f"{count} packages with lifecycle scripts")
        
        return score, reasons
    
    def _calculate_typosquatting_score(self, findings: List[RiskFinding]) -> tuple:
        score = 0.0
        reasons = []
        
        typo_findings = [f for f in findings if f.finding_type.value == 'typosquatting']
        if typo_findings:
            count = len(typo_findings)
            score += count * self.weights.get('typosquatting', 10)
            reasons.append(f"{count} potential typosquatting packages")
        
        return score, reasons
    
    def _calculate_license_score(self, dependencies: List[Dependency]) -> tuple:
        score = 0.0
        reasons = []
        
        unknown_licenses = sum(1 for d in dependencies if d.license and d.license not in [
            'MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC',
            'MPL-2.0', 'LGPL-2.1', 'LGPL-3.0', 'GPL-2.0', 'GPL-3.0',
            'AGPL-3.0', 'EPL-2.0', 'CDDL-1.0', 'Unlicense', 'CC0-1.0'
        ])
        
        if unknown_licenses > 0:
            score += unknown_licenses * self.weights.get('unknown_license', 3)
            reasons.append(f"{unknown_licenses} packages with unknown/non-standard licenses")
        
        return score, reasons
    
    def _calculate_unpinned_score(self, dependencies: List[Dependency]) -> tuple:
        score = 0.0
        reasons = []
        
        unpinned = sum(1 for d in dependencies if not d.declared_version or d.declared_version in ('*', 'latest', ''))
        
        if unpinned > 0:
            score += unpinned * self.weights.get('unpinned_dep', 4)
            reasons.append(f"{unpinned} unpinned dependencies")
        
        return score, reasons
    
    def _calculate_transitive_vuln_score(self, findings: List[RiskFinding]) -> tuple:
        score = 0.0
        reasons = []
        
        transitive_findings = [f for f in findings if f.finding_type.value == 'transitive_vulnerability']
        if transitive_findings:
            count = len(transitive_findings)
            score += count * self.weights.get('transitive_vuln', 5)
            reasons.append(f"{count} vulnerable transitive dependencies")
        
        return score, reasons
    
    def _calculate_complexity_score(self, dependencies: List[Dependency]) -> tuple:
        score = 0.0
        reasons = []
        
        total = len(dependencies)
        if total > 500:
            score += 5
            reasons.append("Large dependency tree (>500 packages)")
        elif total > 200:
            score += 2
            reasons.append("Moderate dependency tree (>200 packages)")
        
        return score, reasons
    
    def _generate_summary(self, score: float, level: str, reasons: List[str]) -> str:
        if not reasons:
            return "No significant security risks detected."
        
        reason_str = "; ".join(reasons[:5])
        if len(reasons) > 5:
            reason_str += f" and {len(reasons) - 5} more"
        
        return f"Risk level: {level} ({score:.1f}/100). Primary factors: {reason_str}."
    
    def update_scan_risk(self, scan: Scan, risk_result: Dict):
        scan.risk_score = risk_result['score']
        scan.risk_level = risk_result['level']
        self.db.commit()


def calculate_risk_score(db: Session, scan: Scan, findings: List[RiskFinding], dependencies: List[Dependency], vulnerabilities: List[Vulnerability]) -> Dict:
    engine = RiskEngine(db)
    return engine.calculate_risk_score(scan, findings, dependencies, vulnerabilities)