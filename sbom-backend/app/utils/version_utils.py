from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from typing import Optional, Tuple, List
import re


def parse_version(version_str: str) -> Optional[Version]:
    if not version_str:
        return None
    try:
        return Version(version_str.strip())
    except InvalidVersion:
        return None


def parse_specifier(specifier_str: str) -> Optional[SpecifierSet]:
    if not specifier_str:
        return None
    try:
        return SpecifierSet(specifier_str.strip())
    except InvalidSpecifier:
        return None


def version_in_range(version: str, specifier: str) -> bool:
    v = parse_version(version)
    spec = parse_specifier(specifier)
    if v is None or spec is None:
        return False
    return v in spec


def compare_versions(v1: str, v2: str) -> int:
    parsed_v1 = parse_version(v1)
    parsed_v2 = parse_version(v2)
    
    if parsed_v1 is None and parsed_v2 is None:
        return 0
    if parsed_v1 is None:
        return -1
    if parsed_v2 is None:
        return 1
    
    if parsed_v1 < parsed_v2:
        return -1
    elif parsed_v1 > parsed_v2:
        return 1
    return 0


def is_outdated(installed: str, latest: str) -> bool:
    return compare_versions(installed, latest) < 0


def is_vulnerable_version(installed: str, affected_range: str) -> bool:
    return version_in_range(installed, affected_range)


def get_fixed_version(affected_ranges: List[str], installed: str) -> Optional[str]:
    for range_str in affected_ranges:
        spec = parse_specifier(range_str)
        if spec is None:
            continue
        for specifier in spec:
            if specifier.operator in (">=", ">", "~=", "==", "==="):
                fixed = specifier.version
                if parse_version(fixed) and compare_versions(fixed, installed) > 0:
                    return fixed
    return None


def normalize_version(version: str) -> str:
    version = version.strip()
    version = re.sub(r'^v', '', version)
    version = re.sub(r'^=', '', version)
    return version


def extract_version_from_range(range_str: str) -> Optional[str]:
    spec = parse_specifier(range_str)
    if spec is None:
        return None
    for specifier in spec:
        if specifier.operator in ("==", "===", "~="):
            return specifier.version
    return None