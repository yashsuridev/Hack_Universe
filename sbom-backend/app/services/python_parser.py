import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from packaging.requirements import Requirement, InvalidRequirement
from packaging.specifiers import SpecifierSet
from app.models.dependency import DependencyType
from app.utils.version_utils import normalize_version, extract_version_from_range
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PythonParser:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.requirements_files: List[Path] = []
        self.setup_py: Optional[Path] = None
        self.pyproject_toml: Optional[Path] = None
        self.pipfile: Optional[Path] = None
    
    def parse(self, manifest_path: str, lockfile_path: Optional[str] = None) -> List[Dict]:
        full_path = self.project_root / manifest_path
        
        if full_path.name == 'requirements.txt' or full_path.name.endswith('.txt'):
            return self._parse_requirements_txt(full_path)
        elif full_path.name == 'setup.py':
            return self._parse_setup_py(full_path)
        elif full_path.name == 'pyproject.toml':
            return self._parse_pyproject_toml(full_path)
        elif full_path.name == 'Pipfile':
            return self._parse_pipfile(full_path)
        
        return []
    
    def _parse_requirements_txt(self, file_path: Path) -> List[Dict]:
        dependencies = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error("Failed to read requirements.txt", path=str(file_path), error=str(e))
            return dependencies
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#') or line.startswith('-'):
                continue
            
            if line.startswith('--'):
                continue
            
            try:
                req = Requirement(line)
                name = req.name
                declared_version = str(req.specifier) if req.specifier else ''
                resolved_version = extract_version_from_range(declared_version)
                
                dependencies.append({
                    'name': name,
                    'declared_version': declared_version or '*',
                    'resolved_version': resolved_version,
                    'dependency_type': DependencyType.DIRECT,
                    'ecosystem': 'pypi',
                    'purl': self._generate_purl(name, resolved_version),
                })
            except InvalidRequirement:
                logger.warning("Invalid requirement", line=line, file=str(file_path), line_num=line_num)
                name = self._extract_name_from_invalid(line)
                if name:
                    dependencies.append({
                        'name': name,
                        'declared_version': '*',
                        'resolved_version': None,
                        'dependency_type': DependencyType.DIRECT,
                        'ecosystem': 'pypi',
                        'purl': self._generate_purl(name, None),
                    })
        
        return dependencies
    
    def _extract_name_from_invalid(self, line: str) -> Optional[str]:
        match = re.match(r'^([A-Za-z0-9][A-Za-z0-9._-]*)', line)
        if match:
            return match.group(1)
        return None
    
    def _parse_setup_py(self, file_path: Path) -> List[Dict]:
        dependencies = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error("Failed to read setup.py", path=str(file_path), error=str(e))
            return dependencies
        
        install_requires_match = re.search(
            r'install_requires\s*=\s*\[([^\]]+)\]',
            content,
            re.DOTALL
        )
        
        if install_requires_match:
            reqs_str = install_requires_match.group(1)
            reqs = re.findall(r'[\'"]([^\'"]+)[\'"]', reqs_str)
            
            for req_str in reqs:
                try:
                    req = Requirement(req_str)
                    name = req.name
                    declared_version = str(req.specifier) if req.specifier else ''
                    resolved_version = extract_version_from_range(declared_version)
                    
                    dependencies.append({
                        'name': name,
                        'declared_version': declared_version or '*',
                        'resolved_version': resolved_version,
                        'dependency_type': DependencyType.DIRECT,
                        'ecosystem': 'pypi',
                        'purl': self._generate_purl(name, resolved_version),
                    })
                except InvalidRequirement:
                    name = self._extract_name_from_invalid(req_str)
                    if name:
                        dependencies.append({
                            'name': name,
                            'declared_version': '*',
                            'resolved_version': None,
                            'dependency_type': DependencyType.DIRECT,
                            'ecosystem': 'pypi',
                            'purl': self._generate_purl(name, None),
                        })
        
        return dependencies
    
    def _parse_pyproject_toml(self, file_path: Path) -> List[Dict]:
        dependencies = []
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                logger.error("tomllib/tomli not available for parsing pyproject.toml")
                return dependencies
        
        try:
            content = file_path.read_bytes()
            data = tomllib.loads(content.decode('utf-8'))
        except Exception as e:
            logger.error("Failed to parse pyproject.toml", path=str(file_path), error=str(e))
            return dependencies
        
        project = data.get('project', {})
        for req_str in project.get('dependencies', []):
            try:
                req = Requirement(req_str)
                name = req.name
                declared_version = str(req.specifier) if req.specifier else ''
                resolved_version = extract_version_from_range(declared_version)
                
                dependencies.append({
                    'name': name,
                    'declared_version': declared_version or '*',
                    'resolved_version': resolved_version,
                    'dependency_type': DependencyType.DIRECT,
                    'ecosystem': 'pypi',
                    'purl': self._generate_purl(name, resolved_version),
                })
            except InvalidRequirement:
                name = self._extract_name_from_invalid(req_str)
                if name:
                    dependencies.append({
                        'name': name,
                        'declared_version': '*',
                        'resolved_version': None,
                        'dependency_type': DependencyType.DIRECT,
                        'ecosystem': 'pypi',
                        'purl': self._generate_purl(name, None),
                    })
        
        optional_deps = project.get('optional-dependencies', {})
        for extra_name, reqs in optional_deps.items():
            for req_str in reqs:
                try:
                    req = Requirement(req_str)
                    name = req.name
                    declared_version = str(req.specifier) if req.specifier else ''
                    resolved_version = extract_version_from_range(declared_version)
                    
                    dependencies.append({
                        'name': name,
                        'declared_version': declared_version or '*',
                        'resolved_version': resolved_version,
                        'dependency_type': DependencyType.OPTIONAL,
                        'ecosystem': 'pypi',
                        'purl': self._generate_purl(name, resolved_version),
                    })
                except InvalidRequirement:
                    pass
        
        return dependencies
    
    def _parse_pipfile(self, file_path: Path) -> List[Dict]:
        dependencies = []
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                logger.error("tomllib/tomli not available for parsing Pipfile")
                return dependencies
        
        try:
            content = file_path.read_bytes()
            data = tomllib.loads(content.decode('utf-8'))
        except Exception as e:
            logger.error("Failed to parse Pipfile", path=str(file_path), error=str(e))
            return dependencies
        
        for section_name, dep_type in [('packages', DependencyType.DIRECT), ('dev-packages', DependencyType.DEVELOPMENT)]:
            for name, spec in data.get(section_name, {}).items():
                if isinstance(spec, str):
                    declared_version = spec
                    resolved_version = extract_version_from_range(spec)
                elif isinstance(spec, dict):
                    declared_version = spec.get('version', '*')
                    resolved_version = extract_version_from_range(declared_version)
                else:
                    declared_version = '*'
                    resolved_version = None
                
                dependencies.append({
                    'name': name.lower(),
                    'declared_version': declared_version,
                    'resolved_version': resolved_version,
                    'dependency_type': dep_type,
                    'ecosystem': 'pypi',
                    'purl': self._generate_purl(name.lower(), resolved_version),
                })
        
        return dependencies
    
    def _generate_purl(self, name: str, version: Optional[str]) -> str:
        if version:
            return f"pkg:pypi/{name}@{version}"
        return f"pkg:pypi/{name}"


def parse_requirements_txt(content: str) -> List[Dict]:
    from io import StringIO
    from pathlib import Path
    
    parser = PythonParser(Path('.'))
    return parser._parse_requirements_txt(StringIO(content))