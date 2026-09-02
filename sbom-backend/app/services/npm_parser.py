import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from app.models.dependency import DependencyType
from app.utils.version_utils import normalize_version
from app.utils.logging import get_logger

logger = get_logger(__name__)


class NPMParser:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.package_json: Dict = {}
        self.package_lock: Dict = {}
    
    def parse(self, manifest_path: str, lockfile_path: Optional[str] = None) -> List[Dict]:
        self._load_package_json(manifest_path)
        if lockfile_path:
            self._load_package_lock(lockfile_path)
        
        dependencies = []
        
        deps = self._extract_dependencies(
            self.package_json.get('dependencies', {}),
            DependencyType.DIRECT
        )
        dependencies.extend(deps)
        
        dev_deps = self._extract_dependencies(
            self.package_json.get('devDependencies', {}),
            DependencyType.DEVELOPMENT
        )
        dependencies.extend(dev_deps)
        
        optional_deps = self._extract_dependencies(
            self.package_json.get('optionalDependencies', {}),
            DependencyType.OPTIONAL
        )
        dependencies.extend(optional_deps)
        
        peer_deps = self._extract_dependencies(
            self.package_json.get('peerDependencies', {}),
            DependencyType.PEER
        )
        dependencies.extend(peer_deps)
        
        if self.package_lock:
            self._enrich_with_lockfile(dependencies)
        
        return dependencies
    
    def _load_package_json(self, manifest_path: str):
        full_path = self.project_root / manifest_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                self.package_json = json.load(f)
        except Exception as e:
            logger.error("Failed to parse package.json", path=manifest_path, error=str(e))
            raise
    
    def _load_package_lock(self, lockfile_path: str):
        full_path = self.project_root / lockfile_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                self.package_lock = json.load(f)
        except Exception as e:
            logger.warning("Failed to parse package-lock.json", path=lockfile_path, error=str(e))
            self.package_lock = {}
    
    def _extract_dependencies(self, deps_dict: Dict, dep_type: DependencyType) -> List[Dict]:
        result = []
        for name, version_range in deps_dict.items():
            version_range = normalize_version(str(version_range))
            result.append({
                'name': name,
                'declared_version': version_range,
                'resolved_version': None,
                'dependency_type': dep_type,
                'ecosystem': 'npm',
            })
        return result
    
    def _enrich_with_lockfile(self, dependencies: List[Dict]):
        lock_deps = self._parse_lockfile_dependencies()
        existing_names = {d['name'] for d in dependencies}
        
        for dep in dependencies:
            name = dep['name']
            if name in lock_deps:
                lock_info = lock_deps[name]
                dep['resolved_version'] = lock_info.get('version')
                dep['purl'] = self._generate_purl(name, lock_info.get('version'))
                dep['license'] = lock_info.get('license')
                dep['package_metadata'] = {
                    'integrity': lock_info.get('integrity'),
                    'resolved': lock_info.get('resolved'),
                }
            else:
                dep['purl'] = self._generate_purl(name, dep.get('declared_version'))
        
        for name, lock_info in lock_deps.items():
            if name not in existing_names:
                version = lock_info.get('version')
                dependencies.append({
                    'name': name,
                    'declared_version': version,
                    'resolved_version': version,
                    'dependency_type': DependencyType.TRANSITIVE,
                    'ecosystem': 'npm',
                    'purl': self._generate_purl(name, version),
                    'license': lock_info.get('license'),
                    'package_metadata': {
                        'integrity': lock_info.get('integrity'),
                        'resolved': lock_info.get('resolved'),
                    }
                })
    
    def _parse_lockfile_dependencies(self) -> Dict[str, Dict]:
        result = {}
        
        if 'packages' in self.package_lock:
            for path, info in self.package_lock['packages'].items():
                if path == '':
                    continue
                name = path.split('node_modules/')[-1]
                if name:
                    result[name] = {
                        'version': info.get('version'),
                        'license': info.get('license'),
                        'resolved': info.get('resolved'),
                        'integrity': info.get('integrity'),
                    }
        elif 'dependencies' in self.package_lock:
            for name, info in self.package_lock['dependencies'].items():
                result[name] = {
                    'version': info.get('version'),
                    'license': info.get('license'),
                    'resolved': info.get('resolved'),
                    'integrity': info.get('integrity'),
                }
        
        return result
    
    def _generate_purl(self, name: str, version: Optional[str]) -> str:
        if version:
            return f"pkg:npm/{name}@{version}"
        return f"pkg:npm/{name}"
    
    def get_lifecycle_scripts(self, package_name: str) -> Dict[str, str]:
        scripts = {}
        if self.package_lock and 'packages' in self.package_lock:
            for path, info in self.package_lock['packages'].items():
                if path.endswith(f'/node_modules/{package_name}') or path == f'node_modules/{package_name}':
                    for script_name in ['preinstall', 'install', 'postinstall', 'preuninstall', 'uninstall', 'postuninstall']:
                        if script_name in info.get('scripts', {}):
                            scripts[script_name] = info['scripts'][script_name]
        return scripts
    
    def build_dependency_tree(self) -> Dict[str, List[str]]:
        tree = {}
        if not self.package_lock or 'packages' not in self.package_lock:
            return tree
        
        for path, info in self.package_lock['packages'].items():
            if path == '':
                continue
            name = path.replace('node_modules/', '')
            deps = info.get('dependencies', {})
            tree[name] = list(deps.keys())
        
        return tree


def parse_package_json(content: str) -> Dict:
    return json.loads(content)


def parse_package_lock(content: str) -> Dict:
    return json.loads(content)