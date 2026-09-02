"""Part 1 — Data Simulator

Generates realistic fake network/login logs as JSON, streaming one entry
every X seconds. Includes normal traffic + injected instances of the 3
attack types:
  1. Brute-force login attempts
  2. Malware/C2 beaconing
  3. Data exfiltration (large outbound transfer at odd hours)
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Generator, Dict, Any, List

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Normal traffic parameters
NORMAL_INTERVAL_MIN = 0.3
NORMAL_INTERVAL_MAX = 2.0

# Attack injection rates (attacks per 100 normal entries)
BRUTE_FORCE_RATE = 1  # 1 brute-force burst per 100 normal logs
CANARY_RATE = 2       # 2 beaconing events per 100 normal logs
EXFIL_RATE = 1        # 1 exfiltration event per 100 normal logs

# Brute-force parameters
BRUTE_FAILED_PER_BURST = 6    # >5 failed logins = brute force flag
BRUTE_WINDOW_SEC = 60

# Beaconing parameters
BEACON_INTERVAL_SEC = 15      # regular ping interval
BEACON_EXTERNAL_IPS = ["185.220.101.12", "45.33.33.110", "198.51.100.42"]

# Exfiltration parameters
EXFIL_SIZE_THRESHOLD_MB = 50  # unusually large transfer >5MB
EXFIL_ODD_HOUR_START = 23     # odd hours start at 23:00
EXFIL_ODD_HOUR_END = 5        # end at 05:00


# ---------------------------------------------------------------------------
# Helper — random normal log entry
# ---------------------------------------------------------------------------

def _random_normal_log(timestamp: datetime) -> Dict[str, Any]:
    """Generate a single normal network log entry."""
    src_ips = [
        "10.0.1.20", "10.0.1.23", "10.0.1.45", "10.0.1.67",
        "10.0.1.88", "10.0.1.112", "10.0.1.145",
    ]
    dst_ips = ["10.0.0.1", "172.16.0.1", "192.168.1.1"]
    services = ["ssh", "http", "smtp", "dns"]
    methods = ["GET", "POST", "PUT", "DELETE"]

    entry = {
        "log_id": f"normal_{timestamp.strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
        "timestamp": timestamp.isoformat() + "Z",
        "source_ip": random.choice(src_ips),
        "destination_ip": random.choice(dst_ips),
        "source_port": random.randint(30000, 65535),
        "destination_port": random.choice([22, 80, 443, 25, 53]),
        "protocol": random.choice(["TCP", "UDP", "ICMP"]),
        "service": random.choice(services),
        "method": random.choice(methods) if random.random() > 0.2 else "N/A",
        "user_agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "python-requests/2.31.0",
        ]),
        "bytes_sent": random.randint(20, 5000),
        "bytes_received": random.randint(200, 15000),
        "event_type": "network_flow",
    }
    return entry


# ---------------------------------------------------------------------------
# Helper — brute-force login attempt log entry
# ---------------------------------------------------------------------------

def _brute_force_log(timestamp: datetime, source_ip: str) -> Dict[str, Any]:
    """Generate a burst of failed login logs from the same IP."""
    failed_attempts = []
    for i in range(BRUTE_FAILED_PER_BURST):
        attempt_ts = timestamp - timedelta(seconds=BRUTE_WINDOW_SEC + i)
        failed_attempts.append({
            "attempt_number": i + 1,
            "timestamp": attempt_ts.isoformat() + "Z",
            "source_ip": source_ip,
            "target_user": f"admin_{random.randint(1, 20)}",
            "status": "failed",
            "reason": "invalid_password",
        })
    return {
        "log_id": f"brute_force_{timestamp.strftime('%Y%m%d%H%M%S')}",
        "timestamp": timestamp.isoformat() + "Z",
        "source_ip": source_ip,
        "event_type": "authentication",
        "failed_attempts": failed_attempts,
    }


# ---------------------------------------------------------------------------
# Helper — malware/C2 beaconing log entry
# ---------------------------------------------------------------------------

def _beaconing_log(timestamp: datetime, source_ip: str, external_ip: str) -> Dict[str, Any]:
    """Generate a C2 beaconing log entry (device pinging external IP)."""
    return {
        "log_id": f"beacon_{timestamp.strftime('%Y%m%d%H%M%S')}",
        "timestamp": timestamp.isoformat() + "Z",
        "source_ip": source_ip,
        "destination_ip": external_ip,
        "destination_port": 443,
        "protocol": "TCP",
        "event_type": "dns_http",
        "bytes_sent": random.randint(50, 500),
        "bytes_received": random.randint(200, 2000),
        "connection_duration_sec": random.randint(3, 10),
        "is_beacon": True,
    }


# ---------------------------------------------------------------------------
# Helper — data exfiltration log entry
# ---------------------------------------------------------------------------

def _exfiltration_log(timestamp: datetime, source_ip: str, 
                      dest_ip: str, size_mb: float) -> Dict[str, Any]:
    """Generate a data exfiltration log entry (large outbound transfer)."""
    return {
        "log_id": f"exfil_{timestamp.strftime('%Y%m%d%H%M%S')}",
        "timestamp": timestamp.isoformat() + "Z",
        "source_ip": source_ip,
        "destination_ip": dest_ip,
        "destination_port": random.choice([443, 80, 21]),
        "protocol": "TCP",
        "event_type": "data_transfer",
        "bytes_sent": int(size_mb * 1024 * 1024 + random.randint(0, 1024 * 1024)),
        "bytes_received": random.randint(0, 100),
        "transfer_duration_sec": random.randint(30, 300),
        "is_exfiltration": True,
        "file_count": random.randint(100, 5000),
    }


# ---------------------------------------------------------------------------
# Main generator — streams log entries
# ---------------------------------------------------------------------------

def log_stream(
    stream_duration_sec: int = 60,
    normal_interval: float = None,
    inject_attacks: bool = True,
    sleep_between: bool = True,
) -> Generator[Dict[str, Any], None, None]:
    """
    Yield one log entry every `normal_interval` seconds (default random
    between NORMAL_INTERVAL_MIN/MAX). If inject_attacks is True, randomly
    intersperse instances of the 3 attack types.
    """
    if normal_interval is None:
        normal_interval = random.uniform(NORMAL_INTERVAL_MIN, NORMAL_INTERVAL_MAX)

    end_time = datetime.utcnow() + timedelta(seconds=stream_duration_sec)
    normal_count = 0

    while datetime.utcnow() < end_time:
        ts = datetime.utcnow()

        # Decide what kind of log entry to yield
        rand = random.random()

        if inject_attacks and rand < 0.15:  # ~15% chance of an attack entry
            # Roughly equal distribution among the 3 attack types among the 15%
            attack_kind = random.choices(
                ["brute_force", "beaconing", "exfiltration"],
                weights=[BRUTE_FORCE_RATE, CANARY_RATE, EXFIL_RATE],
                k=1,
            )[0]

            src_ip = random.choice([
                "10.0.1.50", "10.0.1.55", "10.0.1.60", "10.0.1.65",
                "10.0.1.70", "10.0.1.75", "10.0.1.80",
            ])

            if attack_kind == "brute_force":
                entry = _brute_force_log(ts, src_ip)
                entry["event_type"] = "authentication"
            elif attack_kind == "beaconing":
                ext_ip = random.choice(BEACON_EXTERNAL_IPS)
                entry = _beaconing_log(ts, src_ip, ext_ip)
                entry["event_type"] = "c2_beacon"
            else:  # exfiltration
                # Pick an odd-hour timestamp within the window
                hour = random.randint(EXFIL_ODD_HOUR_START, 23) or random.randint(
                    EXFIL_ODD_HOUR_START, EXFIL_ODD_HOUR_END
                )
                # Adjust timestamp to odd hour
                adj_ts = ts.replace(hour=hour, minute=random.randint(0, 59))
                size_mb = random.uniform(2, 50)
                entry = _exfiltration_log(adj_ts, src_ip, 
                                          random.choice(["8.8.8.8", "1.1.1.1", "0.0.0.0"]),
                                          size_mb)
                entry["event_type"] = "data_exfil"

            yield entry
            normal_count += 1
            if sleep_between:
                yield_delay = random.uniform(0.1, 0.5)
                time.sleep(yield_delay)
            continue

        # Normal traffic entry
        entry = _random_normal_log(ts)
        yield entry
        normal_count += 1

        if sleep_between:
            sleep_time = normal_interval - 0.02
            if sleep_time > 0:
                time.sleep(sleep_time)


# ---------------------------------------------------------------------------
# CLI / CLI testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Quick test: stream 30 seconds of logs and print each as JSON."""
    print("Streaming logs (Ctrl+C to stop):\n")
    try:
        for i, entry in enumerate(log_stream(stream_duration_sec=30, inject_attacks=True)):
            print(json.dumps(entry, indent=2))
            if i >= 50:  # safety cap
                break
    except KeyboardInterrupt:
        print("\nStopped by user.")