# Python Network Scanner

An Nmap-inspired network discovery and port-scanning tool, implemented
from scratch in Python (no `subprocess` calls to `nmap`).

> **⚠️ Legal & Ethical Use**
> This scanner is intended **only** for networks and systems you own or
> have **explicit permission** to test. Unauthorized scanning of networks
> you do not control may be illegal in your jurisdiction (e.g., under the
> U.S. Computer Fraud and Abuse Act, the UK Computer Misuse Act, or
> similar laws elsewhere). You are solely responsible for how you use
> this tool. It performs discovery and enumeration only — it contains no
> exploitation, credential-attack, evasion, or denial-of-service
> capability.

---

## 1. Overview

The scanner discovers live hosts on a network, scans TCP/UDP ports,
identifies running services and (where possible) their versions, makes a
low-confidence guess at the target's OS family, and reports MAC/vendor
information for local-segment hosts. Results can be viewed in a styled
terminal dashboard or exported to JSON, CSV, TXT, or HTML.

Every result the tool reports is either:
- **observed directly** from a real probe (a socket connecting, a banner
  received, an HTTP response parsed), or
- **explicitly labeled** `Unknown` / `Unclassified` when it can't be
  determined.

Nothing is guessed and presented as fact.

## 2. Features

- Host discovery via ICMP ping (subprocess-based, no raw sockets/root
  required) with a TCP-connect fallback for hosts that block ICMP
- ARP-table lookups for MAC addresses on the local segment
- TCP Connect scanning (open / closed / filtered / unknown) using
  `asyncio` with bounded concurrency
- Optional UDP scanning (open / closed / open|filtered)
- Lightweight service/banner detection (SSH, FTP, SMTP, MySQL, Redis,
  etc.) and minimal HTTP/HTTPS probing (server header, status, title)
- Basic passive OS fingerprinting (TTL + indicator ports), always
  reported with a confidence level, never certainty
- MAC vendor lookup from a small built-in OUI table
- Four scan profiles: quick / normal / comprehensive / custom port scan
- Rich terminal dashboard (tables, panels, colorized states) via the
  `rich` library, with a plain-text fallback if `rich` isn't installed
- Export to JSON, CSV, TXT, and self-contained HTML report
- Cross-platform (Windows / Linux / macOS), with platform-specific
  `ping`/ARP handling
- Interactive mode with basic natural-language target parsing
  ("scan my home network")

## 3. Architecture

```
network_scanner/
│
├── scanner.py                 # CLI entry point / orchestrator
├── requirements.txt
├── README.md
│
├── core/
│   ├── discovery.py            # ICMP / TCP-probe / ARP host discovery
│   ├── tcp_scanner.py          # asyncio TCP connect scanning
│   ├── udp_scanner.py          # UDP scanning (thread-pool based)
│   ├── service_detector.py     # banner grabbing + HTTP probing
│   ├── os_detector.py          # TTL + port-based OS heuristics
│   └── network_info.py         # local interface/gateway/subnet detection
│
├── output/
│   ├── formatter.py             # rich terminal dashboard
│   ├── json_exporter.py
│   ├── csv_exporter.py          # also provides the TXT exporter
│   └── html_report.py
│
├── utils/
│   ├── port_database.py         # default ports, service names, OUI table
│   ├── validators.py            # target/port parsing & validation
│   └── logger.py                # --verbose / --debug logging
│
└── tests/
    ├── test_scanner.py          # TCP/UDP scan + service/OS detection tests
    ├── test_discovery.py        # host discovery tests
    └── test_ports.py            # input validation tests
```

### Internal pipeline

```
Target Validation
      ↓
Host Discovery        (ICMP → TCP-probe fallback → ARP enrichment)
      ↓
Port Scanning          (TCP concurrently, UDP optionally)
      ↓
Service Detection      (banner grab / HTTP probe on open ports)
      ↓
Version Detection       (pattern-matched from banners/headers)
      ↓
OS Fingerprinting       (TTL + indicator ports, confidence-scored)
      ↓
Result Aggregation      (per-host report objects)
      ↓
Report Generation       (terminal dashboard + optional file export)
```

Each stage only runs on the data that survived the previous stage — e.g.
service detection only runs against ports the TCP scanner found `open`,
and OS fingerprinting only uses ports actually observed to be open on
that specific host.

## 4. Installation

```bash
git clone <this-repo>
cd network_scanner
pip install -r requirements.txt
```

### Dependencies

- Python 3.8+
- `rich` — terminal dashboard (optional; falls back to plain text)
- `netifaces` — accurate local interface/gateway detection (optional;
  falls back to a best-effort method using `ip route` / `route` /
  `ipconfig`)

### Windows setup

- Install Python 3.8+ from python.org (ensure "Add to PATH" is checked)
- `pip install -r requirements.txt`
- The built-in `ping` and `arp -a` commands are used automatically
- No administrator privileges are required for TCP/UDP scanning; ICMP
  ping uses the standard Windows `ping.exe` utility

### Linux setup

- Python 3.8+ (`sudo apt install python3 python3-pip` on Debian/Ubuntu)
- `pip3 install -r requirements.txt`
- ICMP ping uses the system `ping` binary; on most modern distros this
  works without root because it's setuid or uses `SOCK_DGRAM` ICMP under
  the hood — if your distro restricts it, TCP-probe discovery is used as
  a fallback automatically

### macOS setup

- Python 3.8+ (via python.org or Homebrew: `brew install python3`)
- `pip3 install -r requirements.txt`
- Uses the system `ping` and `arp -a` / `route -n get default`

## 5. Usage Examples

```bash
# Single IP, default (normal) scan
python scanner.py 192.168.1.1

# Multiple IPs
python scanner.py 192.168.1.1,192.168.1.20,192.168.1.30

# Full subnet
python scanner.py 192.168.1.0/24

# Hostname
python scanner.py example.local

# Specific port range
python scanner.py 192.168.1.81 --ports 1-1000

# Specific ports
python scanner.py 192.168.1.1 --ports 22,80,443

# Force service detection
python scanner.py 192.168.1.1 --service-detection

# Force OS detection
python scanner.py 192.168.1.1 --os-detection

# Include UDP scanning
python scanner.py 192.168.1.1 --udp

# Comprehensive scan (TCP + UDP + services + versions + OS + MAC/vendor)
python scanner.py 192.168.1.1 --comprehensive

# Export results
python scanner.py 192.168.1.0/24 --output scan.json
python scanner.py 192.168.1.0/24 --output scan.html

# Tune performance
python scanner.py 192.168.1.0/24 --timeout 1 --workers 100

# Interactive mode (no target given)
python scanner.py
```

## 6. Scan Modes

| Mode              | Flag               | Includes                                                        |
|-------------------|---------------------|-------------------------------------------------------------------|
| Quick              | `--quick`            | Host discovery + common TCP ports                                  |
| Normal (default)  | *(none)*             | Host discovery + common TCP ports + service detection              |
| Comprehensive      | `--comprehensive`    | + UDP scan + version detection + OS detection + MAC/vendor lookup  |
| Custom port scan   | `--ports <spec>`     | Any of the above, restricted/expanded to the ports you specify     |

## 7. Output Examples

Terminal (abbreviated):

```
Host: 192.168.1.81
Status: UP
Latency: 2.31 ms
OS Guess: Likely Windows (Medium)

PORT      STATE      SERVICE       VERSION
-------------------------------------------------------
22/tcp    closed     ssh
80/tcp    open       http          Apache
443/tcp   open       https         nginx
3389/tcp  open       ms-wbt-server

Open ports: 3
```

JSON:

```json
{
  "target": "192.168.1.81",
  "status": "up",
  "os_guess": "Likely Windows",
  "os_confidence": "Medium",
  "ports": [
    {
      "port": 80,
      "protocol": "tcp",
      "state": "open",
      "service": "http",
      "version": "Unknown"
    }
  ]
}
```

## 8. Permission Requirements

- **No root/administrator privileges are required** for TCP connect
  scanning, UDP scanning, or banner grabbing — everything uses standard
  user-space sockets.
- ICMP discovery shells out to the OS's own `ping` utility, which is
  already correctly privileged by the OS installer (setuid on Linux,
  built-in on Windows/macOS) — the scanner itself never needs elevated
  rights for this.
- If a step can't run with your current permissions (e.g. ARP table
  access restricted by OS policy), the tool degrades gracefully and
  explains why in `--verbose`/`--debug` output rather than failing
  silently.

## 9. Legal / Ethical Usage

Only scan:
- `localhost` / `127.0.0.1`
- Private IPv4 ranges you control (`10.0.0.0/8`, `172.16.0.0/12`,
  `192.168.0.0/16`)
- Systems for which you have explicit, documented authorization to test

Do not use this tool to scan networks or hosts you don't own or lack
permission to test. This project intentionally does **not** implement
exploitation, credential attacks, brute forcing, IDS/IPS evasion, or
packet flooding — it is a discovery/enumeration tool only.

## 10. Troubleshooting

| Symptom                                   | Likely cause / fix                                                        |
|---------------------------------------------|-------------------------------------------------------------------------------|
| All hosts show as down on a subnet you know is live | Some networks block ICMP; the TCP-probe fallback should still catch most active hosts — try `--timeout 2` for a slower/less reliable network |
| MAC/vendor always "Unknown"                | MAC info is only available for hosts on your local Ethernet/Wi-Fi segment via the ARP table; remote/routed hosts won't have it |
| `rich` output looks like plain text        | `rich` isn't installed — run `pip install rich`                              |
| Network info (gateway/interface) missing   | `netifaces` isn't installed, or the platform-specific fallback command (`ip route`, `route`, `ipconfig`) isn't available in PATH |
| Scan is slow on a large subnet             | Increase `--workers` (default 100) or reduce the port list with `--ports`     |
| `Permission required` type errors           | These come from the OS, not the scanner — e.g. some minimal Linux containers restrict `ping`; the tool will still attempt TCP-probe discovery |

## 11. Running Tests

```bash
python -m unittest discover -s tests -v
```

Tests use only local loopback sockets and reserved documentation
addresses — no external network access or elevated permissions required.
