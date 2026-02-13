# PROOF: [L2/Infrastructure] <- mekhane/ochema/ A0→CLIインターフェース
#!/usr/bin/env python3
# PURPOSE: Ochēma CLI (AntigravityClient ラッパー)
"""
Ochēma CLI — Command Line Interface for Antigravity

AntigravityClient を CLI から操作し、
モデルへのクエリ送信、セッション履歴の表示、サーバー情報の取得を行う。

Usage:
    python -m mekhane.ochema.cli ask "Hello" --model "MODEL_PLACEHOLDER_M8"
    python -m mekhane.ochema.cli ls
    python -m mekhane.ochema.cli info
"""

from __future__ import annotations

# PROOF: [L2/Infrastructure] <- mekhane/ochema/ A0→CLIインターフェース
import argparse
import os
import sys
import json
import logging
from typing import Optional

# Ensure correct path for direct execution
if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(path))))

from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse


# PURPOSE: [L2-auto] コマンド: ask
def cmd_ask(args: argparse.Namespace) -> int:
    """LLM にメッセージを送信する。"""
    client = AntigravityClient(
        workspace=args.workspace,
        timeout=args.timeout,
    )

    try:
        response = client.ask(
            message=args.message,
            model=args.model,
            timeout=args.timeout,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(response.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"--- Response ({response.model}, {response.duration_ms}ms) ---")
        print(response.text)
        if response.thinking:
            print("\n--- Thinking ---")
            print(response.thinking)
        if response.error:
            print(f"\nError: {response.error}", file=sys.stderr)
            return 1

    return 0


# PURPOSE: [L2-auto] コマンド: ls
def cmd_ls(args: argparse.Namespace) -> int:
    """プロセスリストを表示する。"""
    try:
        info = AntigravityClient.ls()
    except Exception as e:
        print(f"Error listing processes: {e}", file=sys.stderr)
        return 1

    if args.json:
        # Convert dataclass to dict if necessary, or just dump raw
        # AntigravityClient.ls returns LSInfo objects
        data = [
            {
                "pid": i.pid,
                "port": i.port,
                "workspace": i.workspace,
                "cmdline": i.cmdline
            }
            for i in info
        ]
        print(json.dumps(data, indent=2))
    else:
        print(f"Found {len(info)} Antigravity Language Servers:")
        for i in info:
            ws = i.workspace or "(unknown)"
            print(f"  PID: {i.pid:<6} Port: {i.port:<5} Workspace: {ws}")

    return 0


# PURPOSE: [L2-auto] コマンド: info
def cmd_info(args: argparse.Namespace) -> int:
    """サーバー情報を表示する。"""
    client = AntigravityClient(workspace=args.workspace)

    try:
        status = client.get_status()
        config = client.get_model_config()
    except Exception as e:
        print(f"Error getting info: {e}", file=sys.stderr)
        return 1

    if args.json:
        data = {
            "status": status,
            "config": config,
            "connection": {
                "pid": client.pid,
                "port": client.port,
                "workspace": client.workspace_path
            }
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("--- Connection ---")
        print(f"PID: {client.pid}")
        print(f"Port: {client.port}")
        print(f"Workspace: {client.workspace_path}")

        print("\n--- Status ---")
        print(json.dumps(status, indent=2))

        print("\n--- Model Config ---")
        # Simply dump keys to avoid huge output
        if isinstance(config, dict):
            print(f"Config Keys: {list(config.keys())}")
        else:
            print(str(config))

    return 0


# PURPOSE: [L2-auto] コマンド: session
def cmd_session(args: argparse.Namespace) -> int:
    """セッション操作 (list/read)。"""
    client = AntigravityClient(workspace=args.workspace)

    if args.subcommand == "list":
        try:
            info = client.session_info()
            if args.json:
                print(json.dumps(info, indent=2, ensure_ascii=False))
            else:
                sessions = info.get("sessions", [])
                print(f"Found {len(sessions)} active sessions:")
                for s in sessions[:20]:  # limit output
                    print(f"  {s.get('cascade_id')[:8]}.. : {s.get('step_count')} steps - {s.get('summary')}")
        except Exception as e:
            print(f"Error listing sessions: {e}", file=sys.stderr)
            return 1

    elif args.subcommand == "read":
        if not args.id:
            print("Error: --id is required for read", file=sys.stderr)
            return 1
        try:
            data = client.session_read(args.id, full=args.full)
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                conv = data.get("conversation", [])
                print(f"Session {args.id} ({len(conv)} turns):")
                for turn in conv:
                    role = turn.get("role", "unknown")
                    content = turn.get("content", "")[:100].replace("\n", " ")
                    print(f"  [{role}] {content}...")
        except Exception as e:
            print(f"Error reading session: {e}", file=sys.stderr)
            return 1

    return 0


# PURPOSE: [L2-auto] メインエントリポイント
def main() -> int:
    """メインエントリポイント。"""
    parser = argparse.ArgumentParser(description="Ochēma CLI")
    parser.add_argument(
        "--workspace", "-w",
        default=None,
        help="Workspace path or name to attach to (default: auto-detect)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ask
    p_ask = subparsers.add_parser("ask", help="Send message to LLM")
    p_ask.add_argument("message", help="Message to send")
    p_ask.add_argument("--model", "-m", default="MODEL_PLACEHOLDER_M8", help="Model ID")
    p_ask.add_argument("--timeout", "-t", type=float, default=120.0, help="Timeout in seconds")
    p_ask.set_defaults(func=cmd_ask)

    # ls
    p_ls = subparsers.add_parser("ls", help="List running Language Servers")
    p_ls.set_defaults(func=cmd_ls)

    # info
    p_info = subparsers.add_parser("info", help="Get server status and config")
    p_info.set_defaults(func=cmd_info)

    # session
    p_sess = subparsers.add_parser("session", help="Session operations")
    sp_sess = p_sess.add_subparsers(dest="subcommand", required=True)

    sess_list = sp_sess.add_parser("list", help="List sessions")

    sess_read = sp_sess.add_parser("read", help="Read session content")
    sess_read.add_argument("--id", help="Cascade ID")
    sess_read.add_argument("--full", action="store_true", help="Get full conversation history")

    p_sess.set_defaults(func=cmd_session)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
