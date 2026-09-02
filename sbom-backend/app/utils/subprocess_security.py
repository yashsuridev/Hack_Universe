import subprocess
import shlex
from typing import List, Tuple, Optional
import asyncio


ALLOWED_COMMANDS = {
    'npm': ['npm', 'view', '--json'],
    'pip': ['pip', 'index', 'versions'],
    'mvn': ['mvn', 'dependency:tree'],
}


class SubprocessSecurityError(Exception):
    pass


def validate_command(command: List[str]) -> bool:
    if not command:
        return False
    
    base_cmd = command[0]
    if base_cmd not in ALLOWED_COMMANDS:
        return False
    
    allowed_prefix = ALLOWED_COMMANDS[base_cmd]
    if len(command) < len(allowed_prefix):
        return False
    
    for i, allowed_arg in enumerate(allowed_prefix):
        if command[i] != allowed_arg:
            return False
    
    return True


async def run_command_safe(
    command: List[str],
    cwd: Optional[str] = None,
    timeout: int = 30,
    env: Optional[dict] = None
) -> Tuple[int, str, str]:
    if not validate_command(command):
        raise SubprocessSecurityError(f"Command not allowed: {command}")
    
    safe_env = os.environ.copy()
    if env:
        safe_env.update(env)
    
    safe_env.update({
        'PATH': '/usr/bin:/bin:/usr/local/bin',
        'HOME': '/tmp',
        'USER': 'nobody',
    })
    
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            env=safe_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=1024 * 1024,
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise SubprocessSecurityError(f"Command timed out after {timeout}s")
        
        return process.returncode, stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')
    
    except Exception as e:
        raise SubprocessSecurityError(f"Command execution failed: {str(e)}")


def run_command_sync(
    command: List[str],
    cwd: Optional[str] = None,
    timeout: int = 30,
    env: Optional[dict] = None
) -> Tuple[int, str, str]:
    if not validate_command(command):
        raise SubprocessSecurityError(f"Command not allowed: {command}")
    
    safe_env = os.environ.copy()
    if env:
        safe_env.update(env)
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=safe_env,
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        raise SubprocessSecurityError(f"Command timed out after {timeout}s")
    except Exception as e:
        raise SubprocessSecurityError(f"Command execution failed: {str(e)}")


import os