"""Test the end-to-end pipeline directly."""
from part5_api import app, alert_history, ml_initialized, process_log_entry
from part1_data_simulator import log_stream
from part2_detection_engine import MLAnomalyDetector
from part3_response_engine import execute_playbook
from part4_llm_explain import generate_incident_summary

# Set up ML detector
normal_samples = []
for entry in log_stream(stream_duration_sec=10, inject_attacks=False):
    normal_samples.append(entry)
    if len(normal_samples) >= 30:
        break

ml_detector = MLAnomalyDetector(contamination=0.1)
ml_detector.fit(normal_samples)

# Mark ML as initialized
ml_initialized = True

# Process entries from the simulator
state = {
    "brute_force": {},
    "beaconing": {},
    "exfiltration": {},
    "suspicious_external_ips": [
        "185.220.101.12", "45.33.33.110", "198.51.100.42",
    ],
}

print("Processing 20 log entries through full pipeline...\n")
for i, entry in enumerate(log_stream(stream_duration_sec=15, inject_attacks=True)):
    if i >= 20:
        break
    alert = process_log_entry(entry)
    if alert:
        at = alert.get("action_taken", {})
        summary = alert.get("incident_summary", "N/A")
        at_info = f"{at.get('action')} target={at.get('target')} status={at.get('status')}"
        print(f"  ALERT: {alert['type']} ({alert['severity']}) from {alert['source_ip']}")
        print(f"    Action: {at_info}")
        print(f"    Summary: {summary[:100]}...")
        print()

print(f"\nTotal alerts in history: {len(alert_history)}")
print("\nPipeline test complete!")