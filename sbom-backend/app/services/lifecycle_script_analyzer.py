from typing import Dict, List, Optional, Any
from app.utils.logging import get_logger

logger = get_logger(__name__)


SUSPICIOUS_PATTERNS = [
    'curl', 'wget', 'fetch', 'axios', 'request', 'http.get', 'https.get',
    'child_process', 'exec', 'spawn', 'fork', 'execSync', 'spawnSync',
    'eval', 'Function', 'setTimeout', 'setInterval', 'process.exit',
    'fs.writeFile', 'fs.writeFileSync', 'fs.appendFile', 'fs.appendFileSync',
    'fs.unlink', 'fs.unlinkSync', 'fs.rmdir', 'fs.rmdirSync',
    'require("fs")', "require('fs')", 'import fs',
    'require("child_process")', "require('child_process')",
    'require("crypto")', "require('crypto')",
    'require("os")', "require('os')",
    'require("path")', "require('path')",
    'require("net")', "require('net')",
    'require("http")', "require('http')",
    'require("https")', "require('https')",
    'process.env', 'process.argv', 'process.cwd',
    '__dirname', '__filename', 'global.', 'globalThis.',
    'Buffer.from', 'Buffer.alloc', 'new Buffer',
    'crypto.createHash', 'crypto.randomBytes',
    'os.homedir', 'os.tmpdir', 'os.userInfo',
    'path.resolve', 'path.join', 'path.dirname',
    'net.connect', 'net.createConnection',
    'http.request', 'https.request',
]


class LifecycleScriptAnalyzer:
    def __init__(self):
        self.suspicious_patterns = SUSPICIOUS_PATTERNS
    
    def analyze(self, scripts: Dict[str, str]) -> Dict[str, Any]:
        if not scripts:
            return {'has_scripts': False, 'scripts': {}, 'risk_level': 'none', 'findings': []}
        
        findings = []
        risk_level = 'low'
        
        for script_name, script_content in scripts.items():
            script_findings = self._analyze_script(script_name, script_content)
            findings.extend(script_findings)
            
            if script_findings:
                for f in script_findings:
                    if f['severity'] == 'high':
                        risk_level = 'high'
                    elif f['severity'] == 'medium' and risk_level != 'high':
                        risk_level = 'medium'
        
        return {
            'has_scripts': True,
            'scripts': scripts,
            'risk_level': risk_level,
            'findings': findings,
        }
    
    def _analyze_script(self, script_name: str, content: str) -> List[Dict]:
        findings = []
        content_lower = content.lower()
        
        for pattern in self.suspicious_patterns:
            if pattern.lower() in content_lower:
                severity = self._get_pattern_severity(pattern)
                findings.append({
                    'script': script_name,
                    'pattern': pattern,
                    'severity': severity,
                    'description': f"Suspicious pattern '{pattern}' found in {script_name} script",
                })
        
        if 'install' in script_name or 'postinstall' in script_name:
            if len(content) > 500:
                findings.append({
                    'script': script_name,
                    'pattern': 'long_script',
                    'severity': 'medium',
                    'description': f"Long {script_name} script ({len(content)} chars) - review for hidden behavior",
                })
        
        if 'preinstall' in script_name or 'install' in script_name:
            if 'npm' in content_lower or 'yarn' in content_lower or 'pnpm' in content_lower:
                findings.append({
                    'script': script_name,
                    'pattern': 'package_manager_invocation',
                    'severity': 'high',
                    'description': f"{script_name} invokes package manager - potential supply chain attack",
                })
        
        return findings
    
    def _get_pattern_severity(self, pattern: str) -> str:
        high_patterns = [
            'child_process', 'exec', 'spawn', 'fork', 'execSync', 'spawnSync',
            'eval', 'Function', 'process.exit', 'npm', 'yarn', 'pnpm',
            'curl', 'wget', 'fetch', 'axios', 'request',
            'fs.writeFile', 'fs.writeFileSync', 'fs.unlink', 'fs.rmdir',
        ]
        
        medium_patterns = [
            'require("fs")', "require('fs')", 'import fs',
            'require("child_process")', "require('child_process')",
            'require("crypto")', "require('crypto')",
            'require("os")', "require('os')",
            'require("path")', "require('path')",
            'require("net")', "require('net')",
            'require("http")', "require('http')",
            'require("https")', "require('https')",
            'process.env', 'process.argv', 'process.cwd',
            '__dirname', '__filename', 'global.', 'globalThis.',
            'crypto.createHash', 'crypto.randomBytes',
            'os.homedir', 'os.tmpdir', 'os.userInfo',
            'path.resolve', 'path.join', 'path.dirname',
            'net.connect', 'net.createConnection',
            'http.request', 'https.request',
        ]
        
        if pattern in high_patterns:
            return 'high'
        elif pattern in medium_patterns:
            return 'medium'
        return 'low'


lifecycle_script_analyzer = LifecycleScriptAnalyzer()