"""
Cortex API MITM Capture Script for mitmproxy.

LS → Cortex (daily-cloudcode-pa.googleapis.com) 間の gRPC 通信をキャプチャし、
Project ID やリクエスト構造を解析する。

Usage:
    /tmp/mitm-env/bin/mitmdump -s cortex_capture.py --listen-port 8888 \
        --set upstream_cert=false --ssl-insecure
"""

import json
import re
from datetime import datetime

from mitmproxy import http, ctx


# Capture targets
TARGET_HOSTS = [
    "daily-cloudcode-pa.googleapis.com",
    "cloudcode-pa.googleapis.com",
    "antigravity-unleash.goog",
    "googleapis.com",  # Catch all Google APIs
]

LOG_FILE = "/tmp/cortex_capture.log"


# PURPOSE: [L2-auto] Write to both mitmproxy log and file.
def log(msg: str) -> None:
    """Write to both mitmproxy log and file."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{ts}] {msg}"
    ctx.log.info(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# PURPOSE: [L2-auto] Capture outgoing requests to Cortex.
def request(flow: http.HTTPFlow) -> None:
    """Capture outgoing requests to Cortex."""
    host = flow.request.pretty_host
    if not any(t in host for t in TARGET_HOSTS):
        return

    path = flow.request.path
    method = flow.request.method
    content_type = flow.request.headers.get("content-type", "unknown")

    log(f">>> REQUEST {method} {host}{path}")
    log(f"    Content-Type: {content_type}")

    # Log all headers (mask auth tokens)
    for k, v in flow.request.headers.items():
        if "auth" in k.lower() or "token" in k.lower():
            log(f"    Header {k}: {v[:30]}...({len(v)} chars)")
        else:
            log(f"    Header {k}: {v}")

    # Try to decode body
    body = flow.request.get_content()
    if body:
        log(f"    Body size: {len(body)} bytes")
        # Try JSON decode
        try:
            parsed = json.loads(body)
            log(f"    Body (JSON): {json.dumps(parsed, indent=2)[:500]}")
            # Check for project-related fields
            _find_project_fields(parsed, "request")
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Try to extract readable strings from protobuf
            strings = _extract_strings(body)
            if strings:
                log(f"    Body strings: {strings[:10]}")
            # Check for project patterns in raw bytes
            _find_project_in_bytes(body, "request")


# PURPOSE: [L2-auto] Capture responses from Cortex.
def response(flow: http.HTTPFlow) -> None:
    """Capture responses from Cortex."""
    host = flow.request.pretty_host
    if not any(t in host for t in TARGET_HOSTS):
        return

    path = flow.request.path
    status = flow.response.status_code
    content_type = flow.response.headers.get("content-type", "unknown")

    log(f"<<< RESPONSE {status} {host}{path}")
    log(f"    Content-Type: {content_type}")

    body = flow.response.get_content()
    if body:
        log(f"    Body size: {len(body)} bytes")
        try:
            parsed = json.loads(body)
            log(f"    Body (JSON): {json.dumps(parsed, indent=2)[:500]}")
            _find_project_fields(parsed, "response")
        except (json.JSONDecodeError, UnicodeDecodeError):
            strings = _extract_strings(body)
            if strings:
                log(f"    Body strings: {strings[:10]}")
            _find_project_in_bytes(body, "response")


# PURPOSE: [L2-auto] Recursively search for project-related fields in JSON.
def _find_project_fields(obj, context: str, path: str = "") -> None:
    """Recursively search for project-related fields in JSON."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            current = f"{path}.{k}" if path else k
            if any(w in k.lower() for w in [
                "project", "companion", "cloud", "quota"
            ]):
                log(f"    🎯 PROJECT FIELD ({context}): {current} = {v}")
            _find_project_fields(v, context, current)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _find_project_fields(item, context, f"{path}[{i}]")


# PURPOSE: [L2-auto] Search for project ID patterns in raw bytes.
def _find_project_in_bytes(data: bytes, context: str) -> None:
    """Search for project ID patterns in raw bytes."""
    patterns = [
        rb"projects/([a-z][a-z0-9-]{5,29})",
        rb"cloudaicompanion[_\x00]([a-z][a-z0-9-]{5,29})",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, data):
            log(f"    🎯 PROJECT PATTERN ({context}): {match.group().decode('ascii', errors='replace')}")


# PURPOSE: [L2-auto] Extract readable ASCII strings from binary data.
def _extract_strings(data: bytes, min_len: int = 6) -> list[str]:
    """Extract readable ASCII strings from binary data."""
    strings = []
    current = []
    for b in data:
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                strings.append("".join(current))
            current = []
    if len(current) >= min_len:
        strings.append("".join(current))
    return strings
