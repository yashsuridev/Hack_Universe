from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
from app.models.project import Ecosystem
from app.utils.file_security import find_manifest_files
from app.utils.logging import get_logger

logger = get_logger(__name__)


MANIFEST_PATTERNS = {
    Ecosystem.NPM: [
        'package.json',
        'package-lock.json',
        'pnpm-lock.yaml',
        'yarn.lock',
    ],
    Ecosystem.PYPI: [
        'requirements.txt',
        'requirements-dev.txt',
        'setup.py',
        'setup.cfg',
        'pyproject.toml',
        'Pipfile',
        'Pipfile.lock',
    ],
    Ecosystem.MAVEN: [
        'pom.xml',
        'build.gradle',
        'build.gradle.kts',
        'settings.gradle',
        'settings.gradle.kts',
    ],
}

LOCKFILE_PATTERNS = {
    Ecosystem.NPM: ['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock'],
    Ecosystem.PYPI: ['Pipfile.lock', 'requirements.txt'],
    Ecosystem.MAVEN: ['pom.xml'],
}


class ManifestDetector:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.found_manifests: Dict[Ecosystem, List[Path]] = {}
        self.found_lockfiles: Dict[Ecosystem, List[Path]] = {}
    
    def detect(self) -> Dict[Ecosystem, List[Path]]:
        all_files = find_manifest_files(str(self.root_dir))
        
        for file_path in all_files:
            rel_path = Path(file_path).relative_to(self.root_dir)
            file_name = rel_path.name
            
            for ecosystem, patterns in MANIFEST_PATTERNS.items():
                if file_name in patterns:
                    if ecosystem not in self.found_manifests:
                        self.found_manifests[ecosystem] = []
                    self.found_manifests[ecosystem].append(rel_path)
                    break
        
        return self.found_manifests
    
    def get_primary_manifest(self, ecosystem: Ecosystem) -> Optional[Path]:
        manifests = self.found_manifests.get(ecosystem, [])
        if not manifests:
            return None
        
        priority = {
            Ecosystem.NPM: ['package.json'],
            Ecosystem.PYPI: ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
            Ecosystem.MAVEN: ['pom.xml'],
        }
        
        for pref in priority.get(ecosystem, []):
            for m in manifests:
                if m.name == pref:
                    return m
        
        return manifests[0] if manifests else None
    
    def get_lockfile(self, ecosystem: Ecosystem) -> Optional[Path]:
        manifests = self.found_manifests.get(ecosystem, [])
        for manifest in manifests:
            lockfile_patterns = LOCKFILE_PATTERNS.get(ecosystem, [])
            for pattern in lockfile_patterns:
                lockfile_path = manifest.parent / pattern
                full_lockfile = self.root_dir / lockfile_path
                if full_lockfile.exists():
                    return lockfile_path
        return None
    
    def get_ecosystems(self) -> List[Ecosystem]:
        return list(self.found_manifests.keys())
    
    def get_manifest_info(self) -> List[Dict]:
        info = []
        for ecosystem, manifests in self.found_manifests.items():
            for manifest in manifests:
                lockfile = self.get_lockfile(ecosystem)
                info.append({
                    'ecosystem': ecosystem.value,
                    'manifest_path': str(manifest),
                    'lockfile_path': str(lockfile) if lockfile else None,
                })
        return info