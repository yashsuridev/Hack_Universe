"""Part 4 — LLM Explainability Layer (Gemini API)

For each alert, call the Gemini API to generate a short, plain-English
incident summary a non-technical person could understand, including:
  what happened, how it was detected, what automated action was taken,
  and a recommended next step for a human analyst.

Uses the `google-generativeai` SDK.

IMPORTANT: Set your GEMINI_API_KEY environment variable before running,
or paste it below as GEMINI_API_KEY="your-key-here"
"""

import os
import json
import time
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    HAS_GENAI = True
except Exception:
    genai = None
    HAS_GENAI = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY and HAS_GENAI:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        MODEL = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        MODEL = None
else:
    MODEL = None

# ---------------------------------------------------------------------------
# Prompt template (using .format() to avoid f-string brace conflicts)
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """You are a SOC (Security Operations Center) analyst explaining a cybersecurity 
incident to a non-technical executive. Keep the summary concise (3-4 sentences), 
clear, and reassuring. Include these four elements:

1. WHAT HAPPENED: A brief plain-English description of the threat.
2. HOW IT WAS DETECTED: The rule/ML signal that flagged it.
3. WHAT ACTION WAS TAKEN: The automated response that was executed.
4. RECOMMENDED NEXT STEP: What a human analyst should do next.

Alert data (JSON):
{alert_json}

Keep it professional but accessible. No technical jargon unless you explain it.
"""


# ---------------------------------------------------------------------------
# Core function — generate LLM summary for an alert
# ---------------------------------------------------------------------------

def generate_incident_summary(alert: dict, action_taken: dict) -> str:
    """
    Call Gemini API to produce a plain-English incident summary.

    Args:
        alert: The alert dict from the Detection Engine (Part 2)
        action_taken: The action dict from the Playbook Engine (Part 3)

    Returns:
        A string containing the Gemini-generated summary.
    """
    alert_json = json.dumps(alert, indent=2)
    action_json = json.dumps(action_taken, indent=2)

    prompt = PROMPT_TEMPLATE.format(alert_json=alert_json, action_json=action_json)

    try:
        response = MODEL.generate_content(prompt)
        summary = response.text.strip()
        # Ensure it's not too long - truncate if needed
        word_count = len(summary.split())
        if word_count > 50:
            # Manual truncation without regex
            words = summary.split()
            summary = " ".join(words[:50]) + "..."
        return summary
    except Exception as e:
        # Fallback: return a human-readable summary from the data we have
        return """INCIDENT SUMMARY (fallback - LLM unavailable)

What happened: A security alert was triggered for {alert_type} activity
from IP {source_ip} at {timestamp}.

How it was detected: Rule-based detection flagged {evidence_count} evidence points.

What action was taken: {action_action} target {action_target} 
with status {action_status}.

Recommended next step: A human analyst should review the alert details 
in the SOC dashboard, verify the evidence, and determine if additional 
manual intervention is required.
""".format(
            alert_type=alert.get("type", "unknown"),
            source_ip=alert.get("source_ip", "unknown"),
            timestamp=alert.get("timestamp", "unknown time"),
            evidence_count=len(alert.get("raw_evidence", {})),
            action_action=action_taken.get("action", "unknown"),
            action_target=action_taken.get("target", "unknown"),
            action_status=action_taken.get("status", "unknown"),
        )


# ---------------------------------------------------------------------------
# CLI / isolated test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Quick test: generate summary for a sample alert."""
    import os

    # Sample alert (from Part 2 detection)
    sample_alert = {
        "alert_id": "a1b2c3d4e5f6",
        "type": "brute_force",
        "severity": "high",
        "source_ip": "10.0.1.75",
        "timestamp": "2026-08-12T06:19:20Z",
        "raw_evidence": {
            "failed_attempt_count": 6,
            "target_users": ["admin_1", "admin_2", "admin_3", "admin_4", "admin_5", "admin_6"],
            "window_sec": 60,
        }
    }

    # Sample action (from Part 3 playbook)
    sample_action = {
        "action": "block_ip",
        "target": "10.0.1.75",
        "timestamp": "2026-08-12T06:19:21Z",
        "status": "completed",
    }

    print(f"Gemini API Key configured: {len(GEMINI_API_KEY) > 0}")
    if GEMINI_API_KEY:
        print("\nGenerating LLM summary...")
        summary = generate_incident_summary(sample_alert, sample_action)
        print("\n" + "=" * 60)
        print("GEMINI SUMMARY:")
        print("=" * 60)
        print(summary)
        print("=" * 60)
    else:
        print("Skipping Gemini call - no API key set.")
        print("\n--- Fallback summary ---")
        summary = generate_incident_summary(sample_alert, sample_action)
        print(summary)