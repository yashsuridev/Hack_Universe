"""
service_detector.py
--------------------
Lightweight, non-intrusive service and version detection for open TCP
ports: banner grabbing, minimal HTTP HEAD/GET probing, and pattern
matching against known banner formats. No exploitation, no authentication
attempts, no fuzzing. When a version can't be reasonably determined, it is
always reported as "Unknown" — never guessed.
"""

import asyncio
import re
import ssl
from dataclasses import dataclass, field
from typing import Optional

from utils.port_database import get_tcp_service

_BANNER_READ_BYTES = 1024
_BANNER_TIMEOUT = 2.0

# Ports where the server speaks first (banner appears immediately on connect)
_SERVER_SPEAKS_FIRST = {21, 22, 25, 110, 143, 3306}

# Ports treated as HTTP for lightweight HTTP probing
_HTTP_PORTS = {80, 8080, 8000, 8888}
_HTTPS_PORTS = {443, 8443}


@dataclass
class ServiceInfo:
    service: str
    version: str = "Unknown"
    banner: Optional[str] = None
    http_server: Optional[str] = None
    http_version: Optional[str] = None
    http_status: Optional[int] = None
    http_title: Optional[str] = None


async def _grab_banner(ip: str, port: int, timeout_s: float = _BANNER_TIMEOUT) -> Optional[str]:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout_s
        )
    except (asyncio.TimeoutError, OSError):
        return None

    try:
        if port in _SERVER_SPEAKS_FIRST:
            try:
                data = await asyncio.wait_for(reader.read(_BANNER_READ_BYTES), timeout=timeout_s)
            except asyncio.TimeoutError:
                data = b""
        else:
            # Send a harmless newline to try to prompt a response
            try:
                writer.write(b"\r\n")
                await writer.drain()
                data = await asyncio.wait_for(reader.read(_BANNER_READ_BYTES), timeout=timeout_s)
            except (asyncio.TimeoutError, OSError):
                data = b""
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

    if not data:
        return None
    try:
        return data.decode(errors="ignore").strip()
    except Exception:
        return None


def _parse_banner_version(banner: str) -> ServiceInfo:
    """Match common banner formats to extract product/version, never inventing values."""
    if not banner:
        return ServiceInfo(service="unknown")

    patterns = [
        (r"^SSH-[\d.]+-(OpenSSH)[_-]([\w.]+)", "ssh"),
        (r"^220[ -].*?(vsFTPd)\s+([\d.]+)", "ftp"),
        (r"^220[ -].*?(ProFTPD)\s+([\d.]+)", "ftp"),
        (r"^220[ -].*?(Pure-FTPd)", "ftp"),
        (r"(Microsoft ESMTP MAIL Service)", "smtp"),
        (r"^220[ -].*?(Postfix)", "smtp"),
        (r"\+OK.*?(Dovecot)", "pop3"),
        (r"(MySQL)", "mysql"),
        (r"(Redis)", "redis"),
    ]

    for pattern, service in patterns:
        match = re.search(pattern, banner, re.IGNORECASE)
        if match:
            groups = match.groups()
            product = groups[0] if groups else service
            version = groups[1] if len(groups) > 1 else "Unknown"
            return ServiceInfo(service=service, version=version or "Unknown", banner=banner)

    return ServiceInfo(service="unknown", version="Unknown", banner=banner)


async def _http_probe(ip: str, port: int, use_tls: bool, timeout_s: float = _BANNER_TIMEOUT) -> ServiceInfo:
    info = ServiceInfo(service="https" if use_tls else "http")
    try:
        if use_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port, ssl=ctx), timeout=timeout_s
            )
        else:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), timeout=timeout_s
            )
    except (asyncio.TimeoutError, OSError, ssl.SSLError):
        return info

    try:
        request = (
            f"GET / HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: python-network-scanner/1.0\r\n"
            f"Connection: close\r\n\r\n"
        ).encode()
        writer.write(request)
        try:
            await writer.drain()
            raw = await asyncio.wait_for(reader.read(8192), timeout=timeout_s)
        except (asyncio.TimeoutError, OSError):
            raw = b""
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

    if not raw:
        return info

    text = raw.decode(errors="ignore")
    status_match = re.match(r"HTTP/(\d\.\d)\s+(\d+)", text)
    if status_match:
        info.http_version = status_match.group(1)
        info.http_status = int(status_match.group(2))

    server_match = re.search(r"^Server:\s*(.+)$", text, re.IGNORECASE | re.MULTILINE)
    if server_match:
        info.http_server = server_match.group(1).strip()

    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if title_match:
        info.http_title = re.sub(r"\s+", " ", title_match.group(1)).strip()[:120]

    if info.http_server:
        product_match = re.match(r"([A-Za-z\-]+)/?([\d.]+)?", info.http_server)
        if product_match:
            info.version = product_match.group(2) or "Unknown"

    return info


async def detect_service(ip: str, port: int, timeout_s: float = _BANNER_TIMEOUT) -> ServiceInfo:
    """Best-effort service/version identification for a single open TCP port."""
    fallback_name, fallback_full = get_tcp_service(port)

    if port in _HTTP_PORTS:
        info = await _http_probe(ip, port, use_tls=False, timeout_s=timeout_s)
        if not info.http_server and not info.http_status:
            info.service = fallback_name
        return info

    if port in _HTTPS_PORTS:
        info = await _http_probe(ip, port, use_tls=True, timeout_s=timeout_s)
        if not info.http_server and not info.http_status:
            info.service = fallback_name
        return info

    banner = await _grab_banner(ip, port, timeout_s=timeout_s)
    if banner:
        parsed = _parse_banner_version(banner)
        if parsed.service == "unknown":
            parsed.service = fallback_name
        return parsed

    return ServiceInfo(service=fallback_name, version="Unknown")
