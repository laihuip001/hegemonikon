# PROOF: [L3/ユーティリティ] O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
Takeout Importer for Hegemonikón (Robustness Enhanced)
======================================================
Google Takeout (Gemini/ChatGPT) のJSON履歴を
Obsidian Vault 形式のMarkdownに変換する。

Enhancements (v1.1):
- Windows Path Length Limitation (< 50 chars)
- Recursive Text Extraction (Nested structures)
- Error Handling per file
"""

import json
import re
import sys
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Iterable

try:
    import ijson
except ImportError:
    ijson = None


def safe_filename(text: str, max_bytes: int = 100) -> str:
    """
    ファイル名を安全な文字のみにし、バイト数で制限する。
    長すぎる場合はハッシュを付与して一意性を保つ。
    """
    # 無効な文字を置換
    safe_text = re.sub(r'[\\/*?:"<>|]', "_", text)
    safe_text = safe_text.replace("\n", " ").strip()

    # バイト数チェック (UTF-8)
    encoded = safe_text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return safe_text

    # ハッシュ生成
    hash_digest = hashlib.md5(encoded).hexdigest()[:8]

    # 切り詰め (末尾にハッシュをつける余裕を残す)
    # UTF-8境界での切り詰めは複雑なので簡略化のためにdecode ignoreを使う
    truncated = encoded[: max_bytes - 20].decode("utf-8", errors="ignore")
    return f"{truncated}_{hash_digest}"


def extract_text_recursive(node: Union[str, list, dict]) -> str:
    """
    複雑なネスト構造からテキストを再帰的に抽出する。
    Gemini/ChatGPTの多様な構造に対応。
    """
    if isinstance(node, str):
        return node
    elif isinstance(node, list):
        return "\n".join([extract_text_recursive(item) for item in node if item])
    elif isinstance(node, dict):
        parts = []
        # 優先順位: text > content > parts
        if "text" in node:
            parts.append(extract_text_recursive(node["text"]))
        if "content" in node:
            parts.append(extract_text_recursive(node["content"]))
        if "parts" in node:
            parts.append(extract_text_recursive(node["parts"]))
        return "\n".join(parts)
    return ""


def process_conversations(data: Union[List, Dict, Iterable], output_dir: str):
    """メイン処理"""

    # Analyze structure
    conversations_iter = []
    total_count_msg = ""

    if isinstance(data, list):
        conversations_iter = data
        total_count_msg = f"Found {len(data)} conversation items."
    elif isinstance(data, dict):
        if "conversations" in data:
            conversations_iter = data["conversations"]
            total_count_msg = f"Found {len(conversations_iter)} conversation items."
        else:
            print("Warning: Unknown JSON structure. Trying to treat as list.")
            conversations_iter = [data]  # Fallback for single item
            total_count_msg = f"Found 1 conversation item."
    else:
        # Assume Iterable (streaming)
        conversations_iter = data
        total_count_msg = "Processing conversation stream..."

    print(total_count_msg)

    success_count = 0
    error_count = 0

    for item in conversations_iter:
        try:
            # Title extraction
            title = item.get("title", "Untitled")
            create_time = item.get("create_time", item.get("created_at", ""))

            # Format date
            date_str = "Unknown_Date"
            if create_time:
                try:
                    if isinstance(create_time, (int, float)):
                        dt = datetime.fromtimestamp(create_time)
                    else:
                        dt = datetime.fromisoformat(create_time.replace("Z", "+00:00"))
                    date_str = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass  # TODO: Add proper error handling

            # Safe Filename (Robustness)
            base_name = safe_filename(f"{date_str}_{title}")
            file_name = f"{base_name}.md"
            file_path = os.path.join(output_dir, file_name)

            # Messages extraction
            messages = []

            # Mapping (ChatGPT) or Messages (Gemini)
            raw_messages = []
            if "mapping" in item:
                # Topo-sort is ideal, but simplistic approach here
                for key, node in item["mapping"].items():
                    if node and "message" in node and node["message"]:
                        raw_messages.append(node["message"])
            elif "messages" in item:
                raw_messages = item["messages"]

            for m in raw_messages:
                role = m.get("role", m.get("author", {}).get("role", "unknown"))

                # Recursive extraction (Robustness)
                content_text = extract_text_recursive(m)

                if content_text.strip():
                    messages.append({"role": role, "content": content_text})

            # Task extraction (Enhanced Regex)
            tasks = []
            for msg in messages:
                if msg["role"] in ["model", "assistant"]:
                    # Markdown checklist
                    found = re.findall(r"(-\s*\[\s*\]\s*.*)", msg["content"])
                    tasks.extend(found)

                    # Keywords "TODO:", "Task:"
                    for line in msg["content"].split("\n"):
                        if "TODO" in line or "Task" in line:
                            clean_line = line.strip()
                            if clean_line and clean_line not in [t.strip() for t in tasks]:
                                tasks.append(f"- [ ] {clean_line}")

            # Generate Markdown
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"- Date: {date_str}\n")
                f.write(f"- Source: Google Takeout Import\n\n")

                if tasks:
                    f.write("## Extracted Tasks\n")
                    for t in tasks:
                        f.write(f"{t}\n")
                    f.write("\n---\n\n")

                for msg in messages:
                    role_icon = "🤖" if msg["role"] in ["model", "assistant"] else "👤"
                    f.write(f"### {role_icon} {msg['role']}\n\n")
                    f.write(f"{msg['content']}\n\n")

            success_count += 1
            print(f"Generated: {file_name}")

        except Exception as e:
            error_count += 1
            print(f"Error processing item '{title}': {str(e)}")
            continue

    print(f"\nImport Complete: {success_count} success, {error_count} errors.")


def create_dummy_data() -> Dict:
    """テスト用データを生成 (Nested content test included)"""
    return {
        "conversations": [
            {
                "title": "Project Alpha Planning with very long title that might exceed windows path limit validation check",
                "createTime": "2025-12-01T10:00:00Z",
                "messages": [
                    {
                        "role": "user",
                        "content": "Let's plan Project Alpha.\nTODO: Create repository",
                    },
                    {"role": "model", "content": "Sure. I will create a repo for you."},
                ],
            },
            {
                "title": "Complex Nested Data",
                "createTime": "2026-01-20T15:30:00Z",
                "messages": [
                    {"role": "user", "content": {"parts": ["Nested content part 1", " part 2"]}},
                    {"role": "model", "content": "Parsed successfully."},
                ],
            },
        ]
    }


def stream_conversations(f):
    """
    JSON構造を判別してストリーミングイテレータを返す。
    ijsonが利用できない場合はjson.loadを使用する（フォールバック）。
    """
    if ijson is None:
        print("Warning: ijson module not found. Falling back to loading entire JSON into memory.")
        data = json.load(f)
        if isinstance(data, dict) and "conversations" in data:
            return data["conversations"]
        elif isinstance(data, list):
            return data
        else:
            return [data]

    # ファイルの先頭文字を読んで構造を推定
    start_pos = f.tell()
    first_char = f.read(1)
    while first_char and first_char.isspace():
        first_char = f.read(1)

    f.seek(start_pos)

    if first_char == "[":
        return ijson.items(f, "item")
    elif first_char == "{":
        return ijson.items(f, "conversations.item")
    else:
        # フォールバック
        return ijson.items(f, "item")  # Assume list if unknown or let ijson handle error


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_takeout.py [json_file_path] [output_dir]")
        print("   or: python import_takeout.py test (generates dummy data)")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "test":
        # Create dummy JSON
        with open("test_history.json", "w", encoding="utf-8") as f:
            json.dump(create_dummy_data(), f, indent=2)
        process_conversations(create_dummy_data(), "test_vault")
    else:
        input_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "vault_import"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(input_file, "r", encoding="utf-8") as f:
            # Use streaming if possible
            conversations = stream_conversations(f)
            process_conversations(conversations, output_dir)


if __name__ == "__main__":
    main()
