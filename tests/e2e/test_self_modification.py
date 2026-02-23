
import os
import sys
import time
import subprocess
import signal
import requests
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# Ensure project root is in path
sys.path.insert(0, os.getcwd())

from mekhane.api.server import app

# Target file path
SERVE_PY = Path("serve.py").resolve()

# Modified content for serve.py
NEW_CONTENT = """#!/usr/bin/env python3
# PURPOSE: Phase 5 Self-Modification PoC Target Application
# PROOF: [L2/Verification] <- PoC Target

from fastapi import FastAPI
import uvicorn
import sys
import time

app = FastAPI()

@app.get("/api/health")
async def health():
    return {"status": "ok", "poc_timestamp": time.time()}

if __name__ == "__main__":
    port = 9999
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    uvicorn.run(app, host="127.0.0.1", port=port)
"""

def wait_for_server(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(f"http://127.0.0.1:{port}/api/health")
            return True
        except requests.ConnectionError:
            time.sleep(0.5)
    return False

def test_self_modification_poc():
    print("Starting Phase 5 Self-Modification PoC Test...")

    # 1. Start serve.py (Target)
    print("Starting serve.py...")
    proc = subprocess.Popen(
        [sys.executable, str(SERVE_PY), "9999"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        if not wait_for_server(9999):
            raise Exception("serve.py failed to start")
        print("serve.py started on port 9999")

        # Verify initial state
        resp = requests.get("http://127.0.0.1:9999/api/health")
        data = resp.json()
        assert "poc_timestamp" not in data, "Timestamp should not exist yet"
        print("Initial state verified.")

        # 2. Mock CortexClient
        mock_response_1 = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "functionCall": {
                            "name": "propose_edit",
                            "args": {
                                "path": str(SERVE_PY),
                                "content": NEW_CONTENT,
                                "diff_summary": "Added timestamp"
                            }
                        }
                    }]
                }
            }]
        }
        mock_response_2 = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Change proposed."}]
                }
            }]
        }

        with patch("mekhane.ochema.cortex_client.CortexClient._call_api", side_effect=[mock_response_1, mock_response_2]):
            client = TestClient(app)

            # 3. Ask Agent
            print("Asking agent to modify serve.py...")
            resp = client.post("/api/ask/agent", json={"prompt": "Add timestamp to /api/health", "dry_run": True})
            assert resp.status_code == 200, f"Ask failed: {resp.text}"

            result = resp.json()
            proposal_id = result.get("proposal_id")
            assert proposal_id, "No proposal ID returned"
            print(f"Proposal ID received: {proposal_id}")

            # 4. Approve Proposal
            print("Approving proposal...")
            resp = client.post("/api/ask/agent/approve", json={"proposal_id": proposal_id})
            assert resp.status_code == 200, f"Approve failed: {resp.text}"
            print("Proposal approved.")

        # 5. Verify Modification (Restart serve.py to load changes)
        print("Restarting serve.py to load changes...")
        proc.terminate()
        proc.wait()

        # Start again
        proc = subprocess.Popen(
            [sys.executable, str(SERVE_PY), "9999"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if not wait_for_server(9999):
            raise Exception("serve.py failed to restart")

        print("serve.py restarted.")

        # 6. Final Assertion
        resp = requests.get("http://127.0.0.1:9999/api/health")
        data = resp.json()
        assert "poc_timestamp" in data, "Timestamp missing in modified app!"
        print("SUCCESS: poc_timestamp found in response.")

    finally:
        # Cleanup
        if proc.poll() is None:
            proc.terminate()
            proc.wait()

        # Restore original serve.py if needed (or leave it modified as proof?)
        # For repeatable tests, restore is better.
        # But this is a PoC, maybe keeping it is fine?
        # I'll restore it to be clean.
        with open(SERVE_PY, "w") as f:
            f.write("""#!/usr/bin/env python3
# PURPOSE: Phase 5 Self-Modification PoC Target Application
# PROOF: [L2/Verification] <- PoC Target

from fastapi import FastAPI
import uvicorn
import sys

app = FastAPI()

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = 9999
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    uvicorn.run(app, host="127.0.0.1", port=port)
""")
        print("Restored serve.py")

if __name__ == "__main__":
    test_self_modification_poc()
