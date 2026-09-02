import subprocess
import time
import json
import httpx

import os
import sys

# Start the server in a subprocess
backend_dir = os.path.dirname(os.path.abspath(__file__))
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006"],
    cwd=backend_dir,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Wait for server to start
time.sleep(3)

try:
    with httpx.Client(timeout=60.0) as client:
        # Test the health endpoint
        print("=== Testing health endpoint ===")
        response = client.get("http://localhost:8006/api/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Read the zip file
        with open("test-project.zip", "rb") as f:
            zip_data = f.read()
        
        # Create a project (use no trailing slash)
        print("\n=== Creating project ===")
        resp = client.post("http://localhost:8006/api/projects", json={"name": "test-project", "description": "Test"})
        print(f"Create project: {resp.status_code}")
        project_id = resp.json()["id"]
        print(f"Project ID: {project_id}")
        
        # Upload and scan the project
        print("\n=== Uploading and scanning project ===")
        resp = client.post(
            f"http://localhost:8006/api/projects/{project_id}/upload",
            files={"file": ("test-project.zip", zip_data, "application/zip")}
        )
        print(f"Upload result: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        
        if resp.status_code in (200, 201):
            scan_result = resp.json()
            scan_id = scan_result.get("id")
            print(f"Scan ID: {scan_id}")
            
            # Wait a bit for scan to complete
            print("\n=== Waiting for scan to complete ===")
            time.sleep(3)
            
            # Check scan status
            print("\n=== Checking scan status ===")
            resp = client.get(f"http://localhost:8006/api/projects/{project_id}/scans/latest")
            print(f"Latest scan: {resp.status_code} - {resp.json()}")
            
            # Get risk score
            print("\n=== Getting risk score ===")
            resp = client.get(f"http://localhost:8006/api/scans/{scan_id}/risk")
            print(f"Risk result: {resp.status_code} - {resp.text}")
            
            # Get dependencies
            print("\n=== Getting dependencies ===")
            resp = client.get(f"http://localhost:8006/api/scans/{scan_id}/dependencies")
            print(f"Deps result: {resp.status_code}")
            if resp.status_code == 200:
                deps = resp.json()
                print(f"  Total deps: {len(deps)}")
            
            # Get SBOM
            print("\n=== Getting SBOM ===")
            resp = client.get(f"http://localhost:8006/api/sbom/scan/{scan_id}")
            print(f"SBOM result: {resp.status_code}")
            if resp.status_code == 200:
                sbom = resp.json()
                print(f"  Components: {len(sbom.get('components', []))}")
            
            # Get report
            print("\n=== Getting report ===")
            resp = client.get(f"http://localhost:8006/api/reports/scan/{scan_id}/summary")
            print(f"Report result: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  Report size: {len(resp.content)} bytes")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    proc.terminate()
    proc.wait()
    print("\nServer terminated.")