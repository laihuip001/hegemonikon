# PROOF: [L2/Exagoge] <- mekhane/ochema/
# PURPOSE: Google API (googleapis.com) のトラフィックをキャプチャし、
#         Antigravity LS (ConnectRPC) の通信仕様を解析する mitmproxy スクリプト
"""
Cortex Capture — Reverse Engineering Tool.

googleapis.com への通信を傍受し、ペイロード構造とレスポンス形式を特定する。
解析結果は `mekhane/ochema/proto.py` にフィードバックされる。

Usage:
    mitmproxy -s mekhane/ochema/scripts/cortex_capture.py
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

from mitmproxy import http

# ログ設定
LOG_DIR = Path("logs/cortex")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "capture.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# PURPOSE: [L2-auto] mitmproxy のリクエストハンドラ。
def request(flow: http.HTTPFlow) -> None:
    """mitmproxy request handler."""
    if "googleapis.com" in flow.request.host:
        log_traffic("REQ", flow)


# PURPOSE: [L2-auto] mitmproxy のレスポンスハンドラ。
def response(flow: http.HTTPFlow) -> None:
    """mitmproxy response handler."""
    if "googleapis.com" in flow.request.host:
        log_traffic("RES", flow)


# PURPOSE: [L2-auto] トラフィックをログに記録し、JSON ファイルとして保存する。
def log_traffic(direction: str, flow: http.HTTPFlow) -> None:
    """Log traffic details."""
    try:
        url = flow.request.url
        method = flow.request.method

        # Extract content safely
        content: bytes | None = None
        if direction == "REQ":
            content = flow.request.content
        elif flow.response:
            content = flow.response.content

        # Decode JSON if possible
        payload: Dict[str, Any] | str = ""
        if content:
            try:
                payload = json.loads(content.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload = "<binary or non-json>"

        # Log summary
        logging.info(f"{direction} {method} {url}")

        # Save artifact if it's a ConnectRPC call
        if "LanguageServerService" in url:
            save_artifact(direction, url, payload)

    except Exception as e:
        logging.error(f"Error logging traffic: {e}")


# PURPOSE: [L2-auto] 解析用アーティファクトを保存する。
def save_artifact(direction: str, url: str, payload: Any) -> None:
    """Save captured payload for analysis."""
    endpoint = url.split("/")[-1]
    timestamp = int(time.time())
    filename = LOG_DIR / f"{timestamp}_{direction}_{endpoint}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
