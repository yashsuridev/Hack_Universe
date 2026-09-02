from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os
import time

app = FastAPI(title="Network Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scan_status = {"running": False, "results": None, "error": None}

def run_scan_task(target: str):
    global scan_status
    scan_status["running"] = True
    scan_status["results"] = None
    scan_status["error"] = None
    try:
        # We output to a temporary JSON file
        output_file = "temp_results.json"
        if os.path.exists(output_file):
            os.remove(output_file)
            
        process = subprocess.run(
            ["python", "scanner.py", target, "--output", output_file],
            capture_output=True, text=True
        )
        
        if process.returncode != 0 and not os.path.exists(output_file):
            scan_status["error"] = process.stderr
        else:
            with open(output_file, "r") as f:
                scan_status["results"] = json.load(f)
    except Exception as e:
        scan_status["error"] = str(e)
    finally:
        scan_status["running"] = False

@app.post("/api/scan/start")
def start_scan(target: str, background_tasks: BackgroundTasks):
    if scan_status["running"]:
        return {"message": "Scan already running"}
    background_tasks.add_task(run_scan_task, target)
    return {"message": "Scan started"}

@app.get("/api/scan/status")
def get_status():
    return scan_status

if __name__ == "__main__":
    import uvicorn
    print("Network Scanner API running on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
