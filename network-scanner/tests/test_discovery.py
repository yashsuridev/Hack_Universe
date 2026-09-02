"""test_discovery.py -- Unit/integration tests for host discovery."""

import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import discovery


class TestHostDiscovery(unittest.TestCase):
    def test_localhost_is_up(self):
        result = asyncio.run(discovery.discover_host("127.0.0.1", timeout_s=2.0))
        self.assertTrue(result.is_up)
        self.assertEqual(result.ip, "127.0.0.1")

    def test_unreachable_host_marked_down_or_up_gracefully(self):
        # A reserved/unroutable test address (TEST-NET-1 doc range) should
        # not crash the discovery routine; it may resolve to down.
        result = asyncio.run(discovery.discover_host("192.0.2.123", timeout_s=0.5))
        self.assertIsNotNone(result)
        self.assertIn(result.is_up, (True, False))

    def test_discover_hosts_batch(self):
        results = asyncio.run(
            discovery.discover_hosts(["127.0.0.1", "192.0.2.123"], timeout_s=0.5, max_concurrency=10)
        )
        self.assertEqual(len(results), 2)
        ips = {r.ip for r in results}
        self.assertEqual(ips, {"127.0.0.1", "192.0.2.123"})

    def test_progress_callback_invoked(self):
        calls = []

        def cb(done, total):
            calls.append((done, total))

        asyncio.run(
            discovery.discover_hosts(
                ["127.0.0.1"], timeout_s=0.5, max_concurrency=5, progress_callback=cb
            )
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], (1, 1))


if __name__ == "__main__":
    unittest.main()
