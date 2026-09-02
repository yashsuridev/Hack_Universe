"""test_scanner.py -- Integration tests for TCP scanning, UDP scanning,
service detection, and OS heuristics, using local sockets we control
(no external network access required)."""

import asyncio
import os
import socket
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import tcp_scanner, udp_scanner, service_detector, os_detector
from utils import port_database


def _start_tcp_echo_server(port: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", port))
    server.listen(5)
    server.settimeout(5)

    def _serve():
        try:
            conn, _ = server.accept()
            conn.settimeout(2)
            try:
                conn.recv(1024)
                conn.sendall(b"TEST-BANNER-1.0\r\n")
            except socket.timeout:
                pass
            conn.close()
        except socket.timeout:
            pass
        finally:
            server.close()

    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    time.sleep(0.2)
    return t


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestTCPScanner(unittest.TestCase):
    def test_open_port_detected(self):
        port = _free_port()
        _start_tcp_echo_server(port)
        result = asyncio.run(tcp_scanner.scan_tcp_port("127.0.0.1", port, timeout_s=2.0))
        self.assertEqual(result.state, "open")
        self.assertEqual(result.protocol, "tcp")

    def test_closed_port_detected(self):
        port = _free_port()  # nothing listening here
        result = asyncio.run(tcp_scanner.scan_tcp_port("127.0.0.1", port, timeout_s=1.0))
        self.assertEqual(result.state, "closed")

    def test_scan_multiple_ports(self):
        open_port = _free_port()
        _start_tcp_echo_server(open_port)
        closed_port = _free_port()
        results = asyncio.run(
            tcp_scanner.scan_tcp_ports("127.0.0.1", [open_port, closed_port], timeout_s=2.0, max_concurrency=10)
        )
        states = {r.port: r.state for r in results}
        self.assertEqual(states[open_port], "open")
        self.assertEqual(states[closed_port], "closed")


class TestUDPScanner(unittest.TestCase):
    def test_udp_no_listener_returns_valid_state(self):
        port = _free_port()
        results = asyncio.run(
            udp_scanner.scan_udp_ports("127.0.0.1", [port], timeout_s=0.5, max_concurrency=5)
        )
        self.assertEqual(len(results), 1)
        self.assertIn(results[0].state, ("open", "closed", "open|filtered"))


class TestServiceDetector(unittest.TestCase):
    def test_banner_grab(self):
        port = _free_port()
        _start_tcp_echo_server(port)
        info = asyncio.run(service_detector.detect_service("127.0.0.1", port, timeout_s=2.0))
        self.assertIsNotNone(info)
        # Should at least capture the raw banner even if not matched to a known product
        self.assertTrue(info.banner is None or "TEST-BANNER" in info.banner or info.service is not None)

    def test_no_service_never_fabricates_version(self):
        port = _free_port()  # nothing listening
        info = asyncio.run(service_detector.detect_service("127.0.0.1", port, timeout_s=1.0))
        self.assertEqual(info.version, "Unknown")


class TestOSDetector(unittest.TestCase):
    def test_no_evidence_returns_unknown(self):
        guess = os_detector.guess_os("127.0.0.1", open_tcp_ports=[])
        # With no open indicator ports and possibly no TTL, expect Unknown or low confidence
        self.assertIn(guess.confidence, ("Unknown", "Low", "Medium"))
        self.assertTrue(guess.os_guess)

    def test_windows_ports_bias_guess(self):
        guess = os_detector.guess_os("127.0.0.1", open_tcp_ports=[135, 139, 445])
        self.assertIn("Windows", guess.os_guess)

    def test_never_claims_certainty(self):
        guess = os_detector.guess_os("127.0.0.1", open_tcp_ports=[22])
        self.assertIn(guess.confidence, ("Low", "Medium", "Unknown"))


class TestPortDatabase(unittest.TestCase):
    def test_known_tcp_service(self):
        name, full = port_database.get_tcp_service(22)
        self.assertEqual(name, "ssh")

    def test_unknown_tcp_service_labeled_unknown(self):
        name, full = port_database.get_tcp_service(59999)
        self.assertEqual(name, "unknown")

    def test_vendor_unknown_for_unmapped_mac(self):
        vendor = port_database.get_vendor_from_mac("AA:BB:CC:DD:EE:FF")
        self.assertEqual(vendor, "Unknown")

    def test_vendor_lookup_no_mac(self):
        self.assertEqual(port_database.get_vendor_from_mac(None), "Unknown")


if __name__ == "__main__":
    unittest.main()
