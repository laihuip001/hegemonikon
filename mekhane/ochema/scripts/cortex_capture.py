# PROOF: [L2/Hodos] <- mekhane/ochema/scripts/cortex_capture.py
# PURPOSE: Cortex Capture Script
# REASON: Capture and log gRPC traffic between LS and Cortex for debugging.
"""
Cortex Capture Script (mitmproxy).

Captures gRPC traffic between the local Language Server and the Cortex backend
(daily-cloudcode-pa.googleapis.com). Logs request/response bodies to a file.

Usage:
    mitmdump -s cortex_capture.py --listen-port 8888 ...
"""

import json
from mitmproxy import http

# PURPOSE: [L2-auto] リクエストをインターセプトしてログ出力。
def request(flow: http.HTTPFlow) -> None:
    """リクエストをインターセプトしてログ出力。"""
    if "googleapis.com" in flow.request.pretty_host:
        log("--> Request", flow.request.path, flow.request.content)

# PURPOSE: [L2-auto] レスポンスをインターセプトしてログ出力。
def response(flow: http.HTTPFlow) -> None:
    """レスポンスをインターセプトしてログ出力。"""
    if "googleapis.com" in flow.request.pretty_host:
        log("<-- Response", flow.request.path, flow.response.content)

# PURPOSE: [L2-auto] ログファイルに出力。
def log(prefix: str, path: str, data: bytes) -> None:
    """ログファイルに出力。"""
    try:
        text = data.decode("utf-8", errors="replace")
        # gRPC ヘッダー除去 (簡易的)
        if len(text) > 5 and text[0] == "\x00":
            text = text[5:]

        with open("cortex_traffic.log", "a", encoding="utf-8") as f:
            f.write(f"{prefix} {path}\n")
            f.write(f"{text}\n")
            f.write("-" * 40 + "\n")
    except Exception as e:
        print(f"Log error: {e}")
