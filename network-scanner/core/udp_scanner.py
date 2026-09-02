"""
udp_scanner.py
--------------
UDP scanning. UDP is connectionless, so results are inherently less
definitive than TCP:

  OPEN            - a response was received (rare unless the protocol
                     replies to an empty/garbage probe, e.g. DNS, NTP, SNMP)
  CLOSED          - an ICMP Port Unreachable was received
  OPEN|FILTERED   - no response at all (most common outcome; a firewall
                     silently dropping the probe looks identical to an
                     open port that doesn't answer garbage input)

This module intentionally does NOT claim certainty for the common
no-response case.
"""

import asyncio
import socket
from dataclasses import dataclass
from typing import List

# Minimal protocol-appropriate probes for services likely to respond.
# Sending nothing/garbage on other ports usually yields OPEN|FILTERED,
# which is documented and expected.
_PROBES = {
    53: b"\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00",  # partial DNS query
    123: b"\x1b" + 47 * b"\x00",  # NTP client request
    161: b"\x30\x26\x02\x01\x01\x04\x06public\xa0\x19\x02\x04\x00\x00\x00\x00"
         b"\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x05\x00",
}


@dataclass
class UDPPortResult:
    port: int
    protocol: str
    state: str  # open | closed | open|filtered


def _scan_one_udp(ip: str, port: int, timeout_s: float) -> UDPPortResult:
    probe = _PROBES.get(port, b"\x00")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout_s)
    try:
        sock.sendto(probe, (ip, port))
        try:
            sock.recvfrom(1024)
            return UDPPortResult(port=port, protocol="udp", state="open")
        except socket.timeout:
            return UDPPortResult(port=port, protocol="udp", state="open|filtered")
        except ConnectionResetError:
            # Windows raises this on ICMP port-unreachable for UDP sockets
            return UDPPortResult(port=port, protocol="udp", state="closed")
    except OSError as exc:
        # ICMP port unreachable surfaces as ECONNREFUSED on Linux
        if getattr(exc, "errno", None) == 111:  # ECONNREFUSED
            return UDPPortResult(port=port, protocol="udp", state="closed")
        return UDPPortResult(port=port, protocol="udp", state="open|filtered")
    finally:
        sock.close()


async def scan_udp_ports(
    ip: str,
    ports: List[int],
    timeout_s: float = 1.5,
    max_concurrency: int = 50,
    progress_callback=None,
) -> List[UDPPortResult]:
    """UDP sockets aren't natively async-friendly; run via a thread pool."""
    loop = asyncio.get_event_loop()
    semaphore = asyncio.Semaphore(max_concurrency)
    completed = 0
    total = len(ports)

    async def _run(port: int):
        nonlocal completed
        async with semaphore:
            result = await loop.run_in_executor(None, _scan_one_udp, ip, port, timeout_s)
        completed += 1
        if progress_callback:
            progress_callback(completed, total)
        return result

    tasks = [_run(p) for p in ports]
    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda r: r.port)
