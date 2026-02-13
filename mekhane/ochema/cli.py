# PURPOSE: Ochēma CLI — Antigravity LS とのインタラクション
"""Ochēma CLI — Antigravity Language Server Client.

Usage:
    python -m mekhane.ochema.cli status          # LS ステータス確認
    python -m mekhane.ochema.cli ask "message"   # LLM に問い合わせ
    python -m mekhane.ochema.cli models          # モデル一覧
    python -m mekhane.ochema.cli chat            # 対話モード
"""

from __future__ import annotations

import argparse
import sys

from mekhane.ochema.antigravity_client import AntigravityClient, DEFAULT_MODEL


def cmd_status(args: argparse.Namespace) -> None:
    """LS 接続ステータスを表示。"""
    client = AntigravityClient(workspace=args.workspace)
    print(f"┌─────────────────────────────────────────┐")
    print(f"│ ⚡ Ochēma — LS Status")
    print(f"├─────────────────────────────────────────┤")
    print(f"│ PID:       {client.pid}")
    print(f"│ Port:      {client.port}")
    print(f"│ CSRF:      {client.csrf[:12]}...")
    print(f"│ Workspace: {client.workspace}")
    print(f"│ All Ports: {client.ls.all_ports}")
    print(f"└─────────────────────────────────────────┘")


def cmd_models(args: argparse.Namespace) -> None:
    """利用可能なモデル一覧を表示。"""
    client = AntigravityClient(workspace=args.workspace)
    models = client.list_models()
    print(f"┌─────────────────────────────────────────────────┐")
    print(f"│ 🧠 Available Models ({len(models)})")
    print(f"├─────────────────────────────────────────────────┤")
    for m in models:
        bar = "█" * (m["remaining"] // 5) + "░" * (20 - m["remaining"] // 5)
        icon = "🟢" if m["remaining"] >= 80 else "🟡" if m["remaining"] >= 40 else "🔴"
        print(f"│ {icon} {m['label']:<30} {m['remaining']:>3}% {bar}")
    print(f"└─────────────────────────────────────────────────┘")


def cmd_ask(args: argparse.Namespace) -> None:
    """LLM にメッセージを送信し、応答を表示。"""
    client = AntigravityClient(workspace=args.workspace)
    message = " ".join(args.message)
    model = args.model

    print(f"📤 Sending to {model}...")
    print(f"   Message: {message[:80]}{'...' if len(message) > 80 else ''}")
    print()

    try:
        response = client.ask(message, model=model, timeout=args.timeout)
        if response.thinking:
            print("💭 Thinking:")
            print(f"   {response.thinking[:200]}...")
            print()
        print("💬 Response:")
        print(response.text)
        print()
        print(f"───────────────────────────────────────────")
        print(f"  Model: {response.model}")
        if response.token_usage:
            print(f"  Tokens: {response.token_usage}")
    except TimeoutError as e:
        print(f"⏰ {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


def cmd_chat(args: argparse.Namespace) -> None:
    """対話モード。"""
    client = AntigravityClient(workspace=args.workspace)
    model = args.model
    print(f"💬 Ochēma Chat (model: {model})")
    print(f"   Type 'quit' or Ctrl+C to exit")
    print()

    while True:
        try:
            message = input("You> ").strip()
            if not message or message.lower() in ("quit", "exit", "q"):
                print("👋 Bye!")
                break

            response = client.ask(message, model=model, timeout=args.timeout)
            print(f"\nLLM> {response.text}\n")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Bye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def cmd_quota(args: argparse.Namespace) -> None:
    """Quota + Experiment フラグ状態を表示。"""
    import json
    client = AntigravityClient(workspace=args.workspace)
    data = client.quota_status()

    print("┌─────────────────────────────────────────────────────────┐")
    print("│ 📊 Quota Status")
    print("├─────────────────────────────────────────────────────────┤")
    for m in data.get("models", []):
        pct = m["remaining_pct"]
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        icon = "🟢" if pct >= 80 else "🟡" if pct >= 40 else "🔴"
        print(f"│ {icon} {m['label']:<30} {pct:>3}% {bar}")
    print("├─────────────────────────────────────────────────────────┤")
    print("│ 🧪 Context/Memory Experiments")
    for e in data.get("experiments", []):
        icon = "✅" if e["enabled"] else "❌"
        print(f"│ {icon} {e['key']}")
    print("└─────────────────────────────────────────────────────────┘")


def cmd_sessions(args: argparse.Namespace) -> None:
    """セッション一覧/詳細を表示。"""
    import json
    client = AntigravityClient(workspace=args.workspace)
    data = client.session_info(cascade_id=getattr(args, "cascade_id", None))

    if "error" in data:
        print(f"❌ {data['error']}")
        return

    if "sessions" in data:
        print(f"┌────────────────────────────────────────────────────┐")
        print(f"│ 📋 Sessions ({data['total']} total, showing latest 20)")
        print(f"├────────────────────────────────────────────────────┤")
        for s in data["sessions"]:
            status_icon = "🟢" if "RUNNING" in s.get("status", "") else "⚪"
            summary = s.get("summary", "")[:40] or "(no summary)"
            print(f"│ {status_icon} {s['cascade_id'][:8]}... steps={s['step_count']:<4} {summary}")
        print(f"└────────────────────────────────────────────────────┘")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_episodes(args: argparse.Namespace) -> None:
    """エピソード記憶一覧/詳細を表示。"""
    import json
    client = AntigravityClient(workspace=args.workspace)
    data = client.session_episodes(brain_id=getattr(args, "brain_id", None))

    if "error" in data:
        print(f"❌ {data['error']}")
        return

    if "brains" in data:
        print(f"┌────────────────────────────────────────────────────────────┐")
        print(f"│ 🧠 Episode Memory ({data['total_brains']} brains with episodes)")
        print(f"├────────────────────────────────────────────────────────────┤")
        for b in data["brains"]:
            title = b.get("title", "")[:40] or "(no title)"
            print(f"│ {b['brain_id'][:8]}... episodes={b['episode_count']:<3} {title}")
        print(f"└────────────────────────────────────────────────────────────┘")
    else:
        print(f"Brain: {data.get('brain_id', '')}")
        print(f"Episodes: {data.get('total_episodes', 0)}")
        for ep in data.get("episodes", []):
            print(f"  Step {ep['step']}: {ep['size_bytes']} bytes")
            print(f"    {ep['preview'][:80]}...")


def main() -> None:
    """CLI エントリーポイント。"""
    parser = argparse.ArgumentParser(
        prog="ochema",
        description="Ochēma — Antigravity Language Server Client",
    )
    parser.add_argument(
        "--workspace", "-w", default="hegemonikon",
        help="Workspace name (default: hegemonikon)",
    )
    parser.add_argument(
        "--model", "-m", default=DEFAULT_MODEL,
        help=f"Model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--timeout", "-t", type=float, default=120,
        help="Timeout in seconds (default: 120)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    subparsers.add_parser("status", help="Show LS connection status")

    # models
    subparsers.add_parser("models", help="List available models")

    # ask
    ask_parser = subparsers.add_parser("ask", help="Ask LLM a question")
    ask_parser.add_argument("message", nargs="+", help="Message to send")

    # chat
    subparsers.add_parser("chat", help="Interactive chat mode")

    # quota
    subparsers.add_parser("quota", help="Show quota status and experiment flags")

    # sessions
    sess_parser = subparsers.add_parser("sessions", help="List/show cascade sessions")
    sess_parser.add_argument("cascade_id", nargs="?", help="Specific cascade ID for details")

    # episodes
    ep_parser = subparsers.add_parser("episodes", help="Access episode memory (.system_generated)")
    ep_parser.add_argument("brain_id", nargs="?", help="Specific brain ID for details")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "ask":
        cmd_ask(args)
    elif args.command == "chat":
        cmd_chat(args)
    elif args.command == "quota":
        cmd_quota(args)
    elif args.command == "sessions":
        cmd_sessions(args)
    elif args.command == "episodes":
        cmd_episodes(args)


if __name__ == "__main__":
    main()
