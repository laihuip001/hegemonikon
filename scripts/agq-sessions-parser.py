#!/usr/bin/env python3
# PURPOSE: [L2/インフラ] GetAllCascadeTrajectories JSON レスポンスの解析・整形
"""
agq-sessions-parser — Antigravity Sessions Parser v2

GetAllCascadeTrajectories の JSON レスポンスからセッション情報を抽出する。
agq-sessions.sh から呼ばれるヘルパースクリプト。

Usage:
    cat response.json | python3 agq-sessions-parser.py --mode summary
    cat response.json | python3 agq-sessions-parser.py --mode dump --output /path/to/dir
    cat response.json | python3 agq-sessions-parser.py --mode export --output /path/to/file.md

起源: 2026-02-13 Antigravity API ハック → セッション履歴自動同期
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def parse_sessions(data: dict) -> list[dict]:
    """Parse trajectorySummaries into sorted session list."""
    summaries = data.get("trajectorySummaries", {})
    sessions = []

    for conv_id, info in summaries.items():
        created = info.get("createdTime", "")
        modified = info.get("lastModifiedTime", "")
        sessions.append(
            {
                "conversation_id": conv_id,
                "trajectory_id": info.get("trajectoryId", ""),
                "title": info.get("summary", "(untitled)"),
                "step_count": info.get("stepCount", 0),
                "status": info.get("status", ""),
                "created": created,
                "modified": modified,
                "workspaces": [
                    ws.get("workspaceFolderAbsoluteUri", "")
                    for ws in info.get("workspaces", [])
                ],
            }
        )

    # Sort by lastModifiedTime descending (most recent first)
    sessions.sort(key=lambda s: s["modified"], reverse=True)
    return sessions


def format_time_ago(iso_time: str) -> str:
    """Convert ISO time to human-readable 'X ago' format."""
    if not iso_time:
        return "?"
    try:
        # Handle nanosecond precision
        clean = iso_time.split(".")[0] + "Z"
        dt = datetime.fromisoformat(clean.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - dt
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            return f"{int(hours / 24)}d ago"
    except (ValueError, TypeError):
        return "?"


def mode_summary(data: dict) -> str:
    """Output a summary of all sessions."""
    sessions = parse_sessions(data)
    total_steps = sum(s["step_count"] for s in sessions)

    lines = [
        f"📚 Sessions: {len(sessions)} total, {total_steps:,} steps",
        "",
    ]

    # Show latest sessions
    show_count = min(5, len(sessions))
    if sessions:
        lines.append("Latest:")
        for i, sess in enumerate(sessions[:show_count], 1):
            ago = format_time_ago(sess["modified"])
            status_icon = "🟢" if sess["status"] == "CASCADE_RUN_STATUS_IDLE" else "🔵"
            lines.append(
                f"  {status_icon} [{i}] {sess['title']} "
                f"({sess['step_count']} steps, {ago})"
            )

    return "\n".join(lines)


def mode_dump(data: dict, output_dir: str) -> str:
    """Save structured session data to output directory."""
    os.makedirs(output_dir, exist_ok=True)
    sessions = parse_sessions(data)

    # Save raw JSON
    raw_path = os.path.join(output_dir, "trajectories_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Save session index
    index_path = os.path.join(output_dir, "session_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

    return (
        f"✅ Dump complete: {output_dir}/\n"
        f"   Raw: {raw_path} ({os.path.getsize(raw_path):,} bytes)\n"
        f"   Index: {index_path} ({len(sessions)} sessions)"
    )


def mode_export(data: dict, output_path: str) -> str:
    """Export session list as Markdown for /bye Handoff."""
    sessions = parse_sessions(data)

    lines = [
        "# Session History Export",
        "",
        f"> Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> Total: {len(sessions)} sessions",
        f"> Source: gRPC GetAllCascadeTrajectories (auto-export)",
        "",
        "---",
        "",
        "| # | Title | Steps | Last Modified | Status |",
        "|:--|:------|------:|:-------------|:-------|",
    ]

    for i, sess in enumerate(sessions, 1):
        ago = format_time_ago(sess["modified"])
        status = "idle" if "IDLE" in sess["status"] else "active"
        lines.append(
            f"| {i} | {sess['title']} | {sess['step_count']} | {ago} | {status} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Session IDs")
    lines.append("")
    for sess in sessions[:10]:
        lines.append(f"- `{sess['conversation_id']}` — {sess['title']}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return f"✅ Exported: {output_path} ({len(sessions)} sessions)"


def main():
    parser = argparse.ArgumentParser(
        description="Parse Antigravity session trajectories from JSON response"
    )
    parser.add_argument(
        "--mode",
        choices=["summary", "dump", "export"],
        default="summary",
        help="Operation mode",
    )
    parser.add_argument(
        "--output",
        default="/tmp/agq_sessions",
        help="Output directory (dump) or file path (export)",
    )
    args = parser.parse_args()

    # Read from stdin
    raw = sys.stdin.read()
    if not raw:
        print("❌ No data received on stdin", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "summary":
        print(mode_summary(data))
    elif args.mode == "dump":
        print(mode_dump(data, args.output))
    elif args.mode == "export":
        output_path = args.output
        if os.path.isdir(output_path) or not output_path.endswith(".md"):
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_path = os.path.expanduser(
                f"~/oikos/mneme/.hegemonikon/sessions/chat_export_{date_str}.md"
            )
        print(mode_export(data, output_path))


if __name__ == "__main__":
    main()
