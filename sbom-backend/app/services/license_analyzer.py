from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.license import LicenseInfo, KnownLicense, LicenseType, LicenseRiskLevel
from app.utils.logging import get_logger

logger = get_logger(__name__)


SPDX_LICENSES = {
    'MIT': {'risk': LicenseRiskLevel.LOW, 'osi': True, 'fsf': True, 'category': 'Permissive'},
    'Apache-2.0': {'risk': LicenseRiskLevel.LOW, 'osi': True, 'fsf': True, 'category': 'Permissive'},
    'BSD-2-Clause': {'risk': LicenseRiskLevel.LOW, 'osi': True, 'fsf': True, 'category': 'Permissive'},
    'BSD-3-Clause': {'risk': LicenseRiskLevel.LOW, 'osi': True, 'fsf': True, 'category': 'Permissive'},
    'ISC': {'risk': LicenseRiskLevel.LOW, 'osi': True, 'fsf': True, 'category': 'Permissive'},
    'MPL-2.0': {'risk': LicenseRiskLevel.MEDIUM, 'osi': True, 'fsf': True, 'category': 'Weak Copyleft'},
    'LGPL-2.1': {'risk': LicenseRiskLevel.MEDIUM, 'osi': True, 'fsf': True, 'category': 'Weak Copyleft'},
    'LGPL-3.0': {'risk': LicenseRiskLevel.MEDIUM, 'osi': True, 'fsf': True, 'category': 'Weak Copyleft'},
    'GPL-2.0': {'risk': LicenseRiskLevel.HIGH, 'osi': True, 'fsf': True, 'category': 'Strong Copyleft'},
    'GPL-3.0': {'risk': LicenseRiskLevel.HIGH, 'osi': True, 'fsf': True, 'category': 'Strong Copyleft'},
    'AGPL-3.0': {'risk': LicenseRiskLevel.HIGH, 'osi': True, 'fsf': True, 'category': 'Strong Copyleft'},
    'EPL-2.0': {'risk': LicenseRiskLevel.MEDIUM, 'osi': True, 'fsf': True, 'category': 'Weak Copyleft'},
    'CDDL-1.0': {'risk': LicenseRiskLevel.MEDIUM, 'osi': True, 'fsf': True, 'category': 'Weak Copyleft'},
    'Unlicense': {'risk': LicenseRiskLevel.LOW, 'osi': True, 'fsf': True, 'category': 'Public Domain'},
    'CC0-1.0': {'risk': LicenseRiskLevel.LOW, 'osi': True, 'fsf': True, 'category': 'Public Domain'},
}


class LicenseAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self._ensure_known_licenses()
    
    def _ensure_known_licenses(self):
        for spdx_id, info in SPDX_LICENSES.items():
            existing = self.db.query(KnownLicense).filter(KnownLicense.spdx_id == spdx_id).first()
            if not existing:
                license_obj = KnownLicense(
                    spdx_id=spdx_id,
                    name=spdx_id,
                    is_osi_approved=info['osi'],
                    is_fsf_libre=info['fsf'],
                    risk_level=info['risk'],
                    category=info['category'],
                )
                self.db.add(license_obj)
        self.db.commit()
    
    def analyze_license(self, license_str: Optional[str]) -> Dict:
        if not license_str:
            return {
                'spdx_id': None,
                'name': None,
                'risk_level': LicenseRiskLevel.UNKNOWN,
                'is_osi_approved': False,
                'is_fsf_libre': False,
                'is_unknown': True,
            }
        
        license_str = license_str.strip()
        
        if license_str in SPDX_LICENSES:
            info = SPDX_LICENSES[license_str]
            return {
                'spdx_id': license_str,
                'name': license_str,
                'risk_level': info['risk'],
                'is_osi_approved': info['osi'],
                'is_fsf_libre': info['fsf'],
                'is_unknown': False,
            }
        
        known = self.db.query(KnownLicense).filter(KnownLicense.spdx_id == license_str).first()
        if known:
            return {
                'spdx_id': known.spdx_id,
                'name': known.name,
                'risk_level': known.risk_level,
                'is_osi_approved': known.is_osi_approved,
                'is_fsf_libre': known.is_fsf_libre,
                'is_unknown': False,
            }
        
        return {
            'spdx_id': license_str,
            'name': license_str,
            'risk_level': LicenseRiskLevel.UNKNOWN,
            'is_osi_approved': False,
            'is_fsf_libre': False,
            'is_unknown': True,
        }
    
    def save_license_info(self, dependency_id: int, license_str: Optional[str], license_url: Optional[str] = None) -> LicenseInfo:
        analysis = self.analyze_license(license_str)
        
        license_info = LicenseInfo(
            dependency_id=dependency_id,
            license_type=LicenseType.SPDX if analysis['spdx_id'] in SPDX_LICENSES else LicenseType.CUSTOM,
            spdx_id=analysis['spdx_id'],
            name=analysis['name'],
            url=license_url,
            risk_level=analysis['risk_level'],
            is_osi_approved=analysis['is_osi_approved'],
            is_fsf_libre=analysis['is_fsf_libre'],
        )
        
        self.db.add(license_info)
        self.db.commit()
        self.db.refresh(license_info)
        
        return license_info


def normalize_license(license_str: str) -> str:
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