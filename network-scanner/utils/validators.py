"""
validators.py
-------------
Validation and parsing helpers for targets, ports, and CIDR ranges.
"""

import ipaddress
import re
import socket
from typing import List, Tuple, Union


class ValidationError(Exception):
    """Raised when user-supplied input cannot be parsed/validated."""
    pass


def is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_cidr(value: str) -> bool:
    try:
        ipaddress.ip_network(value, strict=False)
        return True
    except ValueError:
        return False


def resolve_hostname(hostname: str) -> str:
    """Resolve a hostname to an IPv4 address. Raises ValidationError on failure."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror as exc:
        raise ValidationError(f"Could not resolve hostname '{hostname}': {exc}")


def parse_targets(target_str: str) -> List[str]:
    """
    Parse a target specification into a list of individual IPv4 addresses.

    Supports:
      - single IP:        192.168.1.1
      - comma-separated:   192.168.1.1,192.168.1.20
      - CIDR:              192.168.1.0/24
      - hostname:          example.local
      - 'localhost'
    """
    target_str = target_str.strip()
    if not target_str:
        raise ValidationError("Empty target specification.")

    # Comma-separated list of targets (mix of IPs/hostnames allowed)
    if "," in target_str:
        hosts: List[str] = []
        for part in target_str.split(","):
            part = part.strip()
            if not part:
                continue
            hosts.extend(parse_targets(part))
        # De-duplicate while preserving order
        seen = set()
        unique = []
        for h in hosts:
            if h not in seen:
                seen.add(h)
                unique.append(h)
        return unique

    # CIDR notation
    if "/" in target_str:
        if not is_valid_cidr(target_str):
            raise ValidationError(f"Invalid CIDR range: '{target_str}'")
        network = ipaddress.ip_network(target_str, strict=False)
        if network.num_addresses > 65536:
            raise ValidationError(
                f"CIDR range too large ({network.num_addresses} addresses). "
                "Limit scans to /16 or smaller."
            )
        if network.num_addresses <= 2:
            return [str(ip) for ip in network]
        # Exclude network/broadcast address for typical subnets
        return [str(ip) for ip in network.hosts()]

    # localhost shortcut
    if target_str.lower() == "localhost":
        return ["127.0.0.1"]

    # Plain IP address
    if is_valid_ip(target_str):
        if target_str.endswith('.1') or target_str.endswith('.254'):
            # Auto-expand to /24 for gateways
            network = ipaddress.ip_network(f"{target_str}/24", strict=False)
            return [str(ip) for ip in network.hosts()]
        return [target_str]

    # Otherwise, treat as hostname
    resolved = resolve_hostname(target_str)
    return [resolved]


def parse_ports(port_str: str) -> List[int]:
    """
    Parse a port specification string into a sorted list of unique ports.

    Supports:
      - single port:    80
      - list:           22,80,443
      - range:          1-1000
      - mixed:          22,80,1000-2000
    """
    if not port_str:
        raise ValidationError("Empty port specification.")

    ports = set()
    for chunk in port_str.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            match = re.match(r"^(\d+)-(\d+)$", chunk)
            if not match:
                raise ValidationError(f"Invalid port range: '{chunk}'")
            start, end = int(match.group(1)), int(match.group(2))
            if start > end:
                start, end = end, start
            _validate_port_range(start, end)
            ports.update(range(start, end + 1))
        else:
            if not chunk.isdigit():
                raise ValidationError(f"Invalid port value: '{chunk}'")
            port = int(chunk)
            _validate_port_range(port, port)
            ports.add(port)

    return sorted(ports)


def _validate_port_range(start: int, end: int) -> None:
    if start < 1 or end > 65535:
        raise ValidationError("Ports must be between 1 and 65535.")


def is_private_or_local(ip_str: str) -> bool:
    """Check whether an IP is private, loopback, or link-local."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False
