"""Part 7 — Demo Script

3-minute Autonomous Cyber SOC live demo script for hackathon judges.

PREP (before demo):
  1. Start the backend:    python part5_api.py
  2. Open the dashboard:   http://localhost:3000 (or serve part6_dashboard.html)
  3. Ensure GEMINI_API_KEY is set (or summaries will use fallback mode)
  4. Verify all three parts 1-4 are imported/working

DEMO FLOW (approximately 3 minutes):

---------------------------------------------------------------------
STEP 1 — System Initialization (≈ 20 seconds)
---------------------------------------------------------------------
[Action]: Start the FastAPI server and open the dashboard.

[What judges see]:
  - Dashboard loads with "Connecting to alerts..." message
  - Client count shows 0 connected
  - Stats panel shows 0 alerts, 0 high, 0 critical, 0 brute force

[Spoken narrative]:
"Good morning judges. I'm going to demonstrate an Autonomous Cyber SOC 
system that detects cyber threats in real-time, automatically responds, 
and explains each incident in plain English using AI. The system consists 
of a data simulator, detection engine, automated playbook, LLM explainability 
layer, and a real-time dashboard — all wired together end-to-end."

[Judge expectation]: System boots up, WebSocket connection establishes.

---------------------------------------------------------------------
STEP 2 — Brute-Force Login Attack (≈ 40 seconds)
---------------------------------------------------------------------
[Action]: Click the "Start simulator" button on the dashboard (or the 
backend endpoint POST /api/simulator/start duration_sec=10).

[What judges see] (timing ~10 seconds):
  1. Alert feed: A new alert appears with RED "HIGH" severity badge
  - Alert type: "Brute Force Login Attempt"
  - Source IP: shows one of the simulated attacker IPs (e.g., 10.0.1.55)
  - Severity: HIGH (red)
  
  2. Selected alert panel updates automatically:
   - Severity icon turns red
   - Alert title: "Brute Force Login Attempt Detected"
   - Description: "Source IP: 10.0.1.55 • detected at [timestamp]"
   - Alert ID shown
   - AI-generated summary appears (3-4 sentences in plain English)
   
  3. Automated action panel updates:
   - Action: "block_ip" 
   - Target: "10.0.1.55"
   - Status: "completed"
   - Timestamp shown

  4. Stats panel updates:
   - Total Alerts: 1
   - High Severity: 1
   - Brute Force: 1

[Spoken narrative]:
"Now watch — a brute-force login attack is being simulated. Multiple failed 
logins from the same IP within a short time window. The detection engine 
immediately flags this as a HIGH severity threat. The AI explains: 'A brute 
force attack was detected from IP 10.0.1.55 with 6 failed login attempts against 
the admin account in 60 seconds. The system has automatically blocked this IP. 
A human analyst should review the blocked IP and consider additional security 
measures.' 

The automated response engine has already blocked the attacker's IP at the 
firewall. The analyst can approve or override this action."

[Key learning point]: Rule-based detection (>5 failed logins in 60 sec = brute 
force flag), playbook execution (brute_force → block_ip), and LLM summary 
generation all work in under 10 seconds.

---------------------------------------------------------------------
STEP 3 — C2 Beaconing/Malware Attack (≈ 40 seconds)
---------------------------------------------------------------------
[Action]: Wait for the simulator to continue (it runs for the configured 
duration, or click the simulator start again if it stopped).

[What judges see] (the simulator intersperses beaconing events):
  1. A new alert appears with ORANGE "HIGH" severity badge
  - Alert type: "C2 Beacon / Malware Communication"
  - Source IP: different IP showing outbound connections
  - Destination IP: shows a suspicious external IP (e.g., 185.220.101.12)
  - Severity: HIGH (orange)
  
  2. Alert detail panel updates:
   - Type: "C2 Beacon" 
   - Evidence shows regular ping intervals to suspicious external IP
   - AI summary: 'A compromised device was detected pinging a known C2 server 
     at IP 185.220.101.12 at regular intervals. The system has isolated the 
     device from the network to prevent further communication. A human analyst 
     should investigate the compromised device and remove any malware.'
   - Action: "isolate_device" 
   - Target: source IP 
   - Status: "completed"

  3. Stats update:
   - C2 beacon count increases

[Spoken narrative]:
"Second attack type — C2 beaconing or malware communication. A device on our 
network is regularly pinging a known malicious external IP, characteristic of 
command-and-control communication. The detection engine identifies the regular 
ping pattern with low variance. The AI explains: a compromised device pinging 
a C2 server. The automated response has isolated the device from the network. 
The analyst can review and override if needed."

[Key learning point]: Behavioral detection of regular beacon intervals, 
device isolation playbook, and LLM explaining the incident.

---------------------------------------------------------------------
STEP 4 — Data Exfiltration Attack (≈ 40 seconds)
---------------------------------------------------------------------
[Action]: Continue waiting for the simulator, or trigger another cycle.

[What judges see]:
  1. A new alert appears with RED "CRITICAL" severity badge
  - Alert type: "Data Exfiltration"
  - Source IP: internal IP
  - Destination IP: external IP (e.g., 1.1.1.1 or 8.8.8.8) 
  - Evidence: shows large bytes_sent (e.g., 28+ MB)
  - Odd-hour timestamp (nighttime/early morning)
  - Severity: CRITICAL (dark red)
  
  2. Alert detail panel:
   - Type: "Data Exfiltration"
   - Evidence: large outbound transfer, odd hour condition met
   - AI summary: 'At an unusual hour, a large data transfer of 28 MB was 
     detected from IP 10.0.1.70 to a external IP. The system has quarantined 
     the outbound transfer. A human analyst should review the transfer details 
     and determine if this represents legitimate business activity or actual 
     data theft.'
   - Action: "quarantine_transfer"
   - Target: source IP
   - Status: "completed"

  3. Stats update:
   - Critical alerts increase
   - Exfiltration count increases

[Spoken narrative]:
"Third and final attack type — data exfiltration. Unusually large outbound 
data transfer at an odd hour (nighttime). The detection rule flags transfers 
exceeding 5MB during hours 23:00-05:00. The AI explains: unusual large data 
transfer at odd hours, transfer quarantined. This is the most severe category 
— potential data breach. The analyst should carefully review whether this is 
legitimate overnight batch processing or actual theft."

[Key learning point]: Threshold-based detection (>5MB odd hours), critical 
severity, quarantine playbook, and LLM framing for non-technical audience.

---------------------------------------------------------------------
STEP 5 — Human Analyst Approval/Override (≈ 30 seconds)
---------------------------------------------------------------------
[Action]: Click the "Approve" button on the selected alert detail panel, 
or the "Override" button.

[What judges sees]:
  - If Approve: toast "Action approved by analyst" appears, the action status 
    changes to "validated_by_analyst"
  - If Override: toast "Action overridden by analyst" appears, the action status 
    changes to "overridden_by_analyst" (e.g., IP unblocked, device restored)

[Spoken narrative]:
"As a human analyst, I have the final say. Let me approve this automated 
action — confirming the IP block is correct. Or, if I determine the block was 
too aggressive, I can override it and restore normal access."

[Key learning point]: Human-in-the-loop control, the system respects analyst 
decisions, maintaining both security and operational continuity.

---------------------------------------------------------------------
STEP 6 — Summary & Close (≈ 20 seconds)
---------------------------------------------------------------------
[Action]: Take a step back and overview the dashboard.

[What judges see]:
  - Dashboard shows 3 alerts total (one of each type)
  - Stats: 3 total alerts, appropriate severity distribution
  - Each alert has its AI-generated summary visible
  - All automated actions recorded in the log

[Spoken narrative]:
"In summary, within just a few minutes this Autonomous Cyber SOC system has:
1. Detected three different attack types using rule-based analysis
2. Automatically responded — blocking IPs, isolating devices, quenching transfers
3. Generated plain-English AI explanations a non-technical person can understand
4. Provided human-in-the-loop control for final approval/override

The system works end-to-end: simulated data → rule-based + ML detection → 
automated playbook → LLM explainability → real-time dashboard. And it's 
all working right now with minimal external dependencies.

Thank you for watching the demo. I'm happy to answer any questions about 
the architecture, the detection rules, the playbook mappings, or the Gemini 
LLM integration."

---------------------------------------------------------------------
KEY TIMING NOTES:
- Brute-force: detected within ~1-2 seconds of simulator starting
- Beaconing: detected after ~3-4 beacon pings (simulated ~15s interval)  
- Exfiltration: detected immediately when the log entry is generated
- Human approval: instantaneous via API call

RECOVERY between demo cycles:
- Click "Refresh" on the dashboard or restart the backend
- Or run: python part5_api.py to restart the server
"""

print("=" * 70)
print("PART 7 — DEMO SCRIPT")
print("=" * 70)
print(__doc__)