#!/usr/bin/env python3
"""
Antigravity IDE チャット履歴メタデータ エクスポーター

state.vscdb の antigravityUnifiedStateSync.trajectorySummaries から
全会話のメタデータ（タイトル、UUID、タイムスタンプ、ステップ数、サマリー）を抽出し、
JSON / Markdown 形式でエクスポートする。

Usage:
    python export_chat_metadata.py                    # 一覧表示
    python export_chat_metadata.py --export json      # JSON エクスポート
    python export_chat_metadata.py --export markdown  # Markdown エクスポート
    python export_chat_metadata.py --export all       # 両方
    python export_chat_metadata.py --conversation-id UUID  # 特定会話の詳細

Data source:
    ~/.config/Antigravity/User/globalStorage/state.vscdb
    Key: antigravityUnifiedStateSync.trajectorySummaries
    Format: Base64 → Protocol Buffers (wire format)

Structure:
    Top-level: repeated field 1 (conversation entries)
    Each entry:
      - SubField 1: conversation UUID (string)
      - SubField 2: nested protobuf → Base64 → inner protobuf
        - field 1: title (string)
        - field 2: step_count (varint)
        - field 3: last_active timestamp {seconds, nanos}
        - field 4: session_id (string)
        - field 5: flag (varint)
        - field 7: created_at timestamp {seconds, nanos}
        - field 9: workspace info (nested)
        - field 10: updated_at timestamp {seconds, nanos}
        - field 12: summary data (nested, large)
        - field 14: summary data v2 (nested)
        - field 16: message_count (varint)
"""

import argparse
import base64
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# Constants
# ============================================================================

STATE_DB_PATH = Path.home() / ".config/Antigravity/User/globalStorage/state.vscdb"
TRAJECTORY_KEY = "antigravityUnifiedStateSync.trajectorySummaries"
DEFAULT_OUTPUT_DIR = Path.home() / "oikos/mneme/.hegemonikon/sessions"
JST = timezone(timedelta(hours=9))

# ============================================================================
# Protobuf Wire Format Parser (schema-less)
# ============================================================================


def parse_varint(buf: bytes, pos: int) -> Tuple[int, int]:
    """Parse a protobuf varint from buffer at position."""
    result = 0
    shift = 0
    while pos < len(buf):
        b = buf[pos]
        result |= (b & 0x7F) << shift
        pos += 1
        if not (b & 0x80):
            break
        shift += 7
    return result, pos


def parse_protobuf(buf: bytes) -> List[Tuple[int, str, Any]]:
    """Parse protobuf wire format without schema.

    Returns list of (field_number, wire_type_name, value) tuples.
    """
    pos = 0
    fields = []
    while pos < len(buf):
        try:
            tag, pos = parse_varint(buf, pos)
        except (IndexError, ValueError):
            break
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 0:
            break

        if wire_type == 0:  # varint
            val, pos = parse_varint(buf, pos)
            fields.append((field_num, "varint", val))
        elif wire_type == 2:  # length-delimited (string, bytes, nested message)
            length, pos = parse_varint(buf, pos)
            if length < 0 or length > len(buf) - pos:
                break
            val = buf[pos : pos + length]
            pos += length
            fields.append((field_num, "bytes", val))
        elif wire_type == 1:  # 64-bit
            if pos + 8 > len(buf):
                break
            pos += 8
        elif wire_type == 5:  # 32-bit
            if pos + 4 > len(buf):
                break
            pos += 4
        else:
            break
    return fields


def try_decode_utf8(data: bytes) -> Optional[str]:
    """Attempt to decode bytes as UTF-8 string."""
    try:
        s = data.decode("utf-8")
        # Heuristic: if it's a valid printable string
        if s and all(c.isprintable() or c in "\n\r\t" for c in s):
            return s
    except (UnicodeDecodeError, ValueError):
        pass
    return None


def parse_timestamp(fields: List[Tuple[int, str, Any]]) -> Optional[datetime]:
    """Parse a protobuf Timestamp message (seconds + nanos)."""
    seconds = None
    nanos = 0
    for fn, ft, fv in fields:
        if fn == 1 and ft == "varint":
            seconds = fv
        elif fn == 2 and ft == "varint":
            nanos = fv
    if seconds is not None:
        try:
            dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
            return dt.astimezone(JST)
        except (OSError, OverflowError, ValueError):
            pass
    return None


# ============================================================================
# Conversation Parser
# ============================================================================


def extract_summary_text(data: bytes) -> Optional[str]:
    """Extract readable summary text from nested protobuf summary fields."""
    fields = parse_protobuf(data)
    texts = []
    for fn, ft, fv in fields:
        if ft == "bytes":
            s = try_decode_utf8(fv)
            if s and len(s) > 10:
                texts.append(s)
            else:
                # Try nested
                inner = parse_protobuf(fv)
                for ifn, ift, ifv in inner:
                    if ift == "bytes":
                        s2 = try_decode_utf8(ifv)
                        if s2 and len(s2) > 10:
                            texts.append(s2)
    return "\n".join(texts) if texts else None


def parse_conversation_entry(entry_data: bytes) -> Optional[Dict]:
    """Parse a single conversation entry from protobuf."""
    subfields = parse_protobuf(entry_data)

    uuid_val = None
    nested_data = None

    for sfn, sft, sfv in subfields:
        if sfn == 1 and sft == "bytes":
            uuid_val = try_decode_utf8(sfv)
        elif sfn == 2 and sft == "bytes":
            nested_data = sfv

    if not uuid_val or not nested_data:
        return None

    # Parse nested data (field 2) — contains a single base64-encoded protobuf
    inner_fields = parse_protobuf(nested_data)
    if not inner_fields:
        return None

    # The first (and usually only) field is a base64-encoded protobuf
    b64_field = inner_fields[0]
    if b64_field[1] != "bytes":
        return None

    try:
        decoded_inner = base64.b64decode(b64_field[2])
    except Exception:
        return None

    detail_fields = parse_protobuf(decoded_inner)

    result = {
        "conversation_id": uuid_val,
        "title": None,
        "step_count": None,
        "message_count": None,
        "last_active": None,
        "created_at": None,
        "updated_at": None,
        "session_id": None,
        "workspace_uri": None,
        "summary": None,
    }

    for fn, ft, fv in detail_fields:
        if fn == 1 and ft == "bytes":
            result["title"] = try_decode_utf8(fv)
        elif fn == 2 and ft == "varint":
            result["step_count"] = fv
        elif fn == 3 and ft == "bytes":
            ts = parse_timestamp(parse_protobuf(fv))
            if ts:
                result["last_active"] = ts.isoformat()
        elif fn == 4 and ft == "bytes":
            result["session_id"] = try_decode_utf8(fv)
        elif fn == 7 and ft == "bytes":
            ts = parse_timestamp(parse_protobuf(fv))
            if ts:
                result["created_at"] = ts.isoformat()
        elif fn == 9 and ft == "bytes":
            s = try_decode_utf8(fv)
            if s:
                # Extract file:// URIs
                uris = re.findall(r"file://[^\x00-\x1f]+", s)
                if uris:
                    result["workspace_uri"] = uris[0]
        elif fn == 10 and ft == "bytes":
            ts = parse_timestamp(parse_protobuf(fv))
            if ts:
                result["updated_at"] = ts.isoformat()
        elif fn == 12 and ft == "bytes":
            summary = extract_summary_text(fv)
            if summary:
                result["summary"] = summary
        elif fn == 16 and ft == "varint":
            result["message_count"] = fv

    return result


# ============================================================================
# Database Reader
# ============================================================================


def read_trajectory_summaries(db_path: Path = STATE_DB_PATH) -> bytes:
    """Read and decode the trajectrySummaries from state.vscdb."""
    if not db_path.exists():
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cursor = conn.execute(
            "SELECT value FROM ItemTable WHERE key = ?", (TRAJECTORY_KEY,)
        )
        row = cursor.fetchone()
        if not row:
            print(f"Error: Key '{TRAJECTORY_KEY}' not found", file=sys.stderr)
            sys.exit(1)

        raw_value = row[0]
        if isinstance(raw_value, str):
            return base64.b64decode(raw_value)
        elif isinstance(raw_value, bytes):
            # Try base64 decode first
            try:
                return base64.b64decode(raw_value)
            except Exception:
                return raw_value
    finally:
        conn.close()


def parse_all_conversations(db_path: Path = STATE_DB_PATH) -> List[Dict]:
    """Parse all conversation entries from state.vscdb."""
    decoded = read_trajectory_summaries(db_path)
    top_fields = parse_protobuf(decoded)

    conversations = []
    for fn, ft, fv in top_fields:
        if fn == 1 and ft == "bytes":
            entry = parse_conversation_entry(fv)
            if entry:
                conversations.append(entry)

    # Sort by last_active (most recent first)
    conversations.sort(
        key=lambda c: c.get("last_active") or "", reverse=True
    )
    return conversations


# ============================================================================
# Export Functions
# ============================================================================


def export_json(conversations: List[Dict], output_path: Path) -> None:
    """Export conversations to JSON."""
    output = {
        "exported_at": datetime.now(JST).isoformat(),
        "total_conversations": len(conversations),
        "total_steps": sum(c.get("step_count", 0) or 0 for c in conversations),
        "conversations": conversations,
    }
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✅ JSON exported: {output_path} ({len(conversations)} conversations)")


def export_markdown(conversations: List[Dict], output_path: Path) -> None:
    """Export conversations to Markdown."""
    lines = [
        f"# Antigravity Chat History Export",
        f"",
        f"> Exported: {datetime.now(JST).strftime('%Y-%m-%d %H:%M JST')}",
        f"> Total: {len(conversations)} conversations, "
        f"{sum(c.get('step_count', 0) or 0 for c in conversations):,} steps",
        f"",
        f"---",
        f"",
        f"| # | Title | Steps | Created | Last Active |",
        f"|:--|:------|------:|:--------|:------------|",
    ]

    for i, c in enumerate(conversations, 1):
        title = c.get("title", "Untitled") or "Untitled"
        steps = c.get("step_count", "?") or "?"
        created = ""
        if c.get("created_at"):
            try:
                dt = datetime.fromisoformat(c["created_at"])
                created = dt.strftime("%m/%d %H:%M")
            except ValueError:
                pass
        last_active = ""
        if c.get("last_active"):
            try:
                dt = datetime.fromisoformat(c["last_active"])
                last_active = dt.strftime("%m/%d %H:%M")
            except ValueError:
                pass
        lines.append(f"| {i} | {title} | {steps} | {created} | {last_active} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Conversation Details",
            "",
        ]
    )

    for c in conversations:
        title = c.get("title", "Untitled") or "Untitled"
        lines.append(f"### {title}")
        lines.append(f"")
        lines.append(f"- **ID**: `{c['conversation_id']}`")
        if c.get("session_id"):
            lines.append(f"- **Session**: `{c['session_id']}`")
        if c.get("step_count"):
            lines.append(f"- **Steps**: {c['step_count']}")
        if c.get("message_count"):
            lines.append(f"- **Messages**: {c['message_count']}")
        if c.get("created_at"):
            lines.append(f"- **Created**: {c['created_at']}")
        if c.get("last_active"):
            lines.append(f"- **Last Active**: {c['last_active']}")
        if c.get("workspace_uri"):
            lines.append(f"- **Workspace**: `{c['workspace_uri']}`")
        if c.get("summary"):
            lines.append(f"- **Summary**:")
            for line in c["summary"].split("\n")[:5]:
                lines.append(f"  > {line[:200]}")
        lines.append("")

    output_path.write_text("\n".join(lines))
    print(f"✅ Markdown exported: {output_path} ({len(conversations)} conversations)")


def print_table(conversations: List[Dict]) -> None:
    """Print conversation list as a formatted table."""
    print(f"\n{'#':>3}  {'Title':<50}  {'Steps':>6}  {'Created':<12}  {'Last Active':<12}")
    print(f"{'─' * 3}  {'─' * 50}  {'─' * 6}  {'─' * 12}  {'─' * 12}")

    for i, c in enumerate(conversations, 1):
        title = (c.get("title") or "Untitled")[:50]
        steps = str(c.get("step_count", "?") or "?")
        created = ""
        if c.get("created_at"):
            try:
                dt = datetime.fromisoformat(c["created_at"])
                created = dt.strftime("%m/%d %H:%M")
            except ValueError:
                pass
        last_active = ""
        if c.get("last_active"):
            try:
                dt = datetime.fromisoformat(c["last_active"])
                last_active = dt.strftime("%m/%d %H:%M")
            except ValueError:
                pass
        print(f"{i:3d}  {title:<50}  {steps:>6}  {created:<12}  {last_active:<12}")

    total_steps = sum(c.get("step_count", 0) or 0 for c in conversations)
    print(f"\n📊 Total: {len(conversations)} conversations, {total_steps:,} steps")


# ============================================================================
# Main
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity IDE チャット履歴メタデータ エクスポーター"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=STATE_DB_PATH,
        help=f"state.vscdb パス (default: {STATE_DB_PATH})",
    )
    parser.add_argument(
        "--export",
        choices=["json", "markdown", "all"],
        help="エクスポート形式",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"出力ディレクトリ (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--conversation-id",
        help="特定の会話 ID の詳細を表示",
    )
    args = parser.parse_args()

    conversations = parse_all_conversations(args.db)

    if args.conversation_id:
        # 特定会話の詳細
        matches = [c for c in conversations if c["conversation_id"] == args.conversation_id]
        if not matches:
            # Partial match
            matches = [
                c
                for c in conversations
                if args.conversation_id in c["conversation_id"]
            ]
        if matches:
            print(json.dumps(matches[0], indent=2, ensure_ascii=False))
        else:
            print(f"Error: Conversation not found: {args.conversation_id}", file=sys.stderr)
            sys.exit(1)
        return

    if args.export:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(JST).strftime("%Y-%m-%d_%H%M")

        if args.export in ("json", "all"):
            json_path = args.output_dir / f"chat_metadata_{timestamp}.json"
            export_json(conversations, json_path)

        if args.export in ("markdown", "all"):
            md_path = args.output_dir / f"chat_metadata_{timestamp}.md"
            export_markdown(conversations, md_path)
    else:
        print_table(conversations)


if __name__ == "__main__":
    main()
