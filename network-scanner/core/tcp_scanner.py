"""
tcp_scanner.py
--------------
TCP Connect scanning using asyncio, with bounded concurrency.

Classifies ports as:
  OPEN     - connection succeeded
  CLOSED   - connection actively refused (RST)
  FILTERED - no response within timeout (likely dropped by a firewall)
  UNKNOWN  - an unexpected error occurred
"""

import asyncio
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PortResult:
    port: int
    protocol: str
    state: str  # open | closed | filtered | unknown


async def scan_tcp_port(ip: str, port: int, timeout_s: float = 1.0) -> PortResult:
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout_s)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return PortResult(port=port, protocol="tcp", state="open")
    except asyncio.TimeoutError:
        return PortResult(port=port, protocol="tcp", state="filtered")
    except ConnectionRefusedError:
        return PortResult(port=port, protocol="tcp", state="closed")
    except OSError:
        return PortResult(port=port, protocol="tcp", state="filtered")
    except Exception:
        return PortResult(port=port, protocol="tcp", state="unknown")


async def scan_tcp_ports(
    ip: str,
    ports: List[int],
    timeout_s: float = 1.0,
    max_concurrency: int = 100,
    progress_callback=None,
) -> List[PortResult]:
    semaphore = asyncio.Semaphore(max_concurrency)
    completed = 0
    total = len(ports)

    async def _run(port: int):
        nonlocal completed
        async with semaphore:
            result = await scan_tcp_port(ip, port, timeout_s)
        completed += 1
        if progress_callback:
            progress_callback(completed, total)
        return result

    tasks = [_run(p) for p in ports]
    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda r: r.port)
