"""test_ports.py -- Unit tests for port and target validation logic."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import validators


class TestParsePorts(unittest.TestCase):
    def test_single_port(self):
        self.assertEqual(validators.parse_ports("80"), [80])

    def test_multiple_ports(self):
        self.assertEqual(validators.parse_ports("22,80,443"), [22, 80, 443])

    def test_range(self):
        self.assertEqual(validators.parse_ports("1-5"), [1, 2, 3, 4, 5])

    def test_reversed_range(self):
        self.assertEqual(validators.parse_ports("5-1"), [1, 2, 3, 4, 5])

    def test_mixed(self):
        self.assertEqual(validators.parse_ports("22,80,100-102"), [22, 80, 100, 101, 102])

    def test_duplicates_removed(self):
        self.assertEqual(validators.parse_ports("80,80,80"), [80])

    def test_invalid_port_too_high(self):
        with self.assertRaises(validators.ValidationError):
            validators.parse_ports("70000")

    def test_invalid_port_zero(self):
        with self.assertRaises(validators.ValidationError):
            validators.parse_ports("0")

    def test_invalid_non_numeric(self):
        with self.assertRaises(validators.ValidationError):
            validators.parse_ports("abc")

    def test_empty_string(self):
        with self.assertRaises(validators.ValidationError):
            validators.parse_ports("")

    def test_malformed_range(self):
        with self.assertRaises(validators.ValidationError):
            validators.parse_ports("1-2-3")


class TestParseTargets(unittest.TestCase):
    def test_single_ip(self):
        self.assertEqual(validators.parse_targets("192.168.1.1"), ["192.168.1.1"])

    def test_comma_separated(self):
        result = validators.parse_targets("192.168.1.1,192.168.1.2")
        self.assertEqual(result, ["192.168.1.1", "192.168.1.2"])

    def test_localhost(self):
        self.assertEqual(validators.parse_targets("localhost"), ["127.0.0.1"])

    def test_cidr_small(self):
        result = validators.parse_targets("192.168.1.0/30")
        # /30 network has 2 usable hosts
        self.assertEqual(result, ["192.168.1.1", "192.168.1.2"])

    def test_cidr_too_large_rejected(self):
        with self.assertRaises(validators.ValidationError):
            validators.parse_targets("10.0.0.0/8")

    def test_invalid_hostname_raises(self):
        with self.assertRaises(validators.ValidationError):
            validators.parse_targets("this-host-does-not-exist.invalid")

    def test_duplicate_removal_in_list(self):
        result = validators.parse_targets("192.168.1.1,192.168.1.1")
        self.assertEqual(result, ["192.168.1.1"])


class TestIsValid(unittest.TestCase):
    def test_valid_ip(self):
        self.assertTrue(validators.is_valid_ip("10.0.0.1"))

    def test_invalid_ip(self):
        self.assertFalse(validators.is_valid_ip("999.999.999.999"))

    def test_valid_cidr(self):
        self.assertTrue(validators.is_valid_cidr("10.0.0.0/24"))

    def test_invalid_cidr(self):
        self.assertFalse(validators.is_valid_cidr("10.0.0.0/99"))

    def test_is_private(self):
        self.assertTrue(validators.is_private_or_local("192.168.1.5"))
        self.assertTrue(validators.is_private_or_local("10.0.0.5"))
        self.assertTrue(validators.is_private_or_local("127.0.0.1"))
        self.assertFalse(validators.is_private_or_local("8.8.8.8"))


if __name__ == "__main__":
    unittest.main()
