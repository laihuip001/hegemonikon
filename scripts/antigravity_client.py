#!/usr/bin/env python3
"""Antigravity LLM Client — 4-Step API Wrapper.

PURPOSE: Antigravity IDE の Language Server API を外部から呼び出し、
LLM テキスト生成を行う Python クライアント。

4-Step Flow:
  1. StartCascade        → cascadeId
  2. SendUserCascadeMessage → {} (非同期受理)
  3. GetAllCascadeTrajectories → trajectoryId
  4. GetCascadeTrajectorySteps → response text

Usage:
  python scripts/antigravity_client.py "Your prompt here"
  python scripts/antigravity_client.py --model MODEL_GEMINI_2_5_PRO "Hello"
  python scripts/antigravity_client.py --json "Explain FEP"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import ssl
from dataclasses import dataclass, field
from typing import Any


# -- Constants --

DEFAULT_MODEL = "MODEL_CLAUDE_4_5_SONNET_THINKING"
BASE_PATH = "/exa.language_server_pb.LanguageServerService"
POLL_INTERVAL = 1.0  # seconds
POLL_TIMEOUT = 120.0  # seconds
WS_FILTER = os.environ.get("AGQ_WORKSPACE", "hegemonikon")

# Known models (from walkthrough)
MODELS = {
    "claude-sonnet": "MODEL_CLAUDE_4_5_SONNET_THINKING",
    "claude-opus": "MODEL_PLACEHOLDER_M26",
    "gemini-pro": "MODEL_GEMINI_2_5_PRO",
    "gemini-flash": "MODEL_GEMINI_2_5_FLASH",
    "gpt-4.1": "MODEL_GPT_4_1",
}


@dataclass
class LSConnection:
    """Language Server connection info."""

    pid: int
    csrf_token: str
    port: int


@dataclass
class LLMResponse:
    """Parsed LLM response."""

    response: str = ""
    thinking: str = ""
    model: str = ""
    status: str = ""
    cascade_id: str = ""
    trajectory_id: str = ""
    raw_steps: list[dict] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [self.response]
        if self.thinking:
            lines.append(f"\n[thinking] {self.thinking[:200]}...")
        lines.append(f"[model: {self.model}]")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "response": self.response,
            "thinking": self.thinking,
            "model": self.model,
            "status": self.status,
            "cascade_id": self.cascade_id,
            "trajectory_id": self.trajectory_id,
        }


class AntigravityClient:
    """Antigravity Language Server LLM client."""

    def __init__(self, workspace: str = WS_FILTER, verbose: bool = False):
        self.workspace = workspace
        self.verbose = verbose
        self._conn: LSConnection | None = None
        # Disable SSL verification (self-signed cert)
        self._ssl_ctx = ssl.create_default_context()
        self._ssl_ctx.check_hostname = False
        self._ssl_ctx.verify_mode = ssl.CERT_NONE

    @property
    def conn(self) -> LSConnection:
        if self._conn is None:
            self._conn = self._detect_ls()
        return self._conn

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[agq] {msg}", file=sys.stderr)

    # -- LS Detection --

    def _detect_ls(self) -> LSConnection:
        """Detect Language Server process, CSRF token, and HTTPS port.

        Replicates the logic from agq-check.sh:
        1. ps aux | grep language_server_linux | grep <workspace>
        2. /proc/<PID>/cmdline → --csrf_token
        3. ss -tlnp | grep pid=<PID> → ports
        4. Try each port with GetUserStatus to find the right one
        """
        self._log(f"Detecting LS (workspace={self.workspace})")

        # Step 1: Find process
        try:
            ps_out = subprocess.check_output(
                ["ps", "aux"], text=True, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ps command failed: {e}") from e

        proc_line = None
        for line in ps_out.splitlines():
            if "language_server_linux" in line and self.workspace in line and "grep" not in line:
                proc_line = line
                break

        if not proc_line:
            raise RuntimeError(
                f"Language Server process not found (workspace: {self.workspace})"
            )

        pid = int(proc_line.split()[1])
        self._log(f"Found LS PID: {pid}")

        # Step 2: Get CSRF token from /proc/PID/cmdline
        csrf = self._get_csrf_from_cmdline(pid)
        if not csrf:
            # Fallback: grep from ps output
            m = re.search(r"csrf_token\s+(\S+)", proc_line)
            if m:
                csrf = m.group(1)
        if not csrf:
            raise RuntimeError(f"CSRF token not found for PID {pid}")
        self._log(f"CSRF token: {csrf[:8]}...")

        # Step 3: Get listening ports
        ports = self._get_ports(pid)
        if not ports:
            raise RuntimeError(f"No listening ports found for PID {pid}")
        self._log(f"Candidate ports: {ports}")

        # Step 4: Try each port with a simple API call
        for port in ports:
            try:
                result = self._raw_call(port, csrf, "/GetUserStatus", {
                    "metadata": {
                        "ideName": "antigravity",
                        "extensionName": "antigravity",
                        "locale": "en",
                    }
                })
                if result and "userStatus" in result:
                    self._log(f"HTTPS port confirmed: {port}")
                    return LSConnection(pid=pid, csrf_token=csrf, port=port)
            except Exception:
                continue

        raise RuntimeError(
            f"Could not connect to LS on any port ({ports})"
        )

    def _get_csrf_from_cmdline(self, pid: int) -> str | None:
        """Read CSRF token from /proc/<PID>/cmdline."""
        cmdline_path = f"/proc/{pid}/cmdline"
        try:
            with open(cmdline_path, "rb") as f:
                raw = f.read()
            args = raw.split(b"\x00")
            for i, arg in enumerate(args):
                if arg == b"--csrf_token" and i + 1 < len(args):
                    return args[i + 1].decode("utf-8")
                # Also check combined form: --csrf_token=VALUE
                if arg.startswith(b"--csrf_token="):
                    return arg.split(b"=", 1)[1].decode("utf-8")
        except (OSError, PermissionError):
            pass
        return None

    def _get_ports(self, pid: int) -> list[int]:
        """Get listening ports for a process via ss."""
        try:
            ss_out = subprocess.check_output(
                ["ss", "-tlnp"], text=True, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            return []

        ports = []
        for line in ss_out.splitlines():
            if f"pid={pid}" in line:
                m = re.search(r"127\.0\.0\.1:(\d+)", line)
                if m:
                    ports.append(int(m.group(1)))
        return sorted(set(ports))

    # -- API Calls --

    def _raw_call(self, port: int, csrf: str, endpoint: str, payload: dict) -> dict:
        """Make a raw ConnectRPC JSON request."""
        url = f"https://127.0.0.1:{port}{BASE_PATH}{endpoint}"
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("x-codeium-csrf-token", csrf)
        req.add_header("Connect-Protocol-Version", "1")

        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body.strip() else {}

    def _call(self, endpoint: str, payload: dict) -> dict:
        """Make a ConnectRPC JSON request using detected connection."""
        c = self.conn
        self._log(f"POST {endpoint}")
        return self._raw_call(c.port, c.csrf_token, endpoint, payload)

    # -- 4-Step Flow --

    def start_cascade(self) -> str:
        """Step 1: Start a new cascade session.

        Returns: cascadeId
        """
        result = self._call("/StartCascade", {"source": 1})
        cascade_id = result.get("cascadeId", "")
        if not cascade_id:
            raise RuntimeError(f"StartCascade failed: {result}")
        self._log(f"cascadeId: {cascade_id}")
        return cascade_id

    def send_message(
        self,
        cascade_id: str,
        prompt: str,
        model: str = DEFAULT_MODEL,
    ) -> dict:
        """Step 2: Send a user message to the cascade.

        Returns: {} (async acknowledgement)
        """
        payload = {
            "cascadeId": cascade_id,
            "items": [{"text": prompt}],
            "cascadeConfig": {
                "plannerConfig": {
                    "conversational": {},
                    "planModel": model,
                }
            },
        }
        return self._call("/SendUserCascadeMessage", payload)

    def get_trajectory(self, cascade_id: str) -> str:
        """Step 3: Get the trajectory ID for a cascade.

        Returns: trajectoryId
        """
        result = self._call("/GetAllCascadeTrajectories", {})
        summaries = result.get("trajectorySummaries", {})
        cascade_summary = summaries.get(cascade_id)
        if not cascade_summary:
            raise RuntimeError(
                f"No trajectory found for cascadeId={cascade_id}. "
                f"Available: {list(summaries.keys())}"
            )
        tid = cascade_summary.get("trajectoryId", "")
        if not tid:
            raise RuntimeError(f"trajectoryId empty for cascadeId={cascade_id}")
        self._log(f"trajectoryId: {tid}")
        return tid

    def get_steps(self, cascade_id: str, trajectory_id: str) -> dict:
        """Step 4: Get all steps of a trajectory.

        Returns: full response including steps and status
        """
        return self._call("/GetCascadeTrajectorySteps", {
            "cascadeId": cascade_id,
            "trajectoryId": trajectory_id,
        })

    def _parse_response(
        self, steps_result: dict, cascade_id: str, trajectory_id: str
    ) -> LLMResponse:
        """Parse the steps result into an LLMResponse.

        Response structure (from live API analysis):
        - status is at STEP level: step["status"] = "CORTEX_STEP_STATUS_DONE"
        - generatorModel is at step["metadata"]["generatorModel"]
        - response text is at step["plannerResponse"]["response"]
        """
        steps = steps_result.get("steps", [])

        resp = LLMResponse(
            cascade_id=cascade_id,
            trajectory_id=trajectory_id,
            raw_steps=steps,
        )

        # Find the PLANNER_RESPONSE step
        for step in steps:
            if step.get("type") == "CORTEX_STEP_TYPE_PLANNER_RESPONSE":
                # Status is at step level
                resp.status = step.get("status", "")
                # Model is in step.metadata
                metadata = step.get("metadata", {})
                resp.model = metadata.get("generatorModel", "")
                # Response text is in plannerResponse
                pr = step.get("plannerResponse", {})
                resp.response = pr.get("response", "") or pr.get("modifiedResponse", "")
                resp.thinking = pr.get("thinking", "")
                break

        return resp

    # -- Unified Interface --

    def ask(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        timeout: float = POLL_TIMEOUT,
        poll_interval: float = POLL_INTERVAL,
    ) -> LLMResponse:
        """Send a prompt and wait for the LLM response.

        This is the main entry point combining all 4 steps with polling.

        Args:
            prompt: The text prompt to send.
            model: Model enum string (e.g. MODEL_CLAUDE_4_5_SONNET_THINKING).
            timeout: Maximum wait time in seconds.
            poll_interval: Polling interval in seconds.

        Returns:
            LLMResponse with the generated text.
        """
        # Step 1: Start cascade
        cascade_id = self.start_cascade()

        # Step 2: Send message
        self.send_message(cascade_id, prompt, model)
        self._log("Message sent, polling for response...")

        # Step 3+4: Poll until planner response is DONE
        start_time = time.time()
        trajectory_id = None

        while time.time() - start_time < timeout:
            time.sleep(poll_interval)

            # Try to get trajectory (may not exist yet)
            try:
                if trajectory_id is None:
                    trajectory_id = self.get_trajectory(cascade_id)
            except RuntimeError:
                self._log("Trajectory not ready yet...")
                continue

            # Get steps and check planner response status
            try:
                result = self.get_steps(cascade_id, trajectory_id)
                steps = result.get("steps", [])

                for step in steps:
                    if step.get("type") == "CORTEX_STEP_TYPE_PLANNER_RESPONSE":
                        step_status = step.get("status", "")
                        self._log(f"Planner status: {step_status}")

                        # DONE = response complete
                        if step_status == "CORTEX_STEP_STATUS_DONE":
                            return self._parse_response(
                                result, cascade_id, trajectory_id
                            )

                        # Fallback: if response text exists, accept it
                        pr = step.get("plannerResponse", {})
                        if pr.get("response"):
                            self._log("Response text found (status not DONE)")
                            return self._parse_response(
                                result, cascade_id, trajectory_id
                            )
                        break  # Found planner step but not ready

            except Exception as e:
                self._log(f"Poll error: {e}")
                continue

        raise TimeoutError(
            f"LLM response not received within {timeout}s "
            f"(cascadeId={cascade_id})"
        )


def resolve_model(name: str) -> str:
    """Resolve a model alias or validate a model enum string."""
    if name in MODELS:
        return MODELS[name]
    if name.startswith("MODEL_"):
        return name
    # Fuzzy match
    lower = name.lower()
    for alias, model_id in MODELS.items():
        if lower in alias:
            return model_id
    return name  # Pass through, let the API validate


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Antigravity LLM Client — send prompts to the IDE's Language Server"
    )
    parser.add_argument("prompt", nargs="?", help="Text prompt to send")
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL}). "
        f"Aliases: {', '.join(MODELS.keys())}",
    )
    parser.add_argument(
        "--json", "-j", action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output to stderr",
    )
    parser.add_argument(
        "--workspace", "-w",
        default=WS_FILTER,
        help=f"Workspace filter (default: {WS_FILTER})",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=float, default=POLL_TIMEOUT,
        help=f"Timeout in seconds (default: {POLL_TIMEOUT})",
    )
    parser.add_argument(
        "--detect", action="store_true",
        help="Only detect LS and print connection info",
    )
    parser.add_argument(
        "--models", action="store_true",
        help="List available model aliases",
    )

    args = parser.parse_args()

    if args.models:
        print("Available model aliases:")
        for alias, model_id in MODELS.items():
            marker = " ← default" if model_id == DEFAULT_MODEL else ""
            print(f"  {alias:20s} → {model_id}{marker}")
        return

    client = AntigravityClient(workspace=args.workspace, verbose=args.verbose)

    if args.detect:
        conn = client.conn
        info = {
            "pid": conn.pid,
            "port": conn.port,
            "csrf_token": conn.csrf_token[:8] + "...",
        }
        print(json.dumps(info, indent=2))
        return

    if not args.prompt:
        # Read from stdin if no prompt argument
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(1)
        prompt = sys.stdin.read().strip()
    else:
        prompt = args.prompt

    if not prompt:
        print("Error: empty prompt", file=sys.stderr)
        sys.exit(1)

    model = resolve_model(args.model)
    try:
        response = client.ask(prompt, model=model, timeout=args.timeout)
    except (RuntimeError, TimeoutError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(response.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(response)


if __name__ == "__main__":
    main()
