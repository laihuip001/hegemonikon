#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/ergasterion/n8n/ O4→n8n Cortex 統合→bridge が担う
# PURPOSE: n8n → Cortex API ブリッジ HTTP サーバー
"""
Cortex n8n Bridge — HTTP → Cortex API Proxy

n8n (Docker) から Cortex API を呼ぶためのブリッジサーバー。
ホスト上で動作し、OAuth トークン管理を代行する。

Architecture:
    n8n (Docker) → HTTP Request → host.docker.internal:9823
                                          ↓
                               cortex_n8n_bridge.py (Host)
                                          ↓
                               CortexClient → Cortex API

Usage:
    # Start bridge server
    cd ~/oikos/hegemonikon
    PYTHONPATH=. python mekhane/ergasterion/n8n/scripts/cortex_n8n_bridge.py

    # Test from host
    curl -X POST http://localhost:9823/ask \
      -H "Content-Type: application/json" \
      -d '{"prompt": "Hello", "model": "gemini-2.0-flash"}'

    # Test quota
    curl http://localhost:9823/quota

    # Health check
    curl http://localhost:9823/health
"""

import json
import logging
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

# Add project root to path
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

from mekhane.ochema.cortex_client import CortexClient, CortexError

# === Settings ===
PORT = int(os.getenv("CORTEX_BRIDGE_PORT", "9823"))
HOST = os.getenv("CORTEX_BRIDGE_HOST", "0.0.0.0")
DEFAULT_MODEL = os.getenv("CORTEX_BRIDGE_MODEL", "gemini-2.0-flash")
MAX_PROMPT_LENGTH = int(os.getenv("CORTEX_BRIDGE_MAX_PROMPT", "100000"))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [cortex-bridge] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("cortex-bridge")

# Lazy client
_client: CortexClient | None = None


# PURPOSE: CortexClient シングルトン
def get_client() -> CortexClient:
    global _client
    if _client is None:
        _client = CortexClient(model=DEFAULT_MODEL)
        log.info(f"CortexClient initialized: model={DEFAULT_MODEL}")
    return _client


# PURPOSE: JSON レスポンス送信ヘルパー
def send_json(handler: BaseHTTPRequestHandler, data: dict, status: int = 200) -> None:
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


# PURPOSE: リクエストボディ読取ヘルパー
def read_body(handler: BaseHTTPRequestHandler) -> dict:
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length == 0:
        return {}
    body = handler.rfile.read(content_length)
    return json.loads(body.decode("utf-8"))


# PURPOSE: HTTP リクエストハンドラ
class CortexBridgeHandler(BaseHTTPRequestHandler):
    """n8n → Cortex API bridge handler."""

    # PURPOSE: アクセスログをロガーにリダイレクト
    def log_message(self, format: str, *args: Any) -> None:
        """Redirect access logs to our logger."""
        log.info(format % args)

    # PURPOSE: GET エンドポイント (/health, /quota) のルーティング
    def do_GET(self) -> None:
        """GET endpoints: /health, /quota."""
        if self.path == "/health":
            send_json(self, {
                "status": "ok",
                "model": DEFAULT_MODEL,
                "port": PORT,
                "uptime": time.time() - _start_time,
            })
        elif self.path == "/quota":
            try:
                client = get_client()
                quota = client.retrieve_quota()
                buckets = []
                for b in quota.get("buckets", []):
                    buckets.append({
                        "model": b.get("modelId", "?"),
                        "remaining": round(b.get("remainingFraction", 0) * 100, 1),
                        "reset": b.get("resetTime", "?"),
                    })
                send_json(self, {"buckets": buckets})
            except Exception as e:
                send_json(self, {"error": str(e)}, 500)
        else:
            send_json(self, {"error": f"Unknown endpoint: {self.path}"}, 404)

    # PURPOSE: POST エンドポイント (/ask, /batch) のルーティング
    def do_POST(self) -> None:
        """POST endpoints: /ask, /batch."""
        if self.path == "/ask":
            self._handle_ask()
        elif self.path == "/batch":
            self._handle_batch()
        else:
            send_json(self, {"error": f"Unknown endpoint: {self.path}"}, 404)

    # PURPOSE: /ask エンドポイント — 単一プロンプト
    def _handle_ask(self) -> None:
        """Handle single prompt request.

        Request:
            {"prompt": "...", "model": "gemini-2.0-flash", "system_instruction": "...", "max_tokens": 8192}

        Response:
            {"text": "...", "model": "...", "tokens": {...}, "elapsed": 1.2}
        """
        try:
            body = read_body(self)
            prompt = body.get("prompt", "")
            if not prompt:
                send_json(self, {"error": "prompt is required"}, 400)
                return
            if len(prompt) > MAX_PROMPT_LENGTH:
                send_json(self, {"error": f"prompt too long ({len(prompt)} > {MAX_PROMPT_LENGTH})"}, 400)
                return

            model = body.get("model", DEFAULT_MODEL)
            system_instruction = body.get("system_instruction")
            max_tokens = int(body.get("max_tokens", 8192))

            client = get_client()
            start = time.time()

            resp = client.ask(
                prompt,
                model=model,
                system_instruction=system_instruction,
                max_tokens=max_tokens,
            )
            elapsed = round(time.time() - start, 2)

            log.info(f"ask: model={resp.model} tokens={resp.token_usage.get('total_tokens', 0)} elapsed={elapsed}s")

            send_json(self, {
                "text": resp.text,
                "model": resp.model,
                "tokens": resp.token_usage,
                "elapsed": elapsed,
            })

        except CortexError as e:
            log.error(f"CortexError: {e}")
            send_json(self, {"error": str(e)}, 502)
        except Exception as e:
            log.error(f"Error: {e}")
            send_json(self, {"error": str(e)}, 500)

    # PURPOSE: /batch エンドポイント — 複数プロンプト一括
    def _handle_batch(self) -> None:
        """Handle batch prompt request.

        Request:
            {"prompts": [{"prompt": "...", "model": "..."}, ...], "delay": 1.0}

        Response:
            {"results": [{"text": "...", "model": "...", "tokens": {...}}, ...], "total_tokens": 123}
        """
        try:
            body = read_body(self)
            prompts = body.get("prompts", [])
            if not prompts:
                send_json(self, {"error": "prompts is required"}, 400)
                return

            delay = float(body.get("delay", 1.0))
            client = get_client()

            # Convert to ask_batch format
            batch_items = []
            for p in prompts:
                item = {"prompt": p.get("prompt", "")}
                if "model" in p:
                    item["model"] = p["model"]
                if "system_instruction" in p:
                    item["system_instruction"] = p["system_instruction"]
                if "max_tokens" in p:
                    item["max_tokens"] = p["max_tokens"]
                batch_items.append(item)

            start = time.time()
            results = client.ask_batch(batch_items, delay=delay)
            elapsed = round(time.time() - start, 2)

            total_tokens = 0
            output = []
            for resp in results:
                tokens = resp.token_usage.get("total_tokens", 0)
                total_tokens += tokens
                output.append({
                    "text": resp.text,
                    "model": resp.model,
                    "tokens": resp.token_usage,
                })

            log.info(f"batch: {len(results)} prompts, {total_tokens} tokens, {elapsed}s")

            send_json(self, {
                "results": output,
                "total_tokens": total_tokens,
                "elapsed": elapsed,
            })

        except CortexError as e:
            log.error(f"CortexError: {e}")
            send_json(self, {"error": str(e)}, 502)
        except Exception as e:
            log.error(f"Error: {e}")
            send_json(self, {"error": str(e)}, 500)


# === Main ===
_start_time = time.time()


# PURPOSE: ブリッジサーバー起動エントリポイント
def main() -> None:
    """Start bridge server."""
    server = HTTPServer((HOST, PORT), CortexBridgeHandler)
    log.info(f"Cortex Bridge starting on {HOST}:{PORT}")
    log.info(f"Default model: {DEFAULT_MODEL}")
    log.info(f"Max prompt: {MAX_PROMPT_LENGTH} chars")
    log.info("Endpoints: GET /health, GET /quota, POST /ask, POST /batch")
    log.info("---")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
