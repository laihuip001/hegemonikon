# PROOF: [L2/Exagoge] <- mekhane/ochema/scripts/cortex_capture.py
# PURPOSE: Cortex Capture Script (mitmproxy)
"""
mitmproxy script to capture Antigravity LS traffic and reverse engineer
the Protocol Buffer structure.

Usage:
    mitmproxy -s mekhane/ochema/scripts/cortex_capture.py
"""

from mitmproxy import http
import json
import time
import os

# Output directory for captured payloads
OUTPUT_DIR = "mekhane/ochema/docs/payloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# PURPOSE: [L2-auto] リクエストをインターセプトして保存。
def request(flow: http.HTTPFlow) -> None:
    """リクエストをインターセプトして保存。"""
    if "googleapis.com" in flow.request.pretty_host:
        # Cortex API calls usually go to some google endpoint or localhost proxy
        pass

    if "CortexService" in flow.request.path:
        _save_interaction(flow, "req")


# PURPOSE: [L2-auto] レスポンスをインターセプトして保存。
def response(flow: http.HTTPFlow) -> None:
    """レスポンスをインターセプトして保存。"""
    if "CortexService" in flow.request.path:
        _save_interaction(flow, "res")


# PURPOSE: [L2-auto] インタラクションを JSON ファイルに保存。
def _save_interaction(flow: http.HTTPFlow, kind: str) -> None:
    """インタラクションを JSON ファイルに保存。"""
    method_name = flow.request.path.split("/")[-1]
    timestamp = int(time.time() * 1000)
    filename = f"{OUTPUT_DIR}/{timestamp}_{method_name}_{kind}.json"

    data = {
        "url": flow.request.url,
        "method": flow.request.method,
        "headers": dict(flow.request.headers),
        "content": flow.request.get_text() if kind == "req" else flow.response.get_text(),
    }

    try:
        # Try to parse as JSON if content-type says so
        if "json" in data["headers"].get("content-type", ""):
            data["json_content"] = json.loads(data["content"])
    except Exception:
        pass

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Captured {kind}: {filename}")
