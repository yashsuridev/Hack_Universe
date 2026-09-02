from typing import Dict, List, Optional, Any
from pathlib import Path
from app.services.npm_parser import NPMParser
from app.services.python_parser import PythonParser
from app.services.maven_parser import MavenParser
from app.services.manifest_detector import ManifestDetector
from app.models.project import Ecosystem
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DependencyAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.detector = ManifestDetector(project_root)
    
    def analyze(self) -> Dict[str, Any]:
        manifests = self.detector.detect()
        ecosystems = self.detector.get_ecosystems()
        
        all_dependencies = []
        manifest_info = []
        
        for ecosystem in ecosystems:
            primary_manifest = self.detector.get_primary_manifest(ecosystem)
            lockfile = self.detector.get_lockfile(ecosystem)
            
            if not primary_manifest:
                continue
            
            manifest_info.append({
                'ecosystem': ecosystem.value,
                'manifest_path': str(primary_manifest),
                'lockfile_path': str(lockfile) if lockfile else None,
            })
            
            deps = self._parse_ecosystem(ecosystem, str(primary_manifest), str(lockfile) if lockfile else None)
            all_dependencies.extend(deps)
        
        stats = self._calculate_stats(all_dependencies)
        
        return {
            'ecosystems': [e.value for e in ecosystems],
            'manifests': manifest_info,
            'dependencies': all_dependencies,
            'stats': stats,
        }
    
    def _parse_ecosystem(self, ecosystem: Ecosystem, manifest_path: str, lockfile_path: Optional[str]) -> List[Dict]:
        if ecosystem == Ecosystem.NPM:
            parser = NPMParser(self.project_root)
            return parser.parse(manifest_path, lockfile_path)
        elif ecosystem == Ecosystem.PYPI:
            parser = PythonParser(self.project_root)
            return parser.parse(manifest_path, lockfile_path)
        elif ecosystem == Ecosystem.MAVEN:
            parser = MavenParser(self.project_root)
            return parser.parse(manifest_path, lockfile_path)
        return []
    
    def _calculate_stats(self, dependencies: List[Dict]) -> Dict[str, int]:
        stats = {
            'total': len(dependencies),
            'direct': 0,
            'transitive': 0,
            'development': 0,
            'optional': 0,
            'peer': 0,
            'by_ecosystem': {},
        }
        
        for dep in dependencies:
            dep_type = dep.get('dependency_type', 'direct')
            ecosystem = dep.get('ecosystem', 'unknown')
            
            if dep_type == 'direct':
                stats['direct'] += 1
            elif dep_type == 'transitive':
                stats['transitive'] += 1
            elif dep_type == 'development':
                stats['development'] += 1
            elif dep_type == 'optional':
                stats['optional'] += 1
            elif dep_type == 'peer':
                stats['peer'] += 1
            
            stats['by_ecosystem'][ecosystem] = stats['by_ecosystem'].get(ecosystem, 0) + 1
        
        return stats
    
    def build_dependency_tree(self, ecosystem: Ecosystem) -> Dict[str, List[str]]:
        if ecosystem == Ecosystem.NPM:
            primary_manifest = self.detector.get_primary_manifest(ecosystem)
            lockfile = self.detector.get_lockfile(ecosystem)
            if primary_manifest:
                parser = NPMParser(self.project_root)
                parser.parse(str(primary_manifest), str(lockfile) if lockfile else None)
                return parser.build_dependency_tree()
        return {}


def analyze_project(project_root: str) -> Dict[str, Any]:
    analyzer = DependencyAnalyzer(project_root)
    return analyzer.analyze()