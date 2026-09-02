import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from packageurl import PackageURL


def normalize_license(license_str: str) -> str:
    """Normalize a license string to SPDX format."""
    if not license_str:
        return ""
    license_str = license_str.strip()
    replacements = {
        'mit': 'MIT',
        'apache 2.0': 'Apache-2.0',
        'apache-2.0': 'Apache-2.0',
        'bsd 2 clause': 'BSD-2-Clause',
        'bsd 3 clause': 'BSD-3-Clause',
        'bsd-2-clause': 'BSD-2-Clause',
        'bsd-3-clause': 'BSD-3-Clause',
        'gpl 2.0': 'GPL-2.0',
        'gpl 3.0': 'GPL-3.0',
        'gpl-2.0': 'GPL-2.0',
        'gpl-3.0': 'GPL-3.0',
        'lgpl 2.1': 'LGPL-2.1',
        'lgpl 3.0': 'LGPL-3.0',
        'lgpl-2.1': 'LGPL-2.1',
        'lgpl-3.0': 'LGPL-3.0',
        'agpl 3.0': 'AGPL-3.0',
        'agpl-3.0': 'AGPL-3.0',
    }
    lower = license_str.lower()
    return replacements.get(lower, license_str)


class SBOMGenerator:
    def __init__(self):
        self.bom_dict: Dict = {}
        self.component_map: Dict[str, Any] = {}

    def generate(self, scan_id: int, dependencies: List[Any], vulnerabilities: List[Any], project_name: str, project_version: str = "1.0.0") -> Dict:
        self.bom_dict = self._create_bom(project_name, project_version)
        self.component_map = {}

        for dep in dependencies:
            component = self._create_component(dep)
            self.bom_dict["components"].append(component)
            self.component_map[self._get_component_key(dep)] = component

        self._add_dependencies(dependencies)

        return self._serialize_bom(vulnerabilities)

    def _create_bom(self, project_name: str, project_version: str) -> Dict:
        """Create the base BOM dictionary structure."""
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "serialNumber": str(uuid.uuid4()),
            "version": 1,
            "metadata": self._create_metadata(project_name, project_version),
            "components": [],
            "dependencies": [],
            "compositions": [],
            "services": [],
            "vulnerabilities": [],
        }

    def _create_metadata(self, project_name: str, project_version: str) -> Dict:
        """Create the BOM metadata section."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tools": [{
                "name": "SBOM Auditor",
                "version": "1.0.0",
                "vendor": {"name": "Security Team"}
            }],
            "authors": [{"name": "SBOM Auditor"}],
            "component": {
                "type": "application",
                "name": project_name,
                "version": project_version,
                "purl": f"pkg:generic/{project_name}@{project_version}",
                "description": None,
            }
        }

    def _create_component(self, dep: Any) -> Dict:
        """Create a component dictionary from a Dependency model."""
        # Parse PURL
        purl_str = None
        if dep.purl:
            try:
                purl_obj = PackageURL.from_string(dep.purl)
                purl_str = str(purl_obj) if purl_obj else None
            except Exception:
                purl_str = None
        
        # Normalize license
        license_normalized = None
        if dep.license:
            license_normalized = normalize_license(dep.license)
        
        component = {
            "type": "library",
            "name": dep.name,
            "version": dep.resolved_version or dep.declared_version or "unknown",
            "purl": purl_str,
            "description": dep.package_metadata.get('description') if dep.package_metadata else None,
            "licenses": [],
            "hashes": [],
            "externalReferences": [],
            "properties": {},
        }
        
        if license_normalized:
            component["licenses"] = [{"spdxId": license_normalized}]
        
        if dep.package_metadata and dep.package_metadata.get('integrity'):
            component["hashes"] = [{
                "algorithm": "SHA-512",
                "value": dep.package_metadata['integrity']
            }]
        
        if dep.dependency_path:
            component["properties"]["dependency_path"] = dep.dependency_path
        
        return component

    def _get_component_key(self, dep: Any) -> str:
        return f"{dep.ecosystem}:{dep.name}@{dep.resolved_version or dep.declared_version}"

    def _add_dependencies(self, dependencies: List[Any]):
        """Add dependency relationships to the BOM."""
        # Build a map of component names
        comp_name_map = {}
        for dep in dependencies:
            key = self._get_component_key(dep)
            if key not in comp_name_map:
                comp_name_map[key] = dep.name
        
        # Add dependency entries
        added_deps = set()
        for dep in dependencies:
            dep_key = self._get_component_key(dep)
            if dep_key not in comp_name_map:
                continue
            
            component_name = comp_name_map[dep_key]
            
            # If not already added as a dependency entry
            if dep_key not in added_deps:
                dep_entry = {
                    "ref": component_name,
                    "depends_on": []
                }
                
                # Add parent dependencies from dependency_path
                if dep.dependency_path:
                    for parent_name in dep.dependency_path:
                        parent_key = f"{dep.ecosystem}:{parent_name}"
                        for key, name in comp_name_map.items():
                            if key.startswith(parent_key) and name != component_name:
                                if name not in dep_entry["depends_on"]:
                                    dep_entry["depends_on"].append(name)
                
                dep_entry["ref"] = component_name
                self.bom_dict["dependencies"].append(dep_entry)
                added_deps.add(dep_key)

    def _serialize_bom(self, vulnerabilities: List[Any]) -> Dict:
        """Serialize the BOM to a dictionary, adding vulnerability information."""
        vuln_list = []
        for vuln in vulnerabilities:
            vuln_entry = {
                "id": vuln.osv_id,
                "source": {"name": "OSV", "url": "https://osv.dev"},
                "description": vuln.summary or vuln.details or "",
                "affected_versions": vuln.affected_versions,
                "fixed_version": vuln.fixed_version,
                "severity": vuln.severity.value,
                "cvss_score": vuln.cvss_score,
                "cvss_vector": vuln.cvss_vector,
                "references": vuln.references,
                "published_at": vuln.published_at.isoformat() if vuln.published_at else None,
                "modified_at": vuln.modified_at.isoformat() if vuln.modified_at else None,
            }
            vuln_list.append(vuln_entry)
        
        self.bom_dict["vulnerabilities"] = vuln_list
        
        return self.bom_dict

    def generate_json_string(self, scan_id: int, dependencies: List[Any], vulnerabilities: List[Any], project_name: str, project_version: str = "1.0.0") -> str:
        bom_dict = self.generate(scan_id, dependencies, vulnerabilities, project_name, project_version)
        return json.dumps(bom_dict, indent=2)


def create_sbom_from_scan(scan_id: int, dependencies: List[Any], vulnerabilities: List[Any], project_name: str) -> Dict:
    generator = SBOMGenerator()
    return generator.generate(scan_id, dependencies, vulnerabilities, project_name)