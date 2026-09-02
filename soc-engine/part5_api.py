"""Part 5 — Backend API (FastAPI)

Wires Parts 1-4 together:
  - WebSocket endpoint that streams new alerts in real time
  - REST endpoint to fetch alert history
  - REST endpoint for human analyst to approve/override actions
  - End-to-end pipeline: simulator → detection → playbook → LLM → WebSocket

FastAPI app with CORS configured for the React frontend.
"""

import json
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our built parts
from part1_data_simulator import log_stream
from part2_detection_engine import detect_alert, MLAnomalyDetector
from part3_response_engine import execute_playbook, response_state
from part4_llm_explain import generate_incident_summary

# ---------------------------------------------------------------------------
# FastAPI app setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Autonomous Cyber SOC API", version="1.0.0")

# CORS - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

# Detection state (rule-based thresholds per IP)
detection_state = {
    "brute_force": {},
    "beaconing": {},
    "exfiltration": {},
    "suspicious_external_ips": [
        "185.220.101.12", "45.33.33.110", "198.51.100.42",
    ],
}

# Alert history (in-memory, persists during server run)
alert_history: List[dict] = []

# Connected WebSocket clients
connected_clients: set = set()

# ML anomaly detector (optional)
ml_detector = MLAnomalyDetector(contamination=0.1)
# Flag to track if ML has been initialized
ml_initialized = False

# Simulator control
simulator_running = False
simulator_task: Optional[asyncio.Task] = None


# ---------------------------------------------------------------------------
# Pydantic models for API contracts
# ---------------------------------------------------------------------------

class AlertCreate(BaseModel):
    """Model for incoming alert (from detection engine)."""
    alert_id: str
    type: str
    severity: str
    source_ip: str
    timestamp: str
    raw_evidence: dict


class ActionTaken(BaseModel):
    """Model for action taken by playbook."""
    action: str
    target: str
    timestamp: str
    status: str


class ApprovalRequest(BaseModel):
    """Model for human analyst approval/override."""
    alert_id: Optional[str] = None
    approved: bool
    comment: Optional[str] = None


class AlertResponse(BaseModel):
    """Model for alert returned via API."""
    alert_id: str
    type: str
    severity: str
    source_ip: str
    timestamp: str
    raw_evidence: dict
    action_taken: Optional[ActionTaken] = None
    incident_summary: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper: Initialize ML detector on first request
# ---------------------------------------------------------------------------

def init_ml_detector(normal_entries: List[dict]) -> None:
    """Train the Isolation Forest on normal traffic."""
    global ml_initialized
    if not ml_initialized and normal_entries:
        ml_detector.fit(normal_entries)
        ml_initialized = True


# ---------------------------------------------------------------------------
# WebSocket endpoint — streams new alerts to connected clients
# ---------------------------------------------------------------------------

@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    """
    WebSocket endpoint that streams new alerts in real time.
    Clients connect and receive new alerts as they are generated.
    """
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Send existing alert history so client catches up
        if alert_history:
            await websocket.send_json({
                "type": "history",
                "alerts": alert_history[-50:]  # last 50 alerts
            })

        # Keep connection alive; alerts come via simulator push
        while True:
            # Wait for messages from client (keepalive pings)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        connected_clients.discard(websocket)


# ---------------------------------------------------------------------------
# REST endpoint — fetch alert history
# ---------------------------------------------------------------------------

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    limit: int = 50,
) -> List[dict]:
    """
    Fetch alert history with optional filtering.

    Parameters:
      - severity: filter by "low"/"medium"/"high"/"critical"
      - alert_type: filter by "brute_force"/"c2_beacon"/"data_exfil"/"anomaly"
      - limit: max number of alerts to return (default 50)
    """
    filtered = alert_history

    if severity:
        filtered = [a for a in filtered if a.get("severity") == severity]
    if alert_type:
        filtered = [a for a in filtered if a.get("type") == alert_type]

    # Add action_taken and incident_summary if missing
    enriched = []
    for alert in filtered[-limit:]:
        # Ensure action_taken exists
        at = alert.get("action_taken")
        if not at and "alert_id" in alert:
            # Try to find matching action from response state
            at_dict = {"action": "unknown", "target": "unknown", "timestamp": "", "status": "unknown"}
            enriched.append({
                **alert,
                "action_taken": at_dict,
                "incident_summary": f"Alert {alert['alert_id']} requires analysis",
            })
        else:
            enriched.append({
                **alert,
                "action_taken": at,
                "incident_summary": alert.get("incident_summary"),
            })

    return enriched


# ---------------------------------------------------------------------------
# REST endpoint — human analyst approves/overrides an action
# ---------------------------------------------------------------------------

@app.post("/api/alerts/{alert_id}/approve")
async def approve_alert(alert_id: str, request: ApprovalRequest) -> dict:
    """
    Human analyst approves or overrides an automated action.

    Parameters:
      - alert_id: the ID of the alert
      - approved: True = approve the automated action, False = override/cancel
      - comment: optional comment from the analyst

    Returns:
      Updated status of the action.
    """
    # Find the alert in history
    alert = None
    for a in alert_history:
        if a.get("alert_id") == alert_id:
            alert = a
            break

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    # Record the analyst decision
    decision = {
        "alert_id": alert_id,
        "approved": request.approved,
        "comment": request.comment,
        "analyst_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # If approved, mark action as validated; if overridden, mark as overridden
    if request.approved:
        # Validate/confirm the action was correct
        action = alert.get("action_taken", {})
        action["status"] = "validated_by_analyst"
        alert["action_taken"] = action
    else:
        # Override - reverse the automated action if possible
        action = alert.get("action_taken", {})
        action_type = action.get("action", "")
        if action_type == "block_ip":
            # Simulate unblocking
            action["status"] = "overridden_by_analyst - IP unblocked"
        elif action_type == "isolate_device":
            action["status"] = "overridden_by_analyst - device restored"
        elif action_type == "quarantine_transfer":
            action["status"] = "overridden_by_analyst - transfer resumed"
        else:
            action["status"] = "overridden_by_analyst"
        alert["action_taken"] = action

    # Push updated alert to WebSocket clients
    broadcast_alert(alert)

    return {
        "message": f"Alert {alert_id} {'approved' if request.approved else 'overridden'} by analyst",
        "decision": decision,
        "alert_id": alert_id,
    }


# ---------------------------------------------------------------------------
# Helper: Broadcast alert to WebSocket clients
# ---------------------------------------------------------------------------

def broadcast_alert(alert: dict) -> None:
    """Send a new alert to all connected WebSocket clients."""
    message = json.dumps({
        "type": "new_alert",
        "alert": alert,
    })
    for client in list(connected_clients):
        try:
            asyncio.create_task(client.send_text(message))
        except Exception:
            connected_clients.discard(client)


# ---------------------------------------------------------------------------
# End-to-end pipeline: process a single log entry
# ---------------------------------------------------------------------------

def process_log_entry(log_entry: dict) -> Optional[dict]:
    """
    Process a single log entry through the full pipeline:
    1. Detection → flag anomalies
    2. Playbook → determine automated action
    3. LLM → generate incident summary
    4. Persist → store in alert history & broadcast

    Returns the alert dict if an alert was generated, else None.
    """
    global ml_initialized

    # Step 1: Detect alert
    alert = detect_alert(log_entry, detection_state, ml_detector if ml_initialized else None)

    if not alert:
        return None

    # Step 2: Execute playbook action
    action_taken = execute_playbook(alert)

    # Step 3: Generate LLM summary
    try:
        summary = generate_incident_summary(alert, action_taken)
    except Exception as e:
        # If Gemini fails, use fallback from part4 module
        from part4_llm_explain import generate_incident_summary as fallback_summary
        # The function already has its own fallback, so just use empty
        summary = f"Alert {alert['alert_id']} detected and handled automatically."

    alert["action_taken"] = action_taken
    alert["incident_summary"] = summary

    # Step 4: Persist and broadcast
    alert_history.append(alert)
    # Keep history manageable
    if len(alert_history) > 200:
        alert_history[:] = alert_history[-100:]

    broadcast_alert(alert)

    return alert


from fastapi.responses import HTMLResponse

# Import dashboard HTML
try:
    from part6_dashboard import HTML as DASHBOARD_HTML
except ImportError:
    DASHBOARD_HTML = "<h1>Autonomous Cyber SOC Dashboard</h1><p>Dashboard HTML loading error.</p>"

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the SOC Dashboard HTML directly at the root URL."""
    return HTMLResponse(content=DASHBOARD_HTML)


class SimulatorStartRequest(BaseModel):
    duration_sec: Optional[int] = 60


@app.post("/api/simulator/start")
async def start_simulator(
    req: Optional[SimulatorStartRequest] = None,
    duration_sec: Optional[int] = None,
) -> dict:
    """
    Start the data simulator that feeds logs through the detection pipeline.
    """
    global simulator_running, simulator_task

    dur = 60
    if req and req.duration_sec is not None:
        dur = req.duration_sec
    elif duration_sec is not None:
        dur = duration_sec

    if simulator_running:
        return {"message": "Simulator already running", "status": "running"}

    simulator_running = True

    async def simulator_loop():
        global simulator_running
        try:
            async for log_entry in run_simulator(dur):
                process_log_entry(log_entry)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Simulator error: {e}")
        finally:
            simulator_running = False

    simulator_task = asyncio.create_task(simulator_loop())

    return {
        "message": f"Simulator started for {dur} seconds",
        "status": "running",
    }


@app.post("/api/simulator/stop")
async def stop_simulator() -> dict:
    """Stop the data simulator early."""
    global simulator_running, simulator_task

    if simulator_task:
        simulator_task.cancel()
        simulator_task = None

    simulator_running = False

    return {"message": "Simulator stopped", "status": "stopped"}


@app.get("/api/simulator/status")
async def get_simulator_status() -> dict:
    """Get current status of the data simulator."""
    return {"running": simulator_running}


async def run_simulator(duration_sec: int):
    """
    Async generator that yields log entries from the data simulator without blocking.
    """
    normal_entries = []
    for entry in log_stream(stream_duration_sec=5, inject_attacks=False, sleep_between=False):
        normal_entries.append(entry)
        if len(normal_entries) >= 30:
            break

    init_ml_detector(normal_entries)

    end_time = time.time() + duration_sec
    for entry in log_stream(stream_duration_sec=duration_sec, inject_attacks=True, sleep_between=False):
        yield entry
        await asyncio.sleep(0.3)
        if time.time() > end_time:
            break


# ---------------------------------------------------------------------------
# CLI / direct server launcher
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    print("Starting Autonomous Cyber SOC API & Dashboard Server...")
    print("Dashboard available at: http://localhost:8001/")
    print("API Documentation at:  http://localhost:8001/docs")
    print()

    uvicorn.run("part5_api:app", host="0.0.0.0", port=8001, reload=False)