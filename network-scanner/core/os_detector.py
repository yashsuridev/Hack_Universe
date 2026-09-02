"""
os_detector.py
---------------
Basic, low-impact, passive OS fingerprinting based on:
  - TTL of ICMP/TCP responses
  - which well-known ports are open (Windows vs Unix indicator ports)
  - simple heuristics only — never a definitive claim

Confidence is always reported as Low / Medium / Unknown; the tool never
claims certainty about OS identity.
"""

import platform
import re
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from utils.port_database import WINDOWS_INDICATOR_PORTS, UNIX_INDICATOR_PORTS


@dataclass
class OSGuess:
    os_guess: str
    confidence: str  # Low | Medium | Unknown
    evidence: List[str] = field(default_factory=list)


def _get_ttl(ip: str, timeout_s: float = 1.0) -> Optional[int]:
    system = platform.system().lower()
    try:
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", str(int(timeout_s * 1000)), ip]
        else:
            cmd = ["ping", "-c", "1", "-W", str(max(int(round(timeout_s)), 1)), ip]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 2).stdout
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None

    match = re.search(r"ttl[=:]\s*(\d+)", out, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _ttl_os_hint(ttl: int) -> Optional[str]:
    """
    Rough heuristic based on common default TTL values.
    Real TTL is (default_ttl - hops), so this is approximate.
    """
    if ttl is None:
        return None
    if ttl <= 64:
        return "Linux/Unix"
    if ttl <= 128:
        return "Windows"
    if ttl <= 255:
        return "Network Device"
    return None


def guess_os(ip: str, open_tcp_ports: List[int]) -> OSGuess:
    evidence: List[str] = []
    votes = {"Windows": 0, "Linux/Unix": 0, "Network Device": 0, "macOS": 0}

    open_set = set(open_tcp_ports)

    windows_hits = open_set & WINDOWS_INDICATOR_PORTS
    if windows_hits:
        votes["Windows"] += len(windows_hits)
        evidence.append(f"Port(s) {sorted(windows_hits)} open (Windows-associated services)")

    unix_hits = open_set & UNIX_INDICATOR_PORTS
    if unix_hits:
        votes["Linux/Unix"] += len(unix_hits)
        evidence.append(f"Port(s) {sorted(unix_hits)} open (Unix/Linux-associated services)")

    ttl = _get_ttl(ip)
    if ttl is not None:
        ttl_hint = _ttl_os_hint(ttl)
        if ttl_hint:
            votes[ttl_hint] = votes.get(ttl_hint, 0) + 1
            evidence.append(f"TTL observed: {ttl} (consistent with {ttl_hint})")

    if not evidence:
        return OSGuess(os_guess="Unknown", confidence="Unknown", evidence=["Insufficient data"])

    best_os = max(votes, key=votes.get)
    best_score = votes[best_os]

    if best_score == 0:
        return OSGuess(os_guess="Unknown", confidence="Unknown", evidence=evidence)

    confidence = "Medium" if best_score >= 2 else "Low"
    return OSGuess(os_guess=f"Likely {best_os}", confidence=confidence, evidence=evidence)
