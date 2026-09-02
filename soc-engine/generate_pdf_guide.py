"""
Script to generate a comprehensive, highly detailed PDF documentation guide 
for the Autonomous Cyber SOC project.
"""

import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4B5563")) # Gray-600
        
        # Header (Only on page 2 and later)
        if self._pageNumber > 1:
            self.drawString(36, 756, "AUTONOMOUS CYBER SOC — COMPLETE PROJECT DOCUMENTATION & GUIDE")
            self.setStrokeColor(colors.HexColor("#D1D5DB"))
            self.setLineWidth(0.5)
            self.line(36, 748, 576, 748)
        
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#D1D5DB"))
        self.setLineWidth(0.5)
        self.line(36, 45, 576, 45)
        
        self.setFont("Helvetica", 8)
        self.drawString(36, 32, "Confidential — Autonomous Cyber SOC AI Security Project")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 32, page_str)
        self.restoreState()


def create_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1E293B"),
        alignment=0,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F8FAFC"),
        borderColor=colors.HexColor("#E2E8F0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=body_style,
        fontSize=8.5,
        leading=11.5,
        spaceAfter=0
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white,
        spaceAfter=0
    )

    q_title = ParagraphStyle(
        'QTitle',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#B91C1C"), # Red-700
        spaceBefore=8,
        spaceAfter=2,
        keepWithNext=True
    )

    ans_style = ParagraphStyle(
        'AnsStyle',
        parent=body_style,
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=10,
        spaceAfter=8
    )

    story = []

    # Title Block
    story.append(Paragraph("Autonomous Cyber SOC", title_style))
    story.append(Paragraph("AI-Powered Cyberattack Detection & Autonomous Response Platform — Complete Technical Reference Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceAfter=15))

    # SECTION 1: EXECUTIVE SUMMARY & OVERVIEW
    story.append(Paragraph("1. Executive Summary & Project Overview", h1_style))
    story.append(Paragraph(
        "The <b>Autonomous Cyber Security Operations Center (SOC)</b> is an end-to-end, automated cybersecurity platform "
        "designed to emulate a modern enterprise security center. In traditional Security Operations Centers, security analysts "
        "are overwhelmed by thousands of daily log alerts (alert fatigue), leading to delayed response times and uncontained breaches. "
        "This project solves alert fatigue by building a 5-stage automated pipeline that ingests raw network telemetry, detects "
        "cyber threats using hybrid (Rule-Based + Machine Learning) techniques, executes immediate containment playbooks, generates "
        "plain-English incident summaries using Google Gemini AI, and streams live telemetry to an interactive web dashboard with Human-in-the-Loop controls.",
        body_style
    ))

    overview_table_data = [
        [Paragraph("Core Capability", table_header), Paragraph("Technical Solution", table_header), Paragraph("Business / SOC Impact", table_header)],
        [
            Paragraph("<b>Log Simulation</b>", table_cell),
            Paragraph("Streams realistic SSH logins, DNS/HTTP flows, brute-force bursts, C2 beacons, data exfiltration.", table_cell),
            Paragraph("Provides realistic security telemetry without requiring expensive lab hardware.", table_cell)
        ],
        [
            Paragraph("<b>Hybrid Detection</b>", table_cell),
            Paragraph("Combines deterministic rule thresholds with Scikit-Learn Isolation Forest anomaly detection.", table_cell),
            Paragraph("Catches known signature attacks instantly while detecting unknown zero-day behavior.", table_cell)
        ],
        [
            Paragraph("<b>Automated Response</b>", table_cell),
            Paragraph("Automated playbooks (`block_ip`, `isolate_device`, `quarantine_transfer`).", table_cell),
            Paragraph("Reduces Mean Time to Respond (MTTR) from hours to sub-seconds.", table_cell)
        ],
        [
            Paragraph("<b>AI Incident Summaries</b>", table_cell),
            Paragraph("Google Gemini 1.5 Flash LLM generates executive-friendly 4-part summaries.", table_cell),
            Paragraph("Translates complex JSON logs into plain English for non-technical leadership.", table_cell)
        ],
        [
            Paragraph("<b>Live SOC Dashboard</b>", table_cell),
            Paragraph("FastAPI backend + Async WebSockets + HTML5/Tailwind responsive UI.", table_cell),
            Paragraph("Real-time threat feed with analyst Approve/Override controls.", table_cell)
        ]
    ]

    t_overview = Table(overview_table_data, colWidths=[1.4*inch, 3.2*inch, 2.4*inch])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 12))

    # SECTION 2: SYSTEM ARCHITECTURE & DATA FLOW
    story.append(Paragraph("2. System Architecture & End-to-End Data Pipeline", h1_style))
    story.append(Paragraph(
        "The application follows a strictly modular architecture composed of 7 primary parts plus a complete test suite. "
        "The data flow operates in a continuous real-time loop:",
        body_style
    ))

    arch_box_content = [
        [Paragraph("<b>HIGH-LEVEL DATA FLOW ARCHITECTURE</b>", ParagraphStyle('BoxHeader', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor("#1E3A8A")))],
        [Paragraph(
            "<b>[1. Data Simulator]</b> (Generates network logs & attack streams)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#129138; Yields raw JSON event logs<br/>"
            "<b>[2. Detection Engine]</b> (Evaluates Rules & Isolation Forest ML Anomaly Detector)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#129138; Output: Structured Threat Alert Dict (ID, Type, Severity, Evidence)<br/>"
            "<b>[3. Response Engine]</b> (Executes Security Playbooks)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#129138; Output: Containment Action (`block_ip`, `isolate_device`, `quarantine_transfer`)<br/>"
            "<b>[4. LLM Explainability]</b> (Calls Google Gemini LLM API / Fallback Summarizer)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#129138; Output: Plain-English executive summary<br/>"
            "<b>[5. Backend API Server]</b> (FastAPI + Asyncio Task Loop + WebSocket Manager)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#129138; Broadcasts alerts to clients over `ws://localhost:8000/ws/alerts`<br/>"
            "<b>[6. Frontend SOC Dashboard]</b> (HTML5, Tailwind CSS, Async JS Event Handlers)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#129138; Renders live threat stream, stats counters & Human Analyst Controls",
            callout_style
        )]
    ]
    t_arch = Table(arch_box_content, colWidths=[7.0*inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 14))

    # SECTION 3: FILE-BY-FILE DEEP DIVE
    story.append(Paragraph("3. Detailed File-by-File Breakdown & Code Explanation", h1_style))
    story.append(Paragraph(
        "Below is an exhaustive breakdown of every file in the project, detailing its purpose, code implementation, functions, and schemas.",
        body_style
    ))

    # File 1: part1_data_simulator.py
    story.append(Paragraph("3.1 Part 1 — Data Simulator (`part1_data_simulator.py`)", h2_style))
    story.append(Paragraph(
        "<b>Purpose:</b> Simulates live enterprise network traffic and intersperses realistic attack vectors for testing detection models.<br/>"
        "<b>Key Concepts & Attack Vectors Generated:</b>",
        body_style
    ))
    story.append(Paragraph("• <b>Normal Traffic:</b> Random network flow logs (HTTP GET/POST, SSH port 22, DNS queries, normal bytes sent/received).", bullet_style))
    story.append(Paragraph("• <b>Brute-Force Attack:</b> A burst of >5 failed login attempts targeted at administrative accounts within a 60-second window.", bullet_style))
    story.append(Paragraph("• <b>C2 Beaconing:</b> Periodic, rhythmic outbound pings from an internal endpoint to known malicious Command & Control IPs (e.g., <code>185.220.101.12</code>).", bullet_style))
    story.append(Paragraph("• <b>Data Exfiltration:</b> Unusually large outbound file transfers (>50 MB) originating during off-peak odd hours (23:00 to 05:00).", bullet_style))
    story.append(Paragraph(
        "<b>Code Highlights & Non-Blocking Design:</b><br/>"
        "The primary generator is <code>log_stream(stream_duration_sec, normal_interval, inject_attacks, sleep_between)</code>. "
        "We added a <code>sleep_between</code> parameter. When collecting normal traffic for ML model training, <code>sleep_between=False</code> allows instantaneous dataset generation. "
        "In async loops, delays are handled asynchronously via <code>await asyncio.sleep()</code> to prevent freezing the server thread.",
        body_style
    ))

    # File 2: part2_detection_engine.py
    story.append(Paragraph("3.2 Part 2 — Detection Engine (`part2_detection_engine.py`)", h2_style))
    story.append(Paragraph(
        "<b>Purpose:</b> Analyzes incoming JSON log entries and flags potential security threats using a hybrid detection approach.<br/>"
        "<b>Detection Mechanisms:</b>",
        body_style
    ))
    story.append(Paragraph("1. <b>Rule-Based Detector:</b> Deterministic stateful inspection tracking failed logins per IP, ping frequency, and exfiltration thresholds.", bullet_style))
    story.append(Paragraph("2. <b>ML Anomaly Detector (`MLAnomalyDetector` class):</b> Uses Scikit-Learn's <b>Isolation Forest</b> algorithm. Isolation Forest isolates anomalies by randomly selecting a feature and splitting the value. Anomalies require fewer splits to isolate, yielding shorter tree path lengths.", bullet_style))
    story.append(Paragraph(
        "<b>Core Functions:</b><br/>"
        "• <code>_detect_brute_force(log_entry, state)</code>: Flags IP if failed attempts ≥ 5 in 60s.<br/>"
        "• <code>_detect_beaconing(log_entry, state)</code>: Flags IP if outbound connection interval to suspicious external IPs is below threshold.<br/>"
        "• <code>_detect_exfiltration(log_entry, state)</code>: Flags transfer if byte count > 5MB during odd hours (23:00 - 05:00).<br/>"
        "• <code>detect_alert(log_entry, state, ml_detector)</code>: Orchestrates rule evaluations, falling back to ML anomaly scoring if rules do not trigger.",
        body_style
    ))

    # File 3: part3_response_engine.py
    story.append(Paragraph("3.3 Part 3 — Response Engine (`part3_response_engine.py`)", h2_style))
    story.append(Paragraph(
        "<b>Purpose:</b> Implements automated Incident Response (IR) playbooks to instantly neutralize detected threats.<br/>"
        "<b>Playbook Mapping & State Management:</b>",
        body_style
    ))
    playbook_table_data = [
        [Paragraph("Alert Type", table_header), Paragraph("Automated Action", table_header), Paragraph("Target Resource", table_header), Paragraph("Action Description", table_header)],
        [
            Paragraph("<code>brute_force</code>", table_cell),
            Paragraph("<code>block_ip</code>", table_cell),
            Paragraph("Attacker Source IP", table_cell),
            Paragraph("Applies firewall block rule to prevent further authentication attempts.", table_cell)
        ],
        [
            Paragraph("<code>c2_beacon</code>", table_cell),
            Paragraph("<code>isolate_device</code>", table_cell),
            Paragraph("Compromised Internal IP", table_cell),
            Paragraph("Disables network interface to halt command & control communication.", table_cell)
        ],
        [
            Paragraph("<code>data_exfil</code>", table_cell),
            Paragraph("<code>quarantine_transfer</code>", table_cell),
            Paragraph("Session / Destination IP", table_cell),
            Paragraph("Terminates active session and quarantines transferred files for forensic review.", table_cell)
        ],
        [
            Paragraph("<code>anomaly</code>", table_cell),
            Paragraph("<code>flag_for_review</code>", table_cell),
            Paragraph("Source IP / Account", table_cell),
            Paragraph("Enriches log context and routes to Tier-2 analyst queue.", table_cell)
        ]
    ]
    t_playbook = Table(playbook_table_data, colWidths=[1.3*inch, 1.5*inch, 1.5*inch, 2.7*inch])
    t_playbook.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_playbook)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Idempotency Guard:</b> Tracks <code>blocked_ips</code> and <code>isolated_devices</code> in a <code>response_state</code> set. "
        "If an IP is already blocked, subsequent triggers mark the status as <code>skipped (already blocked)</code>, preventing duplicate execution.",
        body_style
    ))

    # Page Break for clean layout
    story.append(PageBreak())

    # File 4: part4_llm_explain.py
    story.append(Paragraph("3.4 Part 4 — LLM Explainability Layer (`part4_llm_explain.py`)", h2_style))
    story.append(Paragraph(
        "<b>Purpose:</b> Uses Large Language Models (Google Gemini API) to translate raw alert JSON and technical playbook responses into concise, plain-English executive summaries.<br/>"
        "<b>Prompt Engineering & Required Structure:</b><br/>"
        "The system prompt instructs Gemini to output a structured summary covering 4 essential points:<br/>"
        "1. <b>WHAT HAPPENED:</b> Concise plain-English threat description.<br/>"
        "2. <b>HOW IT WAS DETECTED:</b> Rule or ML signal that flagged the anomaly.<br/>"
        "3. <b>WHAT ACTION WAS TAKEN:</b> Automated response executed by the playbook.<br/>"
        "4. <b>RECOMMENDED NEXT STEP:</b> Actionable guidance for human SOC analysts.<br/>"
        "<b>Resilient Fallback Mechanism:</b><br/>"
        "If the <code>GEMINI_API_KEY</code> is not provided, or if the API call experiences network/quota limits, the system catches the exception and gracefully generates a high-quality fallback template using string interpolation. This guarantees zero server downtime.",
        body_style
    ))

    # File 5: part5_api.py
    story.append(Paragraph("3.5 Part 5 — Backend API Gateway (`part5_api.py`)", h2_style))
    story.append(Paragraph(
        "<b>Purpose:</b> FastAPI application serving as the central nervous system. Wires Parts 1-4 together, provides REST endpoints, handles WebSocket connections, and serves the frontend dashboard.<br/>"
        "<b>Key Endpoints & WebSockets:</b>",
        body_style
    ))
    api_endpoints_data = [
        [Paragraph("HTTP Method / Type", table_header), Paragraph("Endpoint Path", table_header), Paragraph("Function & Description", table_header)],
        [Paragraph("<code>GET</code>", table_cell), Paragraph("<code>/</code> & <code>/dashboard</code>", table_cell), Paragraph("Serves the single-page HTML5 SOC Dashboard interface.", table_cell)],
        [Paragraph("<code>WebSocket</code>", table_cell), Paragraph("<code>/ws/alerts</code>", table_cell), Paragraph("Real-time bi-directional socket streaming new alerts to browser clients.", table_cell)],
        [Paragraph("<code>GET</code>", table_cell), Paragraph("<code>/api/alerts</code>", table_cell), Paragraph("Returns historical alerts with optional severity/type filtering.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/api/alerts/{id}/approve</code>", table_cell), Paragraph("Analyst HITL endpoint: approves or overrides/reverts automated actions.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/api/simulator/start</code>", table_cell), Paragraph("Launches non-blocking background simulation loop for N seconds.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/api/simulator/stop</code>", table_cell), Paragraph("Stops the active background simulation task immediately.", table_cell)],
        [Paragraph("<code>GET</code>", table_cell), Paragraph("<code>/api/simulator/status</code>", table_cell), Paragraph("Returns current simulation status (<code>running: true/false</code>).", table_cell)]
    ]
    t_api = Table(api_endpoints_data, colWidths=[1.5*inch, 2.2*inch, 3.3*inch])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 8))

    # File 6: part6_dashboard.py / index.html
    story.append(Paragraph("3.6 Part 6 — Frontend SOC Dashboard (`part6_dashboard.py` / `index.html`)", h2_style))
    story.append(Paragraph(
        "<b>Purpose:</b> Provides a dark-themed, glassmorphic Security Operations Center user interface built with HTML5, Tailwind CSS, and Vanilla JavaScript.<br/>"
        "<b>Key UI Features & Dynamic Behavior:</b><br/>"
        "• <b>Live Telemetry Stream:</b> Establishes an automatic WebSocket connection (`ws://localhost:8000/ws/alerts`). As new threats are detected, alert cards animate into the feed with severity badges (Critical: Red, High: Orange, Medium: Yellow, Low: Green).<br/>"
        "• <b>Threat Stats Counters:</b> Real-time metric boxes tracking Total Threat Alerts, High Severity, Critical Threats, and Brute-Force Attacks.<br/>"
        "• <b>Interactive Incident Detail Panel:</b> Clicking any alert displays full metadata, raw evidence, automated response status, and Gemini AI plain-English summary.<br/>"
        "• <b>Human Analyst Controls (HITL):</b> Provides <b>Approve Action</b> and <b>Override & Revert</b> buttons. When an analyst overrides an action, the API updates the status (e.g. <code>overridden_by_analyst - IP unblocked</code>) and broadcasts the updated state over WebSockets.<br/>"
        "• <b>Top-Bar Simulator Controls:</b> Includes <b>Simulate Attack</b> and <b>Stop Simulation</b> buttons with live connection status indicators (<code>🟢 SOC Live</code> vs <code>🔴 Disconnected</code>).",
        body_style
    ))

    # File 7 & Test Files
    story.append(Paragraph("3.7 Part 7 & Test Suite (`part7_demo_script.py`, `test_api.py`, `test_pipeline.py`)", h2_style))
    story.append(Paragraph(
        "• <b>`part7_demo_script.py`:</b> A structured 3-minute presentation script designed for hackathon judges and executive demonstrations, outlining step-by-step actions for brute-force attacks, C2 beaconing, and analyst overrides.<br/>"
        "• <b>`test_pipeline.py`:</b> End-to-end integration test validating log generation -> rule/ML detection -> playbook execution -> summary creation without spinning up HTTP servers.<br/>"
        "• <b>`test_api.py`:</b> Automated API unit test suite using FastAPI's <code>TestClient</code>. Validates REST endpoints, JSON models, approval endpoints, and simulator control routes.",
        body_style
    ))

    story.append(Spacer(1, 10))

    # SECTION 4: HOW THE WEBSITE WORKS (USER GUIDE)
    story.append(Paragraph("4. How the Website Works & Execution Workflow", h1_style))
    story.append(Paragraph(
        "To run and test the complete application manually, follow these 4 simple steps:",
        body_style
    ))
    story.append(Paragraph("1. <b>Start the Application Server:</b><br/><code>python part5_api.py</code><br/>This starts the FastAPI server listening on <code>http://localhost:8000</code>.", bullet_style))
    story.append(Paragraph("2. <b>Open the SOC Dashboard:</b><br/>Open your browser and navigate to <b><code>http://localhost:8000/</code></b>. The status badge will show <code>🟢 SOC Live</code>.", bullet_style))
    story.append(Paragraph("3. <b>Simulate Cyberattacks:</b><br/>Click the green <b>'Simulate Attack'</b> button in the top right. The simulator starts feeding attack logs into the pipeline, generating alerts live on the UI.", bullet_style))
    story.append(Paragraph("4. <b>Interact as a SOC Analyst:</b><br/>Click any threat entry in the live stream. Inspect the AI-generated incident summary and click <b>'Approve Action'</b> or <b>'Override & Revert'</b> to test analyst control.", bullet_style))

    story.append(PageBreak())

    # SECTION 5: INTERVIEW QUESTIONS AND ANSWERS
    story.append(Paragraph("5. Top Interview Questions & Detailed Answers", h1_style))
    story.append(Paragraph(
        "Here are 15 comprehensive technical and behavioral interview questions related to this project, complete with model answers.",
        body_style
    ))

    qa_list = [
        (
            "Q1: What is the main problem this Autonomous Cyber SOC project solves?",
            "Ans: It addresses 'Alert Fatigue' in Security Operations Centers. Traditional SOC analysts are inundated with thousands of raw logs daily, leading to missed threats and long Mean Time to Respond (MTTR). This project automates log ingestion, hybrid anomaly detection, playbook containment, and AI explanation, reducing MTTR to sub-seconds while keeping a human analyst in the loop."
        ),
        (
            "Q2: Why did you choose a Hybrid Detection model (Rules + Machine Learning)?",
            "Ans: Deterministic rules provide 100% precision for known attack signatures (e.g., >5 failed logins = brute force) with near-zero latency. However, rules cannot catch novel zero-day attacks. The ML Anomaly Detector (Isolation Forest) models baseline normal traffic behavior and flags unexpected statistical deviations, providing defense-in-depth."
        ),
        (
            "Q3: How does the Isolation Forest algorithm work in your project?",
            "Ans: Isolation Forest isolates anomalies by randomly selecting a feature and split value. Because anomalies (like massive off-hours data exfiltration) are rare and statistically distinct, they are isolated near the root of decision trees, resulting in shorter path lengths. We extract numerical features (bytes sent, bytes received, port numbers, hour of day) and fit the model on normal baseline traffic."
        ),
        (
            "Q4: Explain how WebSockets are used for real-time alerting.",
            "Ans: Traditional HTTP polling creates unnecessary server load and latency. We implemented an async WebSocket endpoint (`/ws/alerts`) in FastAPI. When the backend pipeline detects an attack, `broadcast_alert()` serializes the alert to JSON and pushes it to all connected WebSocket browser clients in real time (<10ms latency)."
        ),
        (
            "Q5: How did you solve Python asyncio event loop blocking during log simulation?",
            "Ans: Standard `time.sleep()` blocks Python's single-threaded event loop, preventing FastAPI from processing HTTP/WebSocket requests. We solved this by creating a non-blocking generator parameter `sleep_between=False` for fast execution, and using `await asyncio.sleep()` inside background tasks to yield execution back to the event loop."
        ),
        (
            "Q6: What is Human-in-the-Loop (HITL) and why is it essential in AI Security?",
            "Ans: Fully autonomous systems risk causing self-inflicted outages if an AI falsely blocks a legitimate mission-critical IP (False Positive). HITL ensures that while automated playbooks take immediate temporary containment actions, a human analyst retains ultimate authority to review AI summaries and approve or override/revert the action."
        ),
        (
            "Q7: How does your LLM Explainability Layer handle Gemini API failure or quota limits?",
            "Ans: We implemented a resilient fallback mechanism. The `generate_incident_summary()` function wraps the Gemini API call in a `try-except` block. If `GEMINI_API_KEY` is missing or the network request fails, it automatically returns a structured plain-English fallback summary generated from local alert metadata, ensuring 100% uptime."
        ),
        (
            "Q8: What is Idempotency in Incident Response, and how is it enforced?",
            "Ans: Idempotency means executing an operation multiple times yields the same result without unintended side effects. In `part3_response_engine.py`, we maintain global sets (`blocked_ips`, `isolated_devices`). If an attacker IP is already blocked, subsequent triggers check this state and mark the action as `skipped (already blocked)`, preventing duplicate firewall commands."
        ),
        (
            "Q9: How did you fix CORS issues when connecting the frontend to the backend?",
            "Ans: Browsers enforce Same-Origin Policy for HTTP and WebSockets. In FastAPI, we configured `CORSMiddleware` with `allow_origin_regex='.*'` and `allow_credentials=True`. This allows the dashboard to communicate seamlessly whether served via `localhost:8000`, `127.0.0.1`, or standalone HTML files."
        ),
        (
            "Q10: Why was the `websockets` Python library required for Uvicorn?",
            "Ans: Uvicorn is a lightweight ASGI web server implementation. While it handles standard HTTP/1.1 out-of-the-box, WebSocket protocol upgrades (`HTTP/1.1 101 Switching Protocols`) require an underlying WebSocket protocol engine like `websockets` or `wsproto`. Installing `websockets` enabled Uvicorn to accept WebSocket handshakes."
        ),
        (
            "Q11: Describe the structure of an Alert JSON payload in your pipeline.",
            "Ans: An Alert payload contains `alert_id` (deterministic SHA256 hash), `type` (e.g., `brute_force`, `c2_beacon`), `severity` (`critical`, `high`, `medium`, `low`), `source_ip`, `timestamp`, `raw_evidence` (failed attempt counts, byte sizes, user targets), `action_taken` (action, target, status, timestamp), and `incident_summary` (LLM string)."
        ),
        (
            "Q12: How would you scale this architecture to handle 100,000 logs/second in production?",
            "Ans: I would introduce Apache Kafka / AWS Kinesis as a distributed event streaming buffer, decouple the detection workers into stateless microservices using Celery/Redis or Kubernetes pods, store persistent alert logs in Elasticsearch / TimescaleDB, and use Redis Pub/Sub to scale WebSockets across multiple API gateway nodes."
        ),
        (
            "Q13: What prompt engineering techniques were used for the Gemini LLM?",
            "Ans: System prompt instructions enforced a strict role ('SOC analyst explaining to an executive'), length constraint (3-4 sentences), and 4 mandatory sections: WHAT HAPPENED, HOW IT WAS DETECTED, WHAT ACTION WAS TAKEN, and RECOMMENDED NEXT STEP. JSON alert data was injected dynamically via string formatting."
        ),
        (
            "Q14: How do you prevent SQL Injection / Command Injection in automated playbook execution?",
            "Ans: All IP targets and parameters are validated against Pydantic type schemas (`source_ip: str` matching IPv4 regex patterns) and parameterized execution handlers rather than passing raw un-sanitized strings directly to OS shell execution."
        ),
        (
            "Q15: What unit testing strategy did you implement for FastAPI?",
            "Ans: We used `fastapi.testclient.TestClient` in `test_api.py`. The test suite verifies endpoint status codes, JSON response schema compliance, simulator start/stop lifecycle management, and analyst approval/override decision recording."
        )
    ]

    for q, a in qa_list:
        story.append(Paragraph(q, q_title))
        story.append(Paragraph(a, ans_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF documentation successfully generated at: {filename}")

if __name__ == "__main__":
    output_path = os.path.join(os.getcwd(), "Autonomous_Cyber_SOC_Project_Guide.pdf")
    create_pdf(output_path)
