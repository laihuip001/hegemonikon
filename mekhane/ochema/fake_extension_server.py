# PROOF: [L2/Auto] <- Default PROOF Header
"""Fake Extension Server — ConnectRPC over HTTP.

LS は ConnectRPC (extension_server_go_proto_connect) で Extension Server に接続する。
ConnectRPC は HTTP POST + protobuf body (Unary) / SSE (Server Streaming) を使う。
このスクリプトは最小限の ConnectRPC サーバーを HTTP で実装する。

解明済みデータ構造 (2026-02-15):
  - Topic.data["oauthTokenInfoSentinelKey"] = Primitive{field_1: Base64(OAuthTokenInfo binary)}
  - OAuthTokenInfo: access_token(1), token_type(2), refresh_token(3), expiry(4=Timestamp)
  - State.vscdb: Base64(Topic proto binary) で永続化
  - LS stdin metadata: access_token を field 1 string で送信

Usage:
    python fake_extension_server.py --port 50051 --from-ide -v
    python fake_extension_server.py --port 50051 --token "ya29.xxx"
"""
from __future__ import annotations

import argparse
import base64
import http.server
import json
import logging
import os
import sqlite3
import struct
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

logger = logging.getLogger("fake-ext-server")

# ====== Protobuf Manual Encoding ======

def _varint_encode(value: int) -> bytes:
    result = []
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)

def _varint_decode(data: bytes, offset: int = 0) -> tuple[int, int]:
    result = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80):
            break
        shift += 7
    return result, offset

def _encode_string_field(field_number: int, value: str) -> bytes:
    if not value:
        return b""
    tag = _varint_encode((field_number << 3) | 2)
    data = value.encode("utf-8")
    return tag + _varint_encode(len(data)) + data

def _encode_submessage_field(field_number: int, submsg: bytes) -> bytes:
    if not submsg:
        return b""
    tag = _varint_encode((field_number << 3) | 2)
    return tag + _varint_encode(len(submsg)) + submsg

def decode_subscribe_request(data: bytes) -> str:
    """Decode SubscribeToUnifiedStateSyncTopicRequest { string topic = 1 }.
    
    ConnectRPC streaming: body is envelope (flags[1] + len[4] + proto).
    """
    # Strip streaming envelope if present
    if len(data) > 5:
        proto_body = data[5:]
    else:
        proto_body = data
    
    offset = 0
    while offset < len(proto_body):
        tag_value, offset = _varint_decode(proto_body, offset)
        field_number = tag_value >> 3
        wire_type = tag_value & 0x07
        if wire_type == 2:  # length-delimited
            length, offset = _varint_decode(proto_body, offset)
            field_data = proto_body[offset:offset + length]
            offset += length
            if field_number == 1:
                return field_data.decode("utf-8")
    return ""

def encode_connect_streaming_message(payload: bytes) -> bytes:
    """ConnectRPC streaming envelope: flags(1) + length(4) + data."""
    flags = 0  # no compression
    length = len(payload)
    return struct.pack(">bI", flags, length) + payload


# ====== OAuth Token Management ======

class OAuthTokenInfo:
    """OAuthTokenInfo protobuf structure."""
    
    def __init__(
        self,
        access_token: str,
        token_type: str = "Bearer",
        refresh_token: str = "",
        expiry_seconds: int = 0,
    ):
        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.expiry_seconds = expiry_seconds
    
    def to_proto_bytes(self) -> bytes:
        """Serialize to protobuf binary.
        
        message OAuthTokenInfo {
            string access_token = 1;
            string token_type = 2;
            string refresh_token = 3;
            google.protobuf.Timestamp expiry = 4;
        }
        """
        result = _encode_string_field(1, self.access_token)
        result += _encode_string_field(2, self.token_type)
        if self.refresh_token:
            result += _encode_string_field(3, self.refresh_token)
        if self.expiry_seconds:
            # Timestamp { int64 seconds = 1 }
            ts_body = _varint_encode((1 << 3) | 0) + _varint_encode(self.expiry_seconds)
            result += _encode_submessage_field(4, ts_body)
        return result

    @classmethod
    def from_proto_bytes(cls, data: bytes) -> OAuthTokenInfo:
        """Deserialize from protobuf binary."""
        access_token = ""
        token_type = ""
        refresh_token = ""
        expiry_seconds = 0
        
        p = 0
        while p < len(data):
            tag, p = _varint_decode(data, p)
            field = tag >> 3
            wire = tag & 0x07
            if wire == 2:
                length, p = _varint_decode(data, p)
                fdata = data[p:p+length]
                p += length
                if field == 1:
                    access_token = fdata.decode("utf-8")
                elif field == 2:
                    token_type = fdata.decode("utf-8")
                elif field == 3:
                    refresh_token = fdata.decode("utf-8")
                elif field == 4:
                    # Parse Timestamp
                    tp = 0
                    while tp < len(fdata):
                        tt, tp = _varint_decode(fdata, tp)
                        tf = tt >> 3
                        tw = tt & 0x07
                        if tw == 0:
                            v, tp = _varint_decode(fdata, tp)
                            if tf == 1:
                                expiry_seconds = v
                        else:
                            break
            elif wire == 0:
                _, p = _varint_decode(data, p)
        
        return cls(access_token, token_type, refresh_token, expiry_seconds)


# Key used in Topic.data map for OAuth token info
OAUTH_SENTINEL_KEY = "oauthTokenInfoSentinelKey"


def build_uss_oauth_topic(token_info: OAuthTokenInfo) -> bytes:
    """Build Topic protobuf for uss-oauth.
    
    Structure (verified via JS source analysis):
      Topic.data["oauthTokenInfoSentinelKey"] = Primitive{field_1: Base64(OAuthTokenInfo binary)}
    
    Where Primitive.field_1 contains Base64-encoded OAuthTokenInfo protobuf.
    """
    # OAuthTokenInfo → proto binary → Base64
    oauth_binary = token_info.to_proto_bytes()
    oauth_b64 = base64.b64encode(oauth_binary)
    
    # Primitive with field 1 = Base64 bytes (wire type 2)
    primitive = _encode_submessage_field(1, oauth_b64)
    
    # Map entry: key (field 1) + Primitive (field 2)
    map_entry = _encode_string_field(1, OAUTH_SENTINEL_KEY) + _encode_submessage_field(2, primitive)
    
    # Topic { map<string, Primitive> data = 1 }
    topic = _encode_submessage_field(1, map_entry)
    return topic


def read_token_from_ide() -> OAuthTokenInfo | None:
    """IDE の state.vscdb から OAuth トークンを読み取る."""
    db_path = Path.home() / ".config" / "Antigravity" / "User" / "globalStorage" / "state.vscdb"
    if not db_path.exists():
        logger.warning("state.vscdb not found: %s", db_path)
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        row = conn.execute(
            "SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.oauthToken'"
        ).fetchone()
        conn.close()
        
        if not row:
            logger.warning("No oauthToken entry in state.vscdb")
            return None
        
        # Decode base64 → Topic proto binary
        topic_bytes = base64.b64decode(row[0])
        
        # Navigate: Topic → map entry → Primitive → inner base64 → OAuthTokenInfo
        _, map_entry, p = _read_proto_field(topic_bytes, 0)
        _, _, p2 = _read_proto_field(map_entry, 0)   # key
        _, primitive, _ = _read_proto_field(map_entry, p2)  # Primitive
        _, inner_b64, _ = _read_proto_field(primitive, 0)   # field 1 = base64 data
        
        # Base64 decode → OAuthTokenInfo proto
        inner = base64.b64decode(inner_b64)
        return OAuthTokenInfo.from_proto_bytes(inner)
    
    except Exception as e:
        logger.error("Failed to read token from state.vscdb: %s", e)
        return None


def _read_proto_field(data: bytes, offset: int) -> tuple[int, bytes, int]:
    """Read a single proto field (wire type 2 only)."""
    tag, offset = _varint_decode(data, offset)
    field = tag >> 3
    wire = tag & 0x07
    if wire == 2:
        length, offset = _varint_decode(data, offset)
        return field, data[offset:offset + length], offset + length
    elif wire == 0:
        val, offset = _varint_decode(data, offset)
        return field, val.to_bytes(8, 'little'), offset
    return field, b"", offset


# ====== ConnectRPC Handler ======

class FakeExtensionServerHandler(http.server.BaseHTTPRequestHandler):
    """ConnectRPC compatible HTTP handler."""

    # Class-level shared state
    _token_info: OAuthTokenInfo | None = None
    _topic_cache: dict[str, bytes] = {}
    _lock = threading.Lock()
    _token_update_events: list[threading.Event] = []

    @classmethod
    def set_token_info(cls, info: OAuthTokenInfo) -> None:
        cls._token_info = info
        # Pre-build uss-oauth topic for performance
        cls._topic_cache["uss-oauth"] = build_uss_oauth_topic(info)
        with cls._lock:
            for ev in cls._token_update_events:
                ev.set()

    def log_message(self, format, *args):
        logger.debug("HTTP: %s", format % args)

    def do_POST(self):
        path = self.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        logger.info("POST %s (%d bytes)", path, len(body))

        svc = "/exa.extension_server_pb.ExtensionServerService/"
        if path.startswith(svc):
            method = path[len(svc):]
            self._handle_rpc(method, body)
        else:
            self.send_error(404, f"Unknown path: {path}")

    def _handle_rpc(self, method: str, body: bytes):
        if method == "SubscribeToUnifiedStateSyncTopic":
            self._handle_subscribe(body)
        elif method == "LanguageServerStarted":
            logger.info("LS reported: started")
            self._send_unary_response(b"")
        elif method == "PushUnifiedStateSyncUpdate":
            logger.debug("LS pushed state update")
            self._send_unary_response(b"")
        elif method == "RecordError":
            logger.warning("LS reported error (%d bytes)", len(body))
            self._send_unary_response(b"")
        else:
            logger.debug("Unimplemented method: %s (returning empty)", method) 
            self._send_unary_response(b"")

    def _handle_subscribe(self, body: bytes):
        """Handle ServerStreaming: SubscribeToUnifiedStateSyncTopic."""
        topic = decode_subscribe_request(body)
        logger.info("LS subscribes to topic: '%s'", topic)

        self.send_response(200)
        self.send_header("Content-Type", "application/connect+proto")
        self.end_headers()

        # Build and send initial state
        topic_bytes = self._get_topic_bytes(topic)
        update = _encode_submessage_field(1, topic_bytes)  # UnifiedStateSyncUpdate.initial_state
        envelope = encode_connect_streaming_message(update)
        self.wfile.write(envelope)
        self.wfile.flush()
        logger.info("Sent initial state for topic '%s' (%d bytes)", topic, len(topic_bytes))

        # Keep stream alive for token updates
        ev = threading.Event()
        with self._lock:
            self._token_update_events.append(ev)

        try:
            while True:
                ev.wait(timeout=30)
                if ev.is_set():
                    ev.clear()
                    if topic == "uss-oauth":
                        topic_bytes = self._get_topic_bytes(topic)
                        update = _encode_submessage_field(1, topic_bytes)
                        self.wfile.write(encode_connect_streaming_message(update))
                        self.wfile.flush()
                        logger.info("Pushed token update for uss-oauth")
        except (BrokenPipeError, ConnectionResetError):
            logger.info("Client disconnected from topic '%s'", topic)
        finally:
            with self._lock:
                self._token_update_events.remove(ev)

    def _send_unary_response(self, payload: bytes):
        """Send ConnectRPC unary response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/proto")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _get_topic_bytes(self, topic: str) -> bytes:
        """Get Topic proto bytes for a given topic name."""
        if topic == "uss-oauth" and "uss-oauth" in self._topic_cache:
            return self._topic_cache["uss-oauth"]
        # Empty topic for everything else
        return b""


def serve(port: int, token_info: OAuthTokenInfo) -> http.server.HTTPServer:
    """HTTP サーバー起動."""
    FakeExtensionServerHandler.set_token_info(token_info)
    server = http.server.HTTPServer(("127.0.0.1", port), FakeExtensionServerHandler)
    logger.info("Fake Extension Server (ConnectRPC/HTTP) on port %d", port)
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Fake Extension Server (ConnectRPC)")
    parser.add_argument("--port", type=int, default=50051)
    parser.add_argument("--token", type=str, default="",
                       help="Access token (ya29.xxx)")
    parser.add_argument("--from-ide", action="store_true",
                       help="Read token from IDE's state.vscdb")
    parser.add_argument("--auto-token", action="store_true",
                       help="Get token from gcloud CLI")
    parser.add_argument("--account", type=str, default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    token_info: OAuthTokenInfo | None = None

    if args.from_ide:
        token_info = read_token_from_ide()
        if token_info:
            logger.info("Got token from IDE state.vscdb (access_token: %d chars, expiry: %d)",
                       len(token_info.access_token), token_info.expiry_seconds)
        else:
            logger.error("Failed to read token from IDE")
            sys.exit(1)
    elif args.token:
        token_info = OAuthTokenInfo(access_token=args.token)
    elif args.auto_token:
        cmd = ["gcloud", "auth", "print-access-token"]
        if args.account:
            cmd.extend(["--account", args.account])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.error("gcloud auth failed: %s", result.stderr)
            sys.exit(1)
        token_info = OAuthTokenInfo(access_token=result.stdout.strip())
        logger.info("Got token from gcloud (%d chars)", len(token_info.access_token))
    else:
        # Default: try IDE first, then gcloud
        token_info = read_token_from_ide()
        if not token_info:
            logger.info("IDE token not available, trying gcloud...")
            try:
                result = subprocess.run(
                    ["gcloud", "auth", "print-access-token"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    token_info = OAuthTokenInfo(access_token=result.stdout.strip())
            except Exception:
                pass
        if not token_info:
            logger.error("No token source available. Use --from-ide or --token")
            sys.exit(1)

    server = serve(args.port, token_info)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
