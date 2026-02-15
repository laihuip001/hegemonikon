"""Fake Extension Server — ConnectRPC over HTTP.

LS は ConnectRPC (extension_server_go_proto_connect) で Extension Server に接続する。
ConnectRPC は HTTP POST + protobuf body (Unary) / SSE (Server Streaming) を使う。
このスクリプトは最小限の ConnectRPC サーバーを HTTP で実装する。

Usage:
    python fake_extension_server.py --port 50051 --auto-token -v
    python fake_extension_server.py --port 50051 --token "ya29.xxx"
"""
from __future__ import annotations

import argparse
import http.server
import io
import json
import logging
import os
import ssl
import struct
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

logger = logging.getLogger("fake-ext-server")

# ====== Protobuf Manual Encoding ======
# proto definition を使わず、バイナリを直接組み立てる

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

def _encode_map_entry(key: str, value: str) -> bytes:
    """Encode a single map<string, Primitive> entry.
    
    Primitive は oneof:
      bool_value = 1
      int32_value = 2  
      string_value = 3  ← これを使う
    """
    # Primitive message: string_value (field 3) = value
    primitive = _encode_string_field(3, value)
    # Map entry: key (field 1) = key, value (field 2) = Primitive submessage
    return _encode_string_field(1, key) + _encode_submessage_field(2, primitive)

def encode_topic(data: dict[str, str]) -> bytes:
    """Encode Topic { map<string, Primitive> data = 1 }."""
    result = b""
    for k, v in data.items():
        entry = _encode_map_entry(k, v)
        result += _encode_submessage_field(1, entry)
    return result

def encode_unified_state_sync_update_initial(data: dict[str, str]) -> bytes:
    """Encode UnifiedStateSyncUpdate { Topic initial_state = 1 }."""
    topic = encode_topic(data)
    return _encode_submessage_field(1, topic)

def decode_subscribe_request(data: bytes) -> str:
    """Decode SubscribeToUnifiedStateSyncTopicRequest { string topic = 1 }."""
    offset = 0
    while offset < len(data):
        tag_value, offset = _varint_decode(data, offset)
        field_number = tag_value >> 3
        wire_type = tag_value & 0x07
        if wire_type == 2:  # length-delimited
            length, offset = _varint_decode(data, offset)
            field_data = data[offset:offset + length]
            offset += length
            if field_number == 1:
                return field_data.decode("utf-8")
    return ""

def encode_connect_streaming_message(payload: bytes) -> bytes:
    """ConnectRPC streaming envelope: flags(1) + length(4) + data."""
    flags = 0  # no compression
    length = len(payload)
    return struct.pack(">bI", flags, length) + payload

def encode_connect_end_stream() -> bytes:
    """ConnectRPC end-of-stream trailer."""
    trailer = json.dumps({"metadata": {}}).encode("utf-8")
    flags = 2  # end stream flag
    length = len(trailer)
    return struct.pack(">bI", flags, length) + trailer

# ====== ConnectRPC Handler ======

class FakeExtensionServerHandler(http.server.BaseHTTPRequestHandler):
    """ConnectRPC compatible HTTP handler."""

    # Class-level shared state
    _token: str = ""
    _lock = threading.Lock()
    _token_update_events: list[threading.Event] = []

    @classmethod
    def set_token(cls, token: str) -> None:
        cls._token = token
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

        # Route to handler
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
            self._handle_ls_started(body)
        elif method == "PushUnifiedStateSyncUpdate":
            self._handle_push_update(body)
        elif method == "RecordError":
            self._handle_record_error(body)
        else:
            # Generic empty response for unimplemented methods
            logger.debug("Unimplemented method: %s (returning empty)", method) 
            self._send_unary_response(b"")

    def _handle_subscribe(self, body: bytes):
        """Handle ServerStreaming: SubscribeToUnifiedStateSyncTopic."""
        topic = decode_subscribe_request(body)
        logger.info("LS subscribes to topic: '%s'", topic)

        # ConnectRPC Server Streaming uses:
        # Content-Type: application/connect+proto
        # Body: series of envelope frames (flags + length + data)
        self.send_response(200)
        self.send_header("Content-Type", "application/connect+proto")
        self.end_headers()

        # Send initial state
        data = self._get_topic_data(topic)
        initial = encode_unified_state_sync_update_initial(data)
        envelope = encode_connect_streaming_message(initial)
        self.wfile.write(envelope)
        self.wfile.flush()
        logger.info("Sent initial state for topic '%s': %d entries", topic, len(data))

        # Keep stream alive
        ev = threading.Event()
        with self._lock:
            self._token_update_events.append(ev)

        try:
            while True:
                ev.wait(timeout=30)
                if ev.is_set():
                    ev.clear()
                    if topic == "api_key":
                        update = encode_unified_state_sync_update_initial(
                            {"api_key": self._token}
                        )
                        self.wfile.write(encode_connect_streaming_message(update))
                        self.wfile.flush()
                        logger.info("Pushed token update")
        except (BrokenPipeError, ConnectionResetError):
            logger.info("Client disconnected from topic '%s'", topic)
        finally:
            with self._lock:
                self._token_update_events.remove(ev)

    def _handle_ls_started(self, body: bytes):
        logger.info("LS reported: started")
        self._send_unary_response(b"")

    def _handle_push_update(self, body: bytes):
        logger.debug("LS pushed state update")
        self._send_unary_response(b"")

    def _handle_record_error(self, body: bytes):
        logger.warning("LS reported error (%d bytes)", len(body))
        self._send_unary_response(b"")

    def _send_unary_response(self, payload: bytes):
        """Send ConnectRPC unary response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/proto")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _get_topic_data(self, topic: str) -> dict[str, str]:
        if topic == "uss-oauth":
            return {"access_token": self._token}
        elif topic == "api_key":
            return {"api_key": self._token}
        elif topic == "experiments":
            return {}
        elif topic == "settings":
            return {}
        elif topic == "user_status":
            return {"name": "standalone", "email": "standalone@local"}
        else:
            logger.warning("Unknown topic: %s", topic)
            return {}


def get_gcloud_token(account: str | None = None) -> str:
    """gcloud CLI から OAuth token を取得."""
    cmd = ["gcloud", "auth", "print-access-token"]
    if account:
        cmd.extend(["--account", account])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        raise RuntimeError(f"gcloud failed: {result.stderr}")
    return result.stdout.strip()


def serve(port: int, token: str) -> http.server.HTTPServer:
    """HTTP サーバー起動."""
    FakeExtensionServerHandler.set_token(token)
    server = http.server.HTTPServer(("127.0.0.1", port), FakeExtensionServerHandler)
    logger.info("Fake Extension Server (ConnectRPC/HTTP) running on port %d", port)
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Fake Extension Server (ConnectRPC)")
    parser.add_argument("--port", type=int, default=50051)
    parser.add_argument("--token", type=str, default="")
    parser.add_argument("--account", type=str, default=None)
    parser.add_argument("--auto-token", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    if args.auto_token or not args.token:
        token = get_gcloud_token(args.account)
        logger.info("Got token from gcloud (%d chars)", len(token))
    else:
        token = args.token

    server = serve(args.port, token)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
