"""
network_info.py
----------------
Detect local network configuration: interface, local IP, subnet, gateway.
Uses only standard library + optional 'netifaces' if present, with graceful
fallbacks so the tool still works when netifaces is not installed.
"""

import ipaddress
import socket
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

try:
    import netifaces
    _HAS_NETIFACES = True
except ImportError:
    _HAS_NETIFACES = False


@dataclass
class NetworkInfo:
    interface: str
    local_ip: str
    subnet_mask: Optional[str]
    network_cidr: Optional[str]
    gateway: Optional[str]
    mac_address: Optional[str]


def get_local_ip() -> str:
    """Determine the local IP used for outbound traffic (no packets sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect (UDP), just used to pick the right interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def _netifaces_info(local_ip: str) -> NetworkInfo:
    gateway = None
    try:
        gws = netifaces.gateways()
        default_gw = gws.get("default", {}).get(netifaces.AF_INET)
        if default_gw:
            gateway = default_gw[0]
            iface_from_gw = default_gw[1]
        else:
            iface_from_gw = None
    except Exception:
        iface_from_gw = None

    interface = iface_from_gw
    subnet_mask = None
    mac_address = None

    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        inet = addrs.get(netifaces.AF_INET, [])
        for entry in inet:
            if entry.get("addr") == local_ip:
                interface = iface
                subnet_mask = entry.get("netmask")
                link = addrs.get(netifaces.AF_LINK, [])
                if link:
                    mac_address = link[0].get("addr")
                break

    network_cidr = None
    if subnet_mask:
        try:
            iface_net = ipaddress.IPv4Network(f"{local_ip}/{subnet_mask}", strict=False)
            network_cidr = str(iface_net)
        except ValueError:
            network_cidr = None

    return NetworkInfo(
        interface=interface or "unknown",
        local_ip=local_ip,
        subnet_mask=subnet_mask,
        network_cidr=network_cidr,
        gateway=gateway,
        mac_address=mac_address,
    )


def _fallback_info(local_ip: str) -> NetworkInfo:
    """Best-effort network info without netifaces (assumes a /24)."""
    subnet_mask = "255.255.255.0"
    try:
        network_cidr = str(ipaddress.IPv4Network(f"{local_ip}/24", strict=False))
    except ValueError:
        network_cidr = None

    gateway = None
    try:
        if sys.platform.startswith("linux"):
            out = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True, timeout=3
            ).stdout
            parts = out.split()
            if "via" in parts:
                gateway = parts[parts.index("via") + 1]
        elif sys.platform == "darwin":
            out = subprocess.run(
                ["route", "-n", "get", "default"],
                capture_output=True, text=True, timeout=3
            ).stdout
            for line in out.splitlines():
                if "gateway:" in line:
                    gateway = line.split(":")[1].strip()
        elif sys.platform.startswith("win"):
            out = subprocess.run(
                ["ipconfig"], capture_output=True, text=True, timeout=5
            ).stdout
            for line in out.splitlines():
                if "Default Gateway" in line and ":" in line:
                    val = line.split(":")[1].strip()
                    if val:
                        gateway = val
                        break
    except Exception:
        gateway = None

    return NetworkInfo(
        interface="default",
        local_ip=local_ip,
        subnet_mask=subnet_mask,
        network_cidr=network_cidr,
        gateway=gateway,
        mac_address=None,
    )


def get_network_info() -> NetworkInfo:
    local_ip = get_local_ip()
    if _HAS_NETIFACES:
        try:
            return _netifaces_info(local_ip)
        except Exception:
            pass
    return _fallback_info(local_ip)
