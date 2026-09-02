#!/usr/bin/env python3
"""
scanner.py
----------
Python Network Scanner - an Nmap-inspired host discovery & port scanning
tool implemented from scratch in Python.

SAFETY NOTICE
=============
This scanner is intended only for networks and systems
you own or have explicit permission to test.

Do not use this tool against systems you do not own or lack
explicit authorization to test. Unauthorized scanning of networks
may be illegal in your jurisdiction.
"""

import argparse
import asyncio
import ipaddress
import re
import sys
import time

from core import discovery, tcp_scanner, udp_scanner, service_detector, os_detector, network_info
from output import formatter, json_exporter, csv_exporter, html_report
from utils import validators, logger as log_module
from utils.port_database import DEFAULT_TCP_PORTS, DEFAULT_UDP_PORTS, get_vendor_from_mac


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scanner.py",
        description="Python Network Scanner - Nmap-inspired host discovery & port scanning.",
        epilog="This scanner is intended only for networks and systems you own or have "
               "explicit permission to test.",
    )
    parser.add_argument("target", nargs="?", default=None,
                         help="Target: IP, comma-separated IPs, CIDR, or hostname.")

    parser.add_argument("--ports", default=None,
                         help="Ports to scan, e.g. '22,80,443' or '1-1000'. Default: common ports.")
    parser.add_argument("--udp", action="store_true", help="Also scan common UDP ports.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Quick scan: discovery + common TCP ports only.")
    mode.add_argument("--comprehensive", action="store_true",
                       help="Comprehensive scan: TCP + UDP + service/version + OS + MAC/vendor.")

    parser.add_argument("--service-detection", action="store_true", help="Force service detection on.")
    parser.add_argument("--os-detection", action="store_true", help="Force OS detection on.")

    parser.add_argument("--timeout", type=float, default=1.0, help="Per-probe timeout in seconds (default: 1.0).")
    parser.add_argument("--workers", type=int, default=100, help="Max concurrent connections (default: 100).")

    parser.add_argument("--output", default=None,
                         help="Export results to a file. Extension determines format: "
                              ".json / .csv / .txt / .html")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose (info-level) logging.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")

    return parser


def resolve_scan_mode(args) -> str:
    if args.quick:
        return "Quick"
    if args.comprehensive:
        return "Comprehensive"
    return "Normal"


def interactive_prompt() -> str:
    print(
        "The scanner operates only against the private\n"
        "network of this computer.\n\n"
        "What would you like me to do?\n\n"
        "Examples:\n"
        "  Scan my home network\n"
        "  Find devices on my network\n"
        "  Check open ports\n"
        "  Analyze my local network\n"
    )
    try:
        text = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return parse_natural_language_target(text)


def parse_natural_language_target(text: str) -> str:
    text_lower = text.lower()
    if (
        "home network" in text_lower
        or "my network" in text_lower
        or "local network" in text_lower
        or "devices on my network" in text_lower
        or "check open ports" in text_lower
        or "analyze" in text_lower
    ):
        info = network_info.get_network_info()
        if info.network_cidr:
            return info.network_cidr
        formatter.print_error("Could not automatically determine local network. Please specify a target.")
        sys.exit(1)
    if "localhost" in text_lower:
        return "localhost"

    # Try to pull an IP/CIDR/hostname-looking token out of free text
    match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3}(?:/\d{1,2})?)", text)
    if match:
        return match.group(1)

    # Fall back to treating the whole (trimmed) input as a target
    cleaned = re.sub(r"^(scan|please scan|can you scan)\s+", "", text_lower).strip()
    return cleaned if cleaned else text


async def scan_single_host(
    ip: str,
    ports: list,
    udp_ports: list,
    args,
    scan_mode: str,
    do_service_detection: bool,
    do_os_detection: bool,
    host_discovery_meta: dict,
    progress=None,
):
    tcp_results = await tcp_scanner.scan_tcp_ports(
        ip, ports, timeout_s=args.timeout, max_concurrency=args.workers
    )

    open_tcp = [r for r in tcp_results if r.state == "open"]

    port_entries = []
    for r in tcp_results:
        entry = {"port": r.port, "protocol": "tcp", "state": r.state,
                 "service": "unknown", "version": "Unknown"}
        port_entries.append(entry)

    if do_service_detection and open_tcp:
        sem = asyncio.Semaphore(args.workers)

        async def _detect(port):
            async with sem:
                return port, await service_detector.detect_service(ip, port, timeout_s=max(args.timeout, 1.5))

        detections = await asyncio.gather(*[_detect(r.port) for r in open_tcp])
        detection_map = {port: info for port, info in detections}
        for entry in port_entries:
            if entry["state"] == "open" and entry["port"] in detection_map:
                info = detection_map[entry["port"]]
                entry["service"] = info.service
                entry["version"] = info.version
                if info.http_server:
                    entry["http_server"] = info.http_server
                if info.http_status is not None:
                    entry["http_status"] = info.http_status
                if info.http_title:
                    entry["http_title"] = info.http_title
    else:
        from utils.port_database import get_tcp_service
        for entry in port_entries:
            if entry["state"] == "open":
                name, _full = get_tcp_service(entry["port"])
                entry["service"] = name

    if udp_ports:
        udp_results = await udp_scanner.scan_udp_ports(
            ip, udp_ports, timeout_s=max(args.timeout, 1.5), max_concurrency=min(args.workers, 50)
        )
        from utils.port_database import get_udp_service
        for r in udp_results:
            name, _full = get_udp_service(r.port)
            port_entries.append({
                "port": r.port, "protocol": "udp", "state": r.state,
                "service": name, "version": "Unknown",
            })

    os_guess_data = None
    if do_os_detection:
        open_port_numbers = [r.port for r in open_tcp]
        os_guess_data = os_detector.guess_os(ip, open_port_numbers)

    meta = host_discovery_meta.get(ip)
    vendor = get_vendor_from_mac(meta.mac) if meta and meta.mac else "Unknown"

    return {
        "ip": ip,
        "status": "up",
        "latency": meta.latency_ms if meta else None,
        "mac": meta.mac if meta else None,
        "vendor": vendor,
        "os_guess": os_guess_data.os_guess if os_guess_data else None,
        "os_confidence": os_guess_data.confidence if os_guess_data else None,
        "os_evidence": os_guess_data.evidence if os_guess_data else [],
        "ports": port_entries,
    }


async def run_scan(args, logger):
    if args.target:
        target_spec = args.target
    else:
        target_spec = interactive_prompt()

    try:
        ip_list = validators.parse_targets(target_spec)
    except validators.ValidationError as exc:
        formatter.print_error(str(exc))
        sys.exit(1)

    scan_mode = resolve_scan_mode(args)

    do_service_detection = args.comprehensive or args.service_detection or (scan_mode == "Normal")
    do_os_detection = args.comprehensive or args.os_detection
    do_udp = args.comprehensive or args.udp
    do_mac_vendor = args.comprehensive

    if args.ports:
        try:
            ports = validators.parse_ports(args.ports)
        except validators.ValidationError as exc:
            formatter.print_error(str(exc))
            sys.exit(1)
    elif args.quick:
        ports = DEFAULT_TCP_PORTS
    else:
        ports = DEFAULT_TCP_PORTS

    udp_ports = DEFAULT_UDP_PORTS if do_udp else []

    formatter.print_banner()

    net_info = None
    if len(ip_list) > 1 or args.comprehensive:
        net_info = network_info.get_network_info()

    formatter.print_scan_header(
        target_spec, scan_mode, interface=net_info.interface if net_info else None
    )
    if net_info and (args.comprehensive or args.verbose):
        formatter.print_network_info(net_info)

    start_time = time.time()

    formatter.print_info(f"Discovering hosts ({len(ip_list)} target(s))...")
    logger.debug(f"Target validated: {len(ip_list)} address(es)")

    discovery_results = await discovery.discover_hosts(
        ip_list, timeout_s=args.timeout, max_concurrency=args.workers
    )
    formatter.print_discovery_results(discovery_results)

    up_hosts = [r for r in discovery_results if r.is_up]
    host_meta = {r.ip: r for r in discovery_results}

    if not up_hosts:
        formatter.print_error("No hosts responded. Nothing further to scan.")
        duration = time.time() - start_time
        summary = {
            "target": target_spec, "hosts_scanned": len(ip_list), "hosts_discovered": 0,
            "hosts_with_open_ports": 0, "total_open_ports": 0, "duration_s": duration,
            "host_open_ports": {},
        }
        formatter.print_summary(summary)
        return {"target": target_spec, "hosts_scanned": len(ip_list), "hosts_discovered": 0,
                "duration_s": duration, "hosts": []}

    host_reports = []
    for idx, host in enumerate(up_hosts, start=1):
        formatter.print_info(f"Scanning {host.ip} ({idx}/{len(up_hosts)})...")
        logger.debug(f"TCP scan started for {host.ip}")
        report = await scan_single_host(
            host.ip, ports, udp_ports, args, scan_mode,
            do_service_detection, do_os_detection, host_meta
        )
        formatter.print_host_report(report)
        host_reports.append(report)

    duration = time.time() - start_time

    total_open = sum(1 for h in host_reports for p in h["ports"] if p["state"] == "open")
    hosts_with_open = sum(1 for h in host_reports if any(p["state"] == "open" for p in h["ports"]))
    host_open_ports = {
        h["ip"]: [p["port"] for p in h["ports"] if p["state"] == "open"]
        for h in host_reports if any(p["state"] == "open" for p in h["ports"])
    }

    summary = {
        "target": target_spec,
        "hosts_scanned": len(ip_list),
        "hosts_discovered": len(up_hosts),
        "hosts_with_open_ports": hosts_with_open,
        "total_open_ports": total_open,
        "duration_s": duration,
        "host_open_ports": host_open_ports,
    }
    formatter.print_summary(summary)

    return {
        "target": target_spec,
        "hosts_scanned": len(ip_list),
        "hosts_discovered": len(up_hosts),
        "duration_s": duration,
        "hosts": host_reports,
    }


def export_results(scan_data: dict, output_path: str):
    ext = output_path.rsplit(".", 1)[-1].lower() if "." in output_path else ""
    if ext == "json":
        json_exporter.export_json(scan_data, output_path)
    elif ext == "csv":
        csv_exporter.export_csv(scan_data, output_path)
    elif ext == "txt":
        csv_exporter.export_txt(scan_data, output_path)
    elif ext == "html":
        html_report.export_html(scan_data, output_path)
    else:
        formatter.print_error(f"Unsupported output extension '.{ext}'. Use .json, .csv, .txt, or .html.")
        return
    formatter.print_info(f"Results exported to {output_path}")


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    logger = log_module.setup_logger(verbose=args.verbose, debug=args.debug)

    try:
        scan_data = asyncio.run(run_scan(args, logger))
    except KeyboardInterrupt:
        formatter.print_error("Scan interrupted by user (Ctrl+C).")
        sys.exit(130)
    except Exception as exc:
        formatter.print_error(f"Unexpected error: {exc}")
        if args.debug:
            raise
        sys.exit(1)

    if args.output:
        export_results(scan_data, args.output)


if __name__ == "__main__":
    main()
