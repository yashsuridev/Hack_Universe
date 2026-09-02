"""Part 2 — Detection Engine

Ingests log entries and flags anomalies using:
  1. Rule-based detection (brute-force, beaconing, exfiltration)
  2. Optional ML-based anomaly detector (Isolation Forest) trained on normal traffic

Output format per alert:
{
  "alert_id": str,
  "type": str,          # "brute_force" | "c2_beacon" | "data_exfil" | "anomaly"
  "severity": str,      # "low" | "medium" | "high" | "critical"
  "source_ip": str,
  "timestamp": str,
  "raw_evidence": dict
}
"""

import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Try to import sklearn for optional ML detector
try:
    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ---------------------------------------------------------------------------
# Rule-based detection thresholds
# ---------------------------------------------------------------------------

BRUTE_FORCE_THRESHOLD = 5      # >5 failed logins in window = brute force
BRUTE_FORCE_WINDOW_SEC = 60

BEACON_INTERVAL_SEC = 12       # if pings < this interval, flag as beacon
EXFIL_SIZE_THRESHOLD_BYTES = 5 * 1024 * 1024  # >5MB = exfiltration
EXFIL_ODD_HOURS = list(range(23, 24)) + list(range(0, 6))  # 23:00-05:59


# ---------------------------------------------------------------------------
# Helper — generate deterministic alert ID
# ---------------------------------------------------------------------------

def _alert_id(log_entry: dict, detection_type: str, source_ip: str) -> str:
    """Create a short, deterministic alert ID from log entry + type."""
    key = f"{detection_type}:{source_ip}:{log_entry.get('timestamp', '')}"
    return hashlib.sha256(key.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Rule-based detectors
# ---------------------------------------------------------------------------

def _detect_brute_force(log_entry: dict, state: dict) -> Optional[dict]:
    """
    Detect brute-force: >5 failed logins from same IP in 60 sec.
    Expected log_entry format (from PART 1 brute_force):
    {
        "event_type": "authentication",
        "source_ip": "...",
        "failed_attempts": [ {...}, {...}, ... ]
    }
    """
    if log_entry.get("event_type") != "authentication":
        return None

    failed_attempts = log_entry.get("failed_attempts", [])
    if len(failed_attempts) >= BRUTE_FORCE_THRESHOLD:
        src_ip = log_entry.get("source_ip", "unknown")
        ts_str = log_entry.get("timestamp", datetime.utcnow().isoformat())

        # Update state tracking per IP
        if src_ip not in state["brute_force"]:
            state["brute_force"][src_ip] = {"count": 0, "first_ts": None}

        state["brute_force"][src_ip]["count"] += len(failed_attempts)
        if state["brute_force"][src_ip]["first_ts"] is None:
            state["brute_force"][src_ip]["first_ts"] = ts_str

        return {
            "alert_id": _alert_id(log_entry, "brute_force", src_ip),
            "type": "brute_force",
            "severity": "high",
            "source_ip": src_ip,
            "timestamp": ts_str,
            "raw_evidence": {
                "failed_attempt_count": len(failed_attempts),
                "target_users": [a.get("target_user") for a in failed_attempts],
                "window_sec": BRUTE_FORCE_WINDOW_SEC,
            }
        }
    return None


def _detect_beaconing(log_entry: dict, state: dict) -> Optional[dict]:
    """
    Detect C2 beaconing: device pinging suspicious external IP at regular intervals.
    Expected log_entry format (from PART 1 beaconing):
    {
        "event_type": "c2_beacon",
        "source_ip": "...",
        "destination_ip": "185.220.101.12|45.33.33.110|198.51.100.42",
        "is_beacon": true,
        "connection_duration_sec": int,
        "bytes_sent": int,
    }
    """
    if log_entry.get("event_type") != "c2_beacon":
        return None

    src_ip = log_entry.get("source_ip", "unknown")
    dst_ip = log_entry.get("destination_ip", "")

    # Check if this is a known suspicious external IP
    suspicious_ips = state.get("suspicious_external_ips", [])
    is_suspicious = dst_ip in suspicious_ips

    # Track beacon intervals per source IP
    if src_ip not in state["beaconing"]:
        state["beaconing"][src_ip] = {"last_ts": None, "count": 0, "intervals": []}

    entry_ts = datetime.fromisoformat(
        log_entry["timestamp"].replace("Z", "+00:00")
    )

    prev_ts = state["beaconing"][src_ip]["last_ts"]
    if prev_ts is not None:
        delta = (entry_ts - prev_ts).total_seconds()
        state["beaconing"][src_ip]["intervals"].append(delta)
        # Keep only last 10 intervals
        if len(state["beaconing"][src_ip]["intervals"]) > 10:
            state["beaconing"][src_ip]["intervals"] = state["beaconing"][src_ip]["intervals"][-10:]

        # Check if intervals are very regular (potential beacon)
        intervals = state["beaconing"][src_ip]["intervals"]
        if len(intervals) >= 3:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
            # Low variance = regular beaconing
            if variance < 4 and avg_interval < BEACON_INTERVAL_SEC * 2:
                return {
                    "alert_id": _alert_id(log_entry, "c2_beacon", src_ip),
                    "type": "c2_beacon",
                    "severity": "high",
                    "source_ip": src_ip,
                    "timestamp": log_entry["timestamp"],
                    "raw_evidence": {
                        "dest_ip": dst_ip,
                        "avg_interval_sec": avg_interval,
                        "interval_variance": variance,
                        "connection_count": state["beaconing"][src_ip]["count"] + 1,
                    }
                }
    state["beaconing"][src_ip]["last_ts"] = entry_ts
    state["beaconing"][src_ip]["count"] += 1

    return None


def _detect_exfiltration(log_entry: dict, state: dict) -> Optional[dict]:
    """
    Detect data exfiltration: unusually large outbound data transfer at odd hours.
    Expected log_entry format (from PART 1 exfiltration):
    {
        "event_type": "data_exfil",
        "source_ip": "...",
        "destination_ip": "...",
        "bytes_sent": int (>5MB flagged),
        "is_exfiltration": true,
        "transfer_duration_sec": int,
        "file_count": int,
    }
    """
    if log_entry.get("event_type") != "data_exfil":
        return None

    src_ip = log_entry.get("source_ip", "unknown")
    bytes_sent = log_entry.get("bytes_sent", 0)
    timestamp = log_entry.get("timestamp", "")

    # Check odd-hour condition
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        is_odd_hour = dt.hour in EXFIL_ODD_HOURS
    except Exception:
        is_odd_hour = False

    size_mb = bytes_sent / (1024 * 1024)
    is_large = bytes_sent > EXFIL_SIZE_THRESHOLD_BYTES

    if is_large or is_odd_hour:
        # Update state tracking
        if src_ip not in state["exfiltration"]:
            state["exfiltration"][src_ip] = {"total_bytes": 0, "count": 0, "odd_hours": 0}

        state["exfiltration"][src_ip]["total_bytes"] += bytes_sent
        state["exfiltration"][src_ip]["count"] += 1
        if is_odd_hour:
            state["exfiltration"][src_ip]["odd_hours"] += 1

        severity = "critical" if size_mb > 50 else ("high" if size_mb > 10 else "medium")

        return {
            "alert_id": _alert_id(log_entry, "data_exfil", src_ip),
            "type": "data_exfil",
            "severity": severity,
            "source_ip": src_ip,
            "timestamp": timestamp,
            "raw_evidence": {
                "bytes_sent": bytes_sent,
                "size_mb": round(size_mb, 2),
                "dest_ip": log_entry.get("destination_ip", "unknown"),
                "port": log_entry.get("destination_port", "unknown"),
                "is_odd_hour": is_odd_hour,
                "transfer_duration_sec": log_entry.get("transfer_duration_sec", 0),
                "file_count": log_entry.get("file_count", 0),
            }
        }
    return None


# ---------------------------------------------------------------------------
# ML-based anomaly detector (Isolation Forest)
# ---------------------------------------------------------------------------

class MLAnomalyDetector:
    """Isolation Forest trained on normal traffic features."""

    def __init__(self, contamination: float = 0.05):
        if not SKLEARN_AVAILABLE:
            self._available = False
            return
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=100,
            max_samples="auto",
            contamination=contamination,
            random_state=42,
        )
        self.feature_names = [
            "bytes_sent", "bytes_received", "transfer_duration_sec", "file_count"
        ]
        self.trained = False
        self.feature_stats = {}

    def fit(self, normal_entries: List[dict]):
        """Train on normal (non-attack) log entries."""
        if not SKLEARN_AVAILABLE or not normal_entries:
            self.trained = False
            return

        X = []
        for entry in normal_entries:
            row = []
            for fname in self.feature_names:
                val = entry.get(fname, 0)
                # Normalize by cliping extremes
                row.append(min(val, 10000))  # cap at 10k
            X.append(row)

        if len(X) >= 10:  # minimum samples
            self.model.fit(np.array(X))
            self.trained = True
            # Compute feature stats for debugging
            self.feature_stats = {
                fname: {
                    "mean": float(np.mean([r[i] for r in X])),
                    "std": float(np.std([r[i] for r in X]))
                }
                for i, fname in enumerate(self.feature_names)
            }
        else:
            self.trained = False

    def predict(self, log_entry: dict) -> Optional[dict]:
        """Return alert dict if anomaly detected, else None."""
        if not self.trained or not SKLEARN_AVAILABLE:
            return None

        row = []
        for fname in self.feature_names:
            val = log_entry.get(fname, 0)
            row.append(min(val, 10000))

        prediction = self.model.predict(np.array([row]))[0]
        # Isolation Forest: -1 = anomaly, 1 = normal
        if prediction == -1:
            # Compute anomaly score (decision function)
            try:
                score = self.model.decision_function(np.array([row]))[0]
            except Exception:
                score = 0.0

            # Map isolation Forest anomaly to our alert format
            src_ip = log_entry.get("source_ip", "unknown")
            return {
                "alert_id": _alert_id(log_entry, "anomaly", src_ip),
                "type": "anomaly",
                "severity": "medium",
                "source_ip": src_ip,
                "timestamp": log_entry.get("timestamp", datetime.utcnow().isoformat()),
                "raw_evidence": {
                    "anomaly_score": float(score),
                    "features": {fname: log_entry.get(fname, 0) for fname in self.feature_names},
                }
            }
        return None


# ---------------------------------------------------------------------------
# Main detection engine — process a single log entry
# ---------------------------------------------------------------------------

def detect_alert(
    log_entry: dict,
    state: dict,
    ml_detector: Optional[MLAnomalyDetector] = None,
) -> Optional[dict]:
    """
    Ingest a single log entry and return an alert dict if an anomaly is found,
    otherwise return None.

    Detection order:
      1. Rule-based brute-force
      2. Rule-based beaconing
      3. Rule-based exfiltration
      4. ML-based anomaly (optional)
    """
    # Rule-based: brute force
    alert = _detect_brute_force(log_entry, state)
    if alert:
        return alert

    # Rule-based: beaconing
    alert = _detect_beaconing(log_entry, state)
    if alert:
        return alert

    # Rule-based: exfiltration
    alert = _detect_exfiltration(log_entry, state)
    if alert:
        return alert

    # ML-based anomaly (last, to avoid false positives on known types)
    if ml_detector:
        ml_alert = ml_detector.predict(log_entry)
        if ml_alert:
            return ml_alert

    return None


# ---------------------------------------------------------------------------
# CLI / isolated test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Quick test: generate normal entries, train ML, then detect alerts."""
    from part1_data_simulator import log_stream

    # Phase 1: Collect normal traffic entries for ML training
    print("Phase 1: Collecting normal traffic for ML training...")
    normal_entries = []
    count = 0
    for entry in log_stream(stream_duration_sec=15, inject_attacks=False):
        normal_entries.append(entry)
        count += 1
        if count >= 30:
            break
    print(f"  Collected {len(normal_entries)} normal entries")

    # Phase 2: Train ML detector
    print("Phase 2: Training Isolation Forest...")
    ml_detector = MLAnomalyDetector(contamination=0.1)
    ml_detector.fit(normal_entries)
    print(f"  ML trained: {ml_detector.trained}")

    # Phase 3: Run detection on mixed traffic
    print("Phase 3: Detecting alerts in mixed traffic...")
    state = {
        "brute_force": {},
        "beaconing": {},
        "exfiltration": {},
        "suspicious_external_ips": [
            "185.220.101.12", "45.33.33.110", "198.51.100.42",
        ],
    }

    alerts = []
    for entry in log_stream(stream_duration_sec=20, inject_attacks=True):
        alert = detect_alert(entry, state, ml_detector)
        if alert:
            alerts.append(alert)
            print(f"  ALERT: {alert['type']} from {alert['source_ip']} "
                  f"(severity: {alert['severity']})")

    print(f"\nTotal alerts detected: {len(alerts)}")
    for a in alerts:
        print(f"  - {a['type']} ({a['severity']}) from {a['source_ip']}")