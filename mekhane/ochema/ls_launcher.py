#!/usr/bin/env python3
# PROOF: [L2/Orchestration] <- mekhane/ochema/ A0→Implementation→ls_launcher.py
"""LS Standalone Launcher — IDE なしで Language Server を直接起動する。

ManagementMetadata protobuf を stdin に送り込んで LS を起動。
Proto definition (from extension.js + Go binary analysis):

    message ManagementMetadata {  // exa.index_pb.ManagementMetadata
      string auth_token = 1;                 // OAuth access token (ya29.xxx)
      string auth_uid = 2;                   // User identifier
      string service_key = 3;                // API/service key  
      bool   force_target_public_index = 4;  // Optional
      string force_team_id = 5;              // Optional
      string service_key_id = 6;             // Optional
    }
"""
from __future__ import annotations

import argparse
import os
import signal
import struct
import subprocess
import sys
import time
import uuid


LS_BINARY = (
    "/usr/share/antigravity/resources/app/extensions/antigravity/bin/"
    "language_server_linux_x64"
)

CLOUD_CODE_ENDPOINT = "https://daily-cloudcode-pa.googleapis.com"


def encode_protobuf_string(field_number: int, value: str) -> bytes:
    """Encode a protobuf string field (wire type 2)."""
    if not value:
        return b""
    tag = (field_number << 3) | 2  # wire type 2 = length-delimited
    data = value.encode("utf-8")
    return _encode_varint(tag) + _encode_varint(len(data)) + data


def encode_protobuf_bool(field_number: int, value: bool) -> bytes:
    """Encode a protobuf bool field (wire type 0)."""
    if not value:
        return b""
    tag = (field_number << 3) | 0  # wire type 0 = varint
    return _encode_varint(tag) + _encode_varint(1 if value else 0)


def _encode_varint(value: int) -> bytes:
    """Encode an integer as a protobuf varint."""
    result = []
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


def build_management_metadata(
    auth_token: str,
    auth_uid: str = "",
    service_key: str = "",
) -> bytes:
    """Build ManagementMetadata protobuf binary."""
    msg = b""
    msg += encode_protobuf_string(1, auth_token)
    if auth_uid:
        msg += encode_protobuf_string(2, auth_uid)
    if service_key:
        msg += encode_protobuf_string(3, service_key)
    return msg


def get_current_oauth_token() -> str | None:
    """現在起動中の LS プロセスのメモリから OAuth token を取得する。
    
    方法: /proc/PID/mem から ya29. で始まるトークンを検索。
    """
    import re
    
    # Get LS PID
    result = subprocess.run(
        ["pgrep", "-f", "language_server_linux.*server_port"],
        capture_output=True, text=True
    )
    if not result.stdout.strip():
        return None
    
    pid = result.stdout.strip().split("\n")[0]
    
    # Read memory maps
    maps_path = f"/proc/{pid}/maps"
    mem_path = f"/proc/{pid}/mem"
    
    token_pattern = re.compile(rb"ya29\.[A-Za-z0-9_.-]{100,500}")
    found_tokens: set[str] = set()
    
    try:
        with open(maps_path, "r") as maps_file:
            with open(mem_path, "rb") as mem_file:
                for line in maps_file:
                    # Only scan heap and anonymous mappings
                    if not ("rw" in line and ("[heap]" in line or "anon" in line.lower() or " 0 " in line)):
                        continue
                    
                    parts = line.split()
                    addr_range = parts[0].split("-")
                    start = int(addr_range[0], 16)
                    end = int(addr_range[1], 16)
                    
                    # Limit chunk size
                    chunk_size = min(end - start, 10 * 1024 * 1024)  # 10MB max
                    
                    try:
                        mem_file.seek(start)
                        data = mem_file.read(chunk_size)
                        
                        for match in token_pattern.finditer(data):
                            token = match.group().decode("utf-8", errors="ignore")
                            found_tokens.add(token)
                    except (OSError, ValueError):
                        continue
    except PermissionError:
        print("Warning: Need root/same-user access for /proc/PID/mem", file=sys.stderr)
        return None
    
    if found_tokens:
        # Return the longest token (most likely to be complete)
        return max(found_tokens, key=len)
    return None


def launch_ls(
    port: int,
    auth_token: str,
    workspace_id: str = "standalone",
    auth_uid: str = "",
    service_key: str = "",
    verbose: bool = False,
    extension_server_port: int | None = None,
) -> subprocess.Popen:
    """LS を直接起動する。"""
    csrf_token = str(uuid.uuid4())
    
    args = [
        LS_BINARY,
        "--server_port", str(port),
        "--csrf_token", csrf_token,
        "--workspace_id", workspace_id,
        "--app_data_dir", "antigravity",
        "--cloud_code_endpoint", CLOUD_CODE_ENDPOINT,
    ]
    
    if extension_server_port:
        args.extend(["--extension_server_port", str(extension_server_port)])
    
    env = {
        **os.environ,
        "ANTIGRAVITY_EDITOR_APP_ROOT": "/usr/share/antigravity/resources/app",
    }
    
    # Remove debug noise
    env.pop("GODEBUG", None)
    
    print(f"[Launcher] Starting LS on port {port}")
    print(f"[Launcher] CSRF: {csrf_token}")
    print(f"[Launcher] Auth token: {auth_token[:20]}...{auth_token[-10:]}")
    
    # Build protobuf metadata
    metadata = build_management_metadata(
        auth_token=auth_token,
        auth_uid=auth_uid,
        service_key=service_key,
    )
    print(f"[Launcher] Metadata size: {len(metadata)} bytes")
    if verbose:
        print(f"[Launcher] Metadata hex: {metadata.hex()}")
    
    # Launch LS
    proc = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE if not verbose else None,
        stderr=subprocess.PIPE if not verbose else None,
        env=env,
    )
    
    # Write metadata to stdin (exactly as IDE does)
    proc.stdin.write(metadata)
    proc.stdin.close()
    
    print(f"[Launcher] LS PID: {proc.pid}")
    
    return proc


def main():
    parser = argparse.ArgumentParser(description="LS Standalone Launcher")
    parser.add_argument("--port", type=int, default=29501, help="Server port")
    parser.add_argument("--token", type=str, help="OAuth access token")
    parser.add_argument("--from-ide", action="store_true",
                        help="Read token from IDE's state.vscdb")
    parser.add_argument("--auto-token", action="store_true",
                        help="Auto-extract token from running LS")
    parser.add_argument("--workspace", type=str, default="standalone_test")
    parser.add_argument("--ext-port", type=int, default=None,
                        help="IDE extension server port (enables OAuth)")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--wait", type=int, default=5,
                        help="Seconds to wait before checking status")
    args = parser.parse_args()
    
    # Get token
    token = args.token
    if not token and args.from_ide:
        from mekhane.ochema.fake_extension_server import read_token_from_ide
        print("[Launcher] Reading OAuth token from IDE state.vscdb...")
        token_info = read_token_from_ide()
        if token_info:
            token = token_info.access_token
            print(f"[Launcher] Found token: {token[:20]}... (expiry: {token_info.expiry_seconds})")
        else:
            print("[Launcher] ERROR: No token found in state.vscdb")
            sys.exit(1)
    elif not token and args.auto_token:
        print("[Launcher] Extracting OAuth token from running LS...")
        token = get_current_oauth_token()
        if token:
            print(f"[Launcher] Found token: {token[:20]}...")
        else:
            print("[Launcher] ERROR: No token found in running LS")
            sys.exit(1)
    
    if not token:
        print("[Launcher] ERROR: --token, --from-ide, or --auto-token required")
        sys.exit(1)
    
    # Launch
    proc = launch_ls(
        port=args.port,
        auth_token=token,
        workspace_id=args.workspace,
        verbose=args.verbose,
        extension_server_port=args.ext_port,
    )
    
    # Wait and check
    print(f"[Launcher] Waiting {args.wait}s for startup...")
    time.sleep(args.wait)
    
    if proc.poll() is not None:
        print(f"[Launcher] FAILED - LS exited with code {proc.returncode}")
        if proc.stderr:
            stderr = proc.stderr.read().decode("utf-8", errors="replace")
            # Show last 1000 chars
            print(f"[Launcher] stderr (last 1000 chars):\n{stderr[-1000:]}")
        sys.exit(1)
    else:
        print(f"[Launcher] SUCCESS - LS running on port {args.port}")
        # Check listening ports
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True, text=True,
        )
        for line in result.stdout.split("\n"):
            if str(proc.pid) in line:
                print(f"  {line.strip()}")
        
        print(f"\n[Launcher] To test: curl -s http://127.0.0.1:{args.port}/")
        print(f"[Launcher] To stop: kill {proc.pid}")
        
        # Keep running
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.send_signal(signal.SIGTERM)
            proc.wait()
            print("\n[Launcher] LS stopped.")


if __name__ == "__main__":
    main()
