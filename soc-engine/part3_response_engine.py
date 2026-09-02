"""Part 3 — Automated Response ("Playbook") Engine

Maps alert types to automated actions. Simulates the action (logs it, no
real firewall needed) and returns an "action_taken" object.

Rules table:
  brute_force        -> block_ip
  c2_beacon          -> isolate_device
  data_exfil         -> quarantine_transfer
  anomaly            -> alert_analyst
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------------
# Playbook rules: alert_type -> (action_name, target_extractor)
# ---------------------------------------------------------------------------

PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "brute_force": {
        "action": "block_ip",
        "target_extractor": lambda evidence: evidence.get("source_ip", "unknown"),
        "severity_map": "high",
        "description": "Block source IP at firewall",
    },
    "c2_beacon": {
        "action": "isolate_device",
        "target_extractor": lambda evidence: evidence.get("source_ip", "unknown"),
        "severity_map": "high",
        "description": "Isolate compromised device from network",
    },
    "data_exfil": {
        "action": "quarantine_transfer",
        "target_extractor": lambda evidence: evidence.get("source_ip", "unknown"),
        "severity_map": "critical",
        "description": "Quarantine outbound data transfer",
    },
    "anomaly": {
        "action": "alert_analyst",
        "target_extractor": lambda evidence: evidence.get("source_ip", "unknown"),
        "severity_map": "medium",
        "description": "Send alert to human analyst queue",
    },
}


# ---------------------------------------------------------------------------
# State tracking for simulated actions (in-memory only)
# ---------------------------------------------------------------------------

class ResponseState:
    """Tracks simulated actions taken — no real network changes."""

    def __init__(self):
        self.actions_taken: List[dict] = []
        self.blocked_ips: set = set()  # simulated blocked IPs
        self.isolated_devices: set = set()

    def record_action(self, action: dict):
        self.actions_taken.append(action)

    def is_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips

    def is_isolated(self, ip: str) -> bool:
        return ip in self.isolated_devices


response_state = ResponseState()


# ---------------------------------------------------------------------------
# Execute playbook action for a given alert
# ---------------------------------------------------------------------------

def execute_playbook(alert: dict) -> dict:
    """
    Look up the alert type in the playbook, execute the mapped action,
    and return an "action_taken" object.

    Returns:
        {
            "action": str,
            "target": str,
            "timestamp": str,
            "status": "completed" | "skipped" | "failed",
        }
    """
    alert_type = alert.get("type", "anomaly")
    rule = PLAYBOOK.get(alert_type, PLAYBOOK["anomaly"])

    action_name = rule["action"]
    target_extractor = rule["target_extractor"]
    target = target_extractor(alert.get("raw_evidence", {}))

    # Simulate action based on type and state
    now = datetime.utcnow().isoformat() + "Z"

    if alert_type == "brute_force":
        ip = target
        if not response_state.is_blocked(ip):
            response_state.blocked_ips.add(ip)
            status = "completed"
        else:
            status = "skipped (already blocked)"

    elif alert_type == "c2_beacon":
        ip = target
        if not response_state.is_isolated(ip):
            response_state.isolated_devices.add(ip)
            status = "completed"
        else:
            status = "skipped (already isolated)"

    elif alert_type == "data_exfil":
        # Always "complete" the quarantine simulation
        status = "completed"

    else:  # anomaly / default
        status = "completed"

    action_taken = {
        "action": action_name,
        "target": target,
        "timestamp": now,
        "status": status,
    }

    response_state.record_action(action_taken)
    return action_taken


# ---------------------------------------------------------------------------
# CLI / isolated test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Quick test: generate alerts and execute playbook."""
    from part2_detection_engine import detect_alert, MLAnomalyDetector
    from part1_data_simulator import log_stream

    # Set up ML detector (None if we just want rule-based)
    ml_detector = None

    # Set up state
    state = {
        "brute_force": {},
        "beaconing": {},
        "exfiltration": {},
        "suspicious_external_ips": [
            "185.220.101.12", "45.33.33.110", "198.51.100.42",
        ],
    }

    # Generate mixed traffic and detect alerts
    print("Generating alerts and executing playbook...\n")
    for entry in log_stream(stream_duration_sec=25, inject_attacks=True):
        alert = detect_alert(entry, state, ml_detector)
        if alert:
            action = execute_playbook(alert)
            print(f"ALERT: {alert['type']} ({alert['severity']}) from {alert['source_ip']}")
            print(f"  -> ACTION: {action['action']} target={action['target']} "
                  f"status={action['status']}")
            print()

    # Summary
    print(f"=== Summary ===")
    print(f"Total actions taken: {len(response_state.actions_taken)}")
    print(f"IPs blocked (simulated): {len(response_state.blocked_ips)}")
    print(f"Devices isolated (simulated): {len(response_state.isolated_devices)}")
    for a in response_state.actions_taken:
        print(f"  - {a['action']} on {a['target']} @ {a['timestamp']} [{a['status']}]")