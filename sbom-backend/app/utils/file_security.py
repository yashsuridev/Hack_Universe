import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional


MAX_ZIP_SIZE = 50 * 1024 * 1024
MAX_EXTRACTED_SIZE = 500 * 1024 * 1024
MAX_FILE_COUNT = 10000
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    '.json', '.txt', '.xml', '.yml', '.yaml', '.toml', '.lock',
    '.js', '.ts', '.py', '.java', '.kt', '.gradle', '.pom',
    '.md', '.rst', '.license', '.licence'
}
BLOCKED_PATHS = ['..', '~', '/etc', '/proc', '/sys', 'C:\\Windows', 'C:\\System32']


class ZipSecurityError(Exception):
    pass


def validate_zip_file(zip_path: str) -> Tuple[bool, str]:
    if not os.path.exists(zip_path):
        return False, "File does not exist"
    
    file_size = os.path.getsize(zip_path)
    if file_size > MAX_ZIP_SIZE:
        return False, f"ZIP file exceeds maximum size of {MAX_ZIP_SIZE / (1024*1024)}MB"
    
    if file_size == 0:
        return False, "ZIP file is empty"
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            if zf.testzip() is not None:
                return False, "ZIP file is corrupted"
            
            file_count = len(zf.infolist())
            if file_count > MAX_FILE_COUNT:
                return False, f"ZIP contains too many files ({file_count} > {MAX_FILE_COUNT})"
            
            total_size = 0
            for info in zf.infolist():
                if info.file_size > MAX_FILE_SIZE:
                    return False, f"File {info.filename} exceeds maximum size of {MAX_FILE_SIZE / (1024*1024)}MB"
                total_size += info.file_size
                
                if is_path_traversal(info.filename):
                    return False, f"Path traversal detected in {info.filename}"
                
                if is_blocked_path(info.filename):
                    return False, f"Blocked path detected: {info.filename}"
            
            if total_size > MAX_EXTRACTED_SIZE:
                return False, f"Total extracted size exceeds maximum of {MAX_EXTRACTED_SIZE / (1024*1024)}MB"
    
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file format"
    except Exception as e:
        return False, f"ZIP validation error: {str(e)}"
    
    return True, "OK"


def is_path_traversal(filename: str) -> bool:
    normalized = os.path.normpath(filename)
    return normalized.startswith('..') or os.path.isabs(normalized)


def is_blocked_path(filename: str) -> bool:
    normalized = os.path.normpath(filename).lower()
    for blocked in BLOCKED_PATHS:
        if blocked.lower() in normalized:
            return True
    return False


def safe_extract_zip(zip_path: str, extract_dir: str) -> Tuple[bool, str, List[str]]:
    valid, msg = validate_zip_file(zip_path)
    if not valid:
        return False, msg, []
    
    extracted_files = []
    abs_extract_dir = os.path.abspath(extract_dir)
    try:
        os.makedirs(abs_extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.infolist():
                if is_path_traversal(member.filename) or is_blocked_path(member.filename):
                    continue
                
                target_path = os.path.abspath(os.path.join(abs_extract_dir, member.filename))
                
                if not target_path.lower().startswith(abs_extract_dir.lower()):
                    continue
                
                if member.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zf.open(member) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    extracted_files.append(target_path)
    
    except Exception as e:
        return False, f"Extraction failed: {str(e)}", extracted_files
    
    return True, "OK", extracted_files


def cleanup_temp_dir(temp_dir: str) -> bool:
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return True
    except Exception:
        return False


def get_file_type(file_path: str) -> Optional[str]:
    ext = Path(file_path).suffix.lower()
    if ext in ALLOWED_EXTENSIONS:
        return ext
    return None


def is_allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def find_manifest_files(root_dir: str) -> List[str]:
    manifest_names = {
        'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock',
        'requirements.txt', 'requirements-dev.txt', 'setup.py', 'setup.cfg', 'pyproject.toml', 'Pipfile', 'Pipfile.lock',
        'pom.xml', 'build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts'
    }
    
    found = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', '__pycache__', 'target', 'build', 'dist', '.git')]
        
        for file in files:
            if file in manifest_names:
                found.append(os.path.join(root, file))
    
    return found