"""
port_database.py
-----------------
Static reference data: common ports, service name mappings, and a small
MAC-address OUI (vendor) prefix table. This is reference data only — it
never fabricates a result, it just supplies the labels used when a scan
actually observes something.
"""

# Default TCP ports scanned when the user does not specify --ports
DEFAULT_TCP_PORTS = [
    20, 21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143,
    443, 445, 465, 587, 993, 995, 1433, 1521, 3306, 3389,
    5432, 5900, 6379, 8080, 8443,
]

# Default UDP ports scanned with --udp
DEFAULT_UDP_PORTS = [
    53, 67, 68, 69, 123, 137, 138, 161, 500, 514, 1900, 4500, 5353,
]

# Port -> (service name, common full name) used as a fallback label.
# This is NOT proof of what's actually running — it's overridden by
# real banner/protocol detection whenever that succeeds.
TCP_SERVICE_MAP = {
    20: ("ftp-data", "FTP Data"),
    21: ("ftp", "FTP"),
    22: ("ssh", "SSH"),
    23: ("telnet", "Telnet"),
    25: ("smtp", "SMTP"),
    53: ("dns", "DNS"),
    80: ("http", "HTTP"),
    110: ("pop3", "POP3"),
    111: ("rpcbind", "RPC Bind"),
    135: ("msrpc", "Microsoft RPC"),
    139: ("netbios-ssn", "NetBIOS Session Service"),
    143: ("imap", "IMAP"),
    443: ("https", "HTTPS"),
    445: ("microsoft-ds", "Microsoft-DS / SMB"),
    465: ("smtps", "SMTP over SSL"),
    587: ("submission", "SMTP Submission"),
    993: ("imaps", "IMAP over SSL"),
    995: ("pop3s", "POP3 over SSL"),
    1433: ("ms-sql-s", "Microsoft SQL Server"),
    1521: ("oracle", "Oracle DB"),
    3306: ("mysql", "MySQL"),
    3389: ("ms-wbt-server", "RDP"),
    5432: ("postgresql", "PostgreSQL"),
    5900: ("vnc", "VNC"),
    6379: ("redis", "Redis"),
    8080: ("http-proxy", "HTTP Alternate"),
    8443: ("https-alt", "HTTPS Alternate"),
}

UDP_SERVICE_MAP = {
    53: ("dns", "DNS"),
    67: ("dhcps", "DHCP Server"),
    68: ("dhcpc", "DHCP Client"),
    69: ("tftp", "TFTP"),
    123: ("ntp", "NTP"),
    137: ("netbios-ns", "NetBIOS Name Service"),
    138: ("netbios-dgm", "NetBIOS Datagram Service"),
    161: ("snmp", "SNMP"),
    500: ("isakmp", "IPsec/ISAKMP"),
    514: ("syslog", "Syslog"),
    1900: ("ssdp", "SSDP/UPnP"),
    4500: ("ipsec-nat-t", "IPsec NAT Traversal"),
    5353: ("mdns", "Multicast DNS"),
}

# Ports strongly associated with Windows hosts (used for OS heuristics only)
WINDOWS_INDICATOR_PORTS = {135, 139, 445, 3389}

# Ports strongly associated with Unix/Linux hosts
UNIX_INDICATOR_PORTS = {22, 111, 2049}

# A small, illustrative OUI prefix -> vendor table.
# NOT exhaustive. Unknown prefixes must be reported as "Unknown" — never guessed.
OUI_VENDOR_MAP = {
    "00:1A:2B": "Cisco",
    "00:1B:63": "Apple",
    "3C:5A:B4": "Google",
    "B8:27:EB": "Raspberry Pi Foundation",
    "DC:A6:32": "Raspberry Pi Foundation",
    "F0:9F:C2": "Ubiquiti Networks",
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "08:00:27": "Oracle VirtualBox",
    "AC:DE:48": "Intel",
    "F4:F5:D8": "Google",
    "00:1E:C2": "Apple",
    "E0:63:DA": "TP-Link",
    "50:C7:BF": "TP-Link",
}


def get_tcp_service(port: int):
    return TCP_SERVICE_MAP.get(port, ("unknown", "Unknown"))


def get_udp_service(port: int):
    return UDP_SERVICE_MAP.get(port, ("unknown", "Unknown"))


def get_vendor_from_mac(mac: str) -> str:
    if not mac:
        return "Unknown"
    prefix = mac.upper()[:8]
    return OUI_VENDOR_MAP.get(prefix, "Unknown")
