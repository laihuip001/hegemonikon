import sys
import json
import subprocess
import threading
import time
from typing import Optional, Dict, Any, List

class MCPClientError(Exception):
    pass

class SimpleMCPClient:
    """A simple synchronous MCP client over stdio."""

    def __init__(self, command: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None):
        self.command = command
        self.cwd = cwd
        self.env = env
        self.process = None
        self._seq = 0
        self._responses = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        """Start the MCP server process."""
        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr, # Redirect stderr to main stderr for logging
                cwd=self.cwd,
                env=self.env,
                text=True,
                bufsize=1
            )
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
        except Exception as e:
            raise MCPClientError(f"Failed to start server: {e}")

    def stop(self):
        """Stop the MCP server process."""
        self._running = False
        if self.process:
            if self.process.stdin:
                try:
                    self.process.stdin.close()
                except:
                    pass
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def _read_loop(self):
        """Background thread to read stdout from server."""
        while self._running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                self._handle_message(line)
            except Exception:
                break

    def _handle_message(self, line: str):
        """Process incoming JSON-RPC message."""
        try:
            msg = json.loads(line)
            if "id" in msg and msg["id"] is not None:
                with self._lock:
                    self._responses[msg["id"]] = msg
        except json.JSONDecodeError:
            pass

    def _send_request(self, method: str, params: Optional[Dict] = None) -> Any:
        """Send a JSON-RPC request and wait for result."""
        if not self.process:
            raise MCPClientError("Server not running")

        req_id = self._seq
        self._seq += 1

        req = {
            "jsonrpc": "2.0",
            "method": method,
            "id": req_id
        }
        if params is not None:
            req["params"] = params

        try:
            json_str = json.dumps(req)
            self.process.stdin.write(json_str + "\n")
            self.process.stdin.flush()
        except Exception as e:
            raise MCPClientError(f"Failed to send request: {e}")

        # Wait for response
        start_time = time.time()
        while time.time() - start_time < 30: # 30s timeout
            with self._lock:
                if req_id in self._responses:
                    resp = self._responses.pop(req_id)
                    if "error" in resp:
                        raise MCPClientError(f"RPC Error: {resp['error']}")
                    return resp.get("result")
            time.sleep(0.01)

        raise MCPClientError("Timeout waiting for response")

    def _send_notification(self, method: str, params: Optional[Dict] = None):
         """Send a JSON-RPC notification."""
         if not self.process:
            raise MCPClientError("Server not running")

         req = {
            "jsonrpc": "2.0",
            "method": method
         }
         if params is not None:
             req["params"] = params

         try:
            json_str = json.dumps(req)
            self.process.stdin.write(json_str + "\n")
            self.process.stdin.flush()
         except Exception as e:
            raise MCPClientError(f"Failed to send notification: {e}")

    def initialize(self):
        """Perform MCP handshake."""
        # 1. Send initialize
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {"name": "prompt-lang-client", "version": "1.0.0"}
        }
        res = self._send_request("initialize", init_params)

        # 2. Send initialized notification
        self._send_notification("notifications/initialized")
        return res

    def list_tools(self) -> List[Dict]:
        """List available tools."""
        res = self._send_request("tools/list")
        return res.get("tools", [])

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool."""
        params = {
            "name": name,
            "arguments": arguments
        }
        res = self._send_request("tools/call", params)
        # Result typically has 'content' list
        return res
