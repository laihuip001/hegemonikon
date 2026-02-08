# PROOF: [L1/定理] <- mekhane/ CCL→実行基盤が必要
#!/usr/bin/env python3
"""
CCL Tracer (v1.0)
Cognitive Control Language Debugging Tool

Logs manual execution steps of CCL programs to verify logic and trace errors.
Designed for the "Human+AI Interpretation" phase of CCL v2.0.

Usage:
  python3 ccl_tracer.py start "<ccl_expression>"
  python3 ccl_tracer.py step "<op>" --status=<status> --note="<note>"
  python3 ccl_tracer.py end --status=<status>

Log Path: ~/.mekhane/logs/ccl.log
"""

import sys
import os
import datetime
import json
import argparse
from pathlib import Path
from typing import Optional

# Palette: Fixed hardcoded path to use user's home directory
LOG_DIR = Path.home() / ".mekhane" / "logs"
LOG_FILE = LOG_DIR / "ccl.log"
STATE_FILE = LOG_DIR / "ccl_state.json"


# Palette: Colors for UX
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def color_print(text: str, color: str = Colors.RESET, bold: bool = False):
    """Prints text with ANSI colors."""
    start = color
    if bold:
        start += Colors.BOLD
    print(f"{start}{text}{Colors.RESET}")


# PURPOSE: ensure_dirs — システムの処理
def ensure_dirs():
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)


# PURPOSE: load_state プロパティの取得
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


# PURPOSE: 設定/保存: save_state
def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# PURPOSE: log_entry — システムの処理
def log_entry(entry: dict):
    ensure_dirs()
    timestamp = datetime.datetime.now().isoformat()
    log_line = f"[{timestamp}] [{entry.get('type', 'INFO')}] {json.dumps(entry, ensure_ascii=False)}"

    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

    # Also print to stdout for immediate feedback (Palette: Enhanced UX)
    msg_type = entry.get("type", "INFO")
    message = entry.get("message", "")

    if msg_type == "SESSION_START":
        color_print(f"\n🚀 {message}", Colors.GREEN, bold=True)
        color_print("-" * 50, Colors.GREEN)
    elif msg_type == "SESSION_END":
        color_print("-" * 50, Colors.BLUE)
        color_print(f"🏁 {message}\n", Colors.BLUE, bold=True)
    elif msg_type == "STEP":
        status = entry.get("status", "running")
        if status == "running":
            color_print(f"  ⏳ {message}", Colors.CYAN)
        elif status == "success":
            color_print(f"  ✅ {message}", Colors.GREEN)
        elif status == "failed":
            color_print(f"  ❌ {message}", Colors.RED)
        else:
            color_print(f"  ℹ️  {message}", Colors.YELLOW)
    else:
        print(f"CCL_TRACE: {message}")


# PURPOSE: 実行: start_session
def start_session(expression: str):
    session_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    state = {
        "session_id": session_id,
        "expression": expression,
        "start_time": datetime.datetime.now().isoformat(),
        "steps": [],
    }
    save_state(state)

    log_entry(
        {
            "type": "SESSION_START",
            "session_id": session_id,
            "expression": expression,
            "message": f"Started CCL Session: {expression}",
        }
    )


# PURPOSE: log_step — システムの処理
def log_step(op: str, status: str = "running", note: str = ""):
    state = load_state()
    if not state:
        color_print("🚨 Error: No active CCL session. Run 'start' first.", Colors.RED, bold=True)
        return

    step_record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "op": op,
        "status": status,
        "note": note,
    }
    state["steps"].append(step_record)
    save_state(state)

    log_entry(
        {
            "type": "STEP",
            "session_id": state.get("session_id"),
            "op": op,
            "status": status,
            "note": note,
            "message": f"Step: {op} [{status}] {note}",
        }
    )


# PURPOSE: end_session — システムの処理
def end_session(status: str = "completed"):
    state = load_state()
    if not state:
        color_print("🚨 Error: No active CCL session.", Colors.RED, bold=True)
        return

    duration = "unknown"
    if "start_time" in state:
        start_dt = datetime.datetime.fromisoformat(state["start_time"])
        end_dt = datetime.datetime.now()
        duration = str(end_dt - start_dt)

    log_entry(
        {
            "type": "SESSION_END",
            "session_id": state.get("session_id"),
            "status": status,
            "duration": duration,
            "step_count": len(state.get("steps", [])),
            "message": f"Ended CCL Session: {status} (Duration: {duration})",
        }
    )

    # Archive state
    # In a real implementation, we might move state file to history
    # For now, just leave it for inspection or next overwrite


# PURPOSE: CLI エントリポイント — システムの直接実行
def main():
    parser = argparse.ArgumentParser(description="CCL Tracer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Start
    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("expression", help="CCL expression to execution")

    # Step
    step_parser = subparsers.add_parser("step")
    step_parser.add_argument("op", help="Current operator/operation")
    step_parser.add_argument(
        "--status", default="running", help="Status (running, success, failed, skipped)"
    )
    step_parser.add_argument("--note", default="", help="Optional note")

    # End
    end_parser = subparsers.add_parser("end")
    end_parser.add_argument("--status", default="completed", help="Final status")

    args = parser.parse_args()
    ensure_dirs()

    if args.command == "start":
        start_session(args.expression)
    elif args.command == "step":
        log_step(args.op, args.status, args.note)
    elif args.command == "end":
        end_session(args.status)


if __name__ == "__main__":
    main()
