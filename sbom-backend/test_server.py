import asyncio
import subprocess
import time
import urllib.request
import sys

import os

# Start the server in a subprocess
backend_dir = os.path.dirname(os.path.abspath(__file__))
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
    cwd=backend_dir,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Wait for server to start
time.sleep(3)

try:
    # Test the health endpoint
    req = urllib.request.urlopen("http://localhost:8001/api/health")
    result = req.read().decode()
    print("Health check result:")
    print(result)
except Exception as e:
    print(f"Error: {e}")
finally:
    proc.terminate()
    proc.wait()