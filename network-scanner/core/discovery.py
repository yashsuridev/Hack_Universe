"""
discovery.py
------------
Host discovery using multiple safe techniques:
  1. ICMP echo (ping) via the system 'ping' utility (no raw sockets / root
     needed, works cross-platform).
  2. TCP probe against a handful of commonly-open ports, used as a
     fallback for hosts that don't respond to ICMP (many hosts and
     firewalls block ICMP by default).
  3. ARP table lookup for local-segment hosts (best-effort; used only to
     enrich results with MAC addresses, never as the sole liveness signal).

A host is marked DOWN only if none of the applicable techniques got a
response — non-response to ICMP alone is never treated as proof a host
is offline, per spec.
"""

import asyncio
import platform
import re
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

# A very small set of commonly-open ports used only for TCP-probe discovery
_PROBE_PORTS = [80, 443, 22, 445, 3389, 53]


@dataclass
class HostResult:
    ip: str
    is_up: bool
    latency_ms: Optional[float] = None
    mac: Optional[str] = None
    discovery_method: Optional[str] = None


def _ping_command(ip: str, timeout_s: float) -> List[str]:
    system = platform.system().lower()
    timeout_ms = max(int(timeout_s * 1000), 100)
    if system == "windows":
        return ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    # Linux / macOS
    # -c 1: one packet, -W: timeout in seconds (Linux) or ms (varies) —
    # use a ceiling of at least 1s for portability
    timeout_s_ceiled = max(int(round(timeout_s)), 1)
    return ["ping", "-c", "1", "-W", str(timeout_s_ceiled), ip]


async def _icmp_ping(ip: str, timeout_s: float) -> Optional[float]:
    """Return latency in ms if the host responds to ICMP echo, else None."""
    cmd = _ping_command(ip, timeout_s)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout_s + 2)
        except asyncio.TimeoutError:
            proc.kill()
            return None
    except (OSError, FileNotFoundError):
        return None

    if proc.returncode != 0:
        return None

    text = stdout.decode(errors="ignore")
    match = re.search(r"time[=<]([\d.]+)\s*ms", text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    # Responded but latency not parsed (platform formatting difference)
    return 0.0


async def _tcp_probe(ip: str, timeout_s: float) -> bool:
    """Try connecting to a handful of common ports; success => host is up."""
    for port in _PROBE_PORTS:
        try:
            conn = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout_s)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError):
            # Refused still proves the host is up (something answered)
            if isinstance(_last_exc(), ConnectionRefusedError):
                return True
            continue
        except OSError:
            continue
    return False


def _last_exc():
    import sys
    return sys.exc_info()[1]


def _get_arp_table() -> dict:
    """Best-effort parse of the system ARP table -> {ip: mac}."""
    system = platform.system().lower()
    table = {}
    try:
        if system == "windows":
            out = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5).stdout
            for line in out.splitlines():
                m = re.match(r"\s*(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17})", line)
                if m:
                    table[m.group(1)] = m.group(2).replace("-", ":").upper()
        else:
            out = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5).stdout
            for line in out.splitlines():
                m = re.search(r"\(([\d.]+)\)\s+at\s+([0-9a-fA-F:]{17})", line)
                if m:
                    table[m.group(1)] = m.group(2).upper()
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass
    return table


async def discover_host(ip: str, timeout_s: float = 1.0) -> HostResult:
    """Run ICMP, then TCP-probe fallback, against a single host."""
    latency = await _icmp_ping(ip, timeout_s)
    if latency is not None:
        return HostResult(ip=ip, is_up=True, latency_ms=latency, discovery_method="icmp")

    tcp_up = await _tcp_probe(ip, timeout_s)
    if tcp_up:
        return HostResult(ip=ip, is_up=True, discovery_method="tcp-probe")

    return HostResult(ip=ip, is_up=False, discovery_method=None)


async def discover_hosts(
    ips: List[str],
    timeout_s: float = 1.0,
    max_concurrency: int = 100,
    progress_callback=None,
) -> List[HostResult]:
    """Discover liveness for a list of IPs concurrently, bounded by a semaphore."""
    semaphore = asyncio.Semaphore(max_concurrency)
    results: List[HostResult] = []
    completed = 0
    total = len(ips)

    async def _run(ip: str):
        nonlocal completed
        async with semaphore:
            result = await discover_host(ip, timeout_s)
        completed += 1
        if progress_callback:
            progress_callback(completed, total)
        return result

    tasks = [_run(ip) for ip in ips]
    results = await asyncio.gather(*tasks)

    # Enrich with ARP/MAC info for hosts found up (best-effort, local segment only)
    arp_table = _get_arp_table()
    for r in results:
        if r.is_up and r.ip in arp_table:
            r.mac = arp_table[r.ip]

    return list(results)
