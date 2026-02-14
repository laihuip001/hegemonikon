# PROOF: [L1/スクリプト] <- scripts/
"""mitmdump addon: Cortex API の Authorization ヘッダーをキャプチャする。

Usage:
    /tmp/mitmproxy-env/bin/mitmdump -p 8765 --mode reverse:https://daily-cloudcode-pa.googleapis.com/ -s /tmp/capture_cortex_token.py
"""
import datetime
import json

LOG_FILE = "/tmp/cortex_tokens.log"
INTERESTING_PATHS = [
    "GenerateChat",
    "StreamGenerateChat",
    "LoadCodeAssist",
    "GetCodeAssistModel",
]


def request(flow):
    """Intercept requests and log Authorization headers."""
    auth = flow.request.headers.get("authorization", "")
    path = flow.request.path

    # Log all requests with their headers
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "method": flow.request.method,
        "path": path,
        "host": flow.request.headers.get("host", ""),
        "has_auth": bool(auth),
        "auth_prefix": auth[:30] + "..." if len(auth) > 30 else auth,
        "content_type": flow.request.headers.get("content-type", ""),
    }

    # For interesting paths, log full auth
    is_interesting = any(p in path for p in INTERESTING_PATHS)
    if is_interesting and auth:
        entry["authorization_full"] = auth
        entry["interesting"] = True

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Print to console for visibility
    marker = "★" if is_interesting else " "
    print(f"{marker} {flow.request.method} {path} auth={'YES' if auth else 'NO'}")
