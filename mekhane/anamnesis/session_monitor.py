#!/usr/bin/env python3
# PURPOSE: LS API ポーリングでアクティブセッションをリアルタイムにモニターし MD 保存する
"""
PROOF: [L2/インフラ] <- mekhane/anamnesis/

Session Monitor — リアルタイムセッションログ保存

AntigravityClient を使って LS API をポーリングし、
新しい/更新されたセッションの対話内容を MD ファイルとして保存する。

Usage:
    # One-shot: 現時点のスナップショットを保存
    python mekhane/anamnesis/session_monitor.py --once

    # デーモン: 30秒間隔で監視 (Ctrl+C で停止)
    python mekhane/anamnesis/session_monitor.py --daemon

    # カスタム間隔
    python mekhane/anamnesis/session_monitor.py --daemon --interval 60
"""

import argparse
import json
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure hegemonikon root is in path
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

from mekhane.ochema.antigravity_client import AntigravityClient

# --- Constants ---

OUTPUT_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "sessions"
STATE_FILE = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "monitor_state.json"
DEFAULT_INTERVAL = 30  # seconds
MAX_SESSIONS = 20  # monitor top N recent sessions


# PURPOSE: 前回のモニター状態 (各セッションの最終 step_count) を JSON から復元する
def load_state() -> dict:
    """PURPOSE: 前回のモニター状態 (各セッションの最終 step_count) を JSON から復元する"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


# PURPOSE: モニター状態を JSON ファイルに永続化する
def save_state(state: dict) -> None:
    """PURPOSE: モニター状態を JSON ファイルに永続化する"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


# PURPOSE: 会話データをセッション記録用マークダウン形式にフォーマットする
def format_session_md(conv: dict, summary: str, cascade_id: str) -> str:
    """PURPOSE: 会話データをセッション記録用マークダウン形式にフォーマットする"""
    lines = [
        f"# {summary}",
        "",
        f"- **ID**: `{cascade_id}`",
        f"- **キャプチャ日時**: {datetime.now().isoformat()}",
        f"- **ステップ数**: {conv.get('total_steps', 0)}",
        f"- **ターン数**: {conv.get('total_turns', 0)}",
        "",
        "---",
        "",
    ]

    for turn in conv.get("conversation", []):
        role = turn.get("role", "")
        if role == "user":
            lines.append("## 👤 User")
            lines.append("")
            lines.append(turn.get("content", ""))
            lines.append("")
        elif role == "assistant":
            model = turn.get("model", "")
            model_note = f" ({model})" if model else ""
            lines.append(f"## 🤖 Claude{model_note}")
            lines.append("")
            lines.append(turn.get("content", ""))
            lines.append("")
        elif role == "tool":
            tool_name = turn.get("tool", "unknown")
            status = turn.get("status", "")
            lines.append(f"> 🔧 `{tool_name}` [{status}]")
            lines.append("")

    return "\n".join(lines)


# PURPOSE: [L2-auto] タイトルをファイル名に変換
def sanitize_filename(title: str) -> str:
    """タイトルをファイル名に変換"""
    # Remove or replace problematic chars
    import re
    name = re.sub(r'[<>:"/\\|?*\n\r]', '_', title)
    name = re.sub(r'_+', '_', name).strip('_')
    return name[:80] if name else "untitled"


# PURPOSE: [L2-auto] 1回のモニタリングサイクル
def monitor_once(client: AntigravityClient, state: dict) -> dict:
    """1回のモニタリングサイクル"""
    # 全セッション一覧を取得
    info = client.session_info()
    if "error" in info:
        print(f"[Monitor] ❌ LS API error: {info['error']}")
        return state

    sessions = info.get("sessions", [])
    if not sessions:
        print("[Monitor] No sessions found")
        return state

    # 最新 N 件を対象
    recent = sessions[:MAX_SESSIONS]
    updated_count = 0

    for s in recent:
        cascade_id = s.get("cascade_id", "")
        step_count = s.get("step_count", 0)
        summary = s.get("summary", f"Session {cascade_id[:8]}")
        status = s.get("status", "")

        if not cascade_id:
            continue

        # 前回との比較
        prev_steps = state.get(cascade_id, {}).get("step_count", 0)

        if step_count <= prev_steps:
            continue  # 変化なし

        # 新しいステップ検出
        delta = step_count - prev_steps
        print(f"[Monitor] 📝 {summary[:50]}... (+{delta} steps)")

        try:
            conv = client.session_read(cascade_id, full=True)
            if "error" in conv:
                print(f"  ⚠️ Read error: {conv['error']}")
                continue

            # MD 保存
            md_content = format_session_md(conv, summary, cascade_id)
            safe_name = sanitize_filename(summary)
            ts = datetime.now().strftime("%Y-%m-%d")
            filename = f"live_{ts}_{safe_name}.md"
            filepath = OUTPUT_DIR / filename

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            filepath.write_text(md_content, encoding="utf-8")
            print(f"  ✅ Saved: {filepath.name} ({len(md_content)} bytes)")

            # 状態更新
            state[cascade_id] = {
                "step_count": step_count,
                "summary": summary,
                "last_updated": datetime.now().isoformat(),
                "status": status,
            }
            updated_count += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    if updated_count == 0:
        print(f"[Monitor] ✅ No updates ({len(recent)} sessions checked)")
    else:
        print(f"[Monitor] 📊 {updated_count} sessions updated")
        save_state(state)

    return state


# PURPOSE: [L2-auto] デーモンモード: 定期ポーリング
def daemon_loop(client: AntigravityClient, interval: int) -> None:
    """デーモンモード: 定期ポーリング"""
    state = load_state()
    running = True

    # PURPOSE: [L2-auto] 関数: signal_handler
    def signal_handler(sig, frame):
        nonlocal running
        print("\n[Monitor] 🛑 Shutting down...")
        save_state(state)
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"[Monitor] 🚀 Daemon started (interval={interval}s, max_sessions={MAX_SESSIONS})")
    print(f"[Monitor]    Output: {OUTPUT_DIR}")
    print(f"[Monitor]    State:  {STATE_FILE}")

    cycle = 0
    while running:
        cycle += 1
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n[Monitor] --- Cycle {cycle} ({ts}) ---")

        try:
            state = monitor_once(client, state)
        except Exception as e:
            print(f"[Monitor] ❌ Cycle error: {e}")

        # Wait with interruptibility
        for _ in range(interval):
            if not running:
                break
            time.sleep(1)

    print("[Monitor] 👋 Daemon stopped")

# PURPOSE: [L2-auto] 関数: main

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor active Antigravity sessions and save to MD"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--once", action="store_true",
        help="One-shot: capture current state and exit",
    )
    mode.add_argument(
        "--daemon", action="store_true",
        help="Daemon: poll continuously",
    )
    parser.add_argument(
        "--interval", type=int, default=DEFAULT_INTERVAL,
        help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--workspace", default="hegemonikon",
        help="Workspace name for LS detection (default: hegemonikon)",
    )

    args = parser.parse_args()

    # Connect to LS
    try:
        client = AntigravityClient(workspace=args.workspace)
        print(f"[Monitor] Connected to LS (PID={client.pid}, port={client.port})")
    except Exception as e:
        print(f"[Monitor] ❌ Cannot connect to LS: {e}")
        return 1

    if args.once:
        state = load_state()
        state = monitor_once(client, state)
        save_state(state)
        return 0
    elif args.daemon:
        daemon_loop(client, args.interval)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
