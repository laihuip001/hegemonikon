#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/
"""
Chronos Ingest - Conversation History を LanceDB に自動投入

Usage:
    python chronos_ingest.py
"""

import re
import sys
from pathlib import Path
from typing import List, Optional

import lancedb
from pydantic import BaseModel

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# デフォルト設定 (overridable)
DEFAULT_SESSION_DIR = Path.home() / "oikos/.gemini/antigravity/conversations"
DEFAULT_DB_PATH = Path.home() / "oikos/mneme/.hegemonikon/lancedb"
TABLE_NAME = "sessions"

class SessionDocument(BaseModel):
    """セッションドキュメントのスキーマ"""
    filename: str
    title: str
    exported_at: str
    message_count: int
    content: str  # メッセージ全文
    content_preview: str  # 検索結果表示用

def get_session_files(directory: Path = DEFAULT_SESSION_DIR) -> List[Path]:
    """Get all session files from directory."""
    if not directory.exists():
        return []
    return list(directory.glob("*.md"))

def parse_session_file(filepath: Path) -> Optional[SessionDocument]:
    """セッション md ファイルをパースしてドキュメントに変換"""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        # タイトル抽出（# で始まる行）
        title = "Untitled"
        for line in lines[:5]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # エクスポート日時抽出
        exported_at = ""
        for line in lines[:10]:
            if "**Exported**" in line:
                match = re.search(r"\d{4}-\d{2}-\d{2}T[\d:.]+", line)
                if match:
                    exported_at = match.group()
                break

        # メッセージ数抽出
        message_count = 0
        for line in lines[:10]:
            if "**Messages**" in line:
                match = re.search(r"(\d+)", line)
                if match:
                    message_count = int(match.group(1))
                break

        # メッセージ本文抽出（--- 以降）
        body_start = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                body_start = i + 1
                break

        body_lines = []
        for line in lines[body_start:]:
            # ヘッダーとセパレータをスキップ
            if line.startswith("## 🤖") or line.startswith("## 👤"):
                continue
            if line.strip() == "---":
                continue
            if line.strip():
                body_lines.append(line.strip())

        full_content = "\n".join(body_lines)

        # CSS ノイズを除去
        full_content = re.sub(r"/\*.*?\*/", "", full_content, flags=re.DOTALL)
        full_content = re.sub(r"@media\s*\([^)]*\)\s*\{[^}]*\}", "", full_content)
        full_content = re.sub(r"\.markdown[-\w]*\s*\{[^}]*\}", "", full_content)
        full_content = re.sub(r"Thought for \d+s\s*", "", full_content)
        full_content = re.sub(r"Thought for <\d+s\s*", "", full_content)
        full_content = re.sub(r"\n{3,}", "\n\n", full_content).strip()

        # プレビュー（最初の 500 文字）
        preview = full_content[:500].replace("\n", " ")

        return SessionDocument(
            filename=filepath.name,
            title=title,
            exported_at=exported_at,
            message_count=message_count,
            content=full_content[:10000],
            content_preview=preview,
        )

    except Exception as e:
        print(f"[!] Error parsing {filepath.name}: {e}")
        return None

def ingest_to_chronos(docs: List[SessionDocument], db_path: Path = DEFAULT_DB_PATH) -> int:
    """Ingest documents to LanceDB (returns count)."""
    if not docs:
        # print("[!] No documents to index")
        return 0

    print(f"[*] Ingesting {len(docs)} documents to {db_path}")

    # データベース接続
    db_path.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(db_path))

    # テーブルが存在する場合は削除して再作成
    # Note: Incremental update logic could be added here
    if TABLE_NAME in db.list_tables():
        db.drop_table(TABLE_NAME)
        # print(f"[*] Dropped existing table: {TABLE_NAME}")

    # ドキュメントを辞書に変換
    data = [doc.model_dump() for doc in docs]

    # テーブル作成
    table = db.create_table(TABLE_NAME, data)
    print(f"[✓] Created table: {TABLE_NAME} ({len(docs)} rows)")

    # Full-Text Search インデックスを作成
    try:
        table.create_fts_index("content", replace=True)
        print(f"[✓] Created FTS index on 'content'")
    except Exception as e:
        print(f"[!] FTS index creation failed: {e}")

    return len(docs)

def search_chronos(query: str, db_path: Path = DEFAULT_DB_PATH, limit: int = 5):
    """Search Chronos index."""
    if not db_path.exists():
        return []

    db = lancedb.connect(str(db_path))
    if TABLE_NAME not in db.list_tables():
        return []

    table = db.open_table(TABLE_NAME)

    try:
        results = table.search(query, query_type="fts").limit(limit).to_list()
        return results
    except Exception as e:
        print(f"[!] Search error: {e}")
        return []

if __name__ == "__main__":
    # Simple CLI for testing
    import argparse
    parser = argparse.ArgumentParser(description="Chronos Ingest CLI")
    parser.add_argument("--search", type=str, help="Search query")
    args = parser.parse_args()

    if args.search:
        results = search_chronos(args.search)
        for r in results:
            print(f"- {r['title']} ({r['filename']})")
    else:
        files = get_session_files()
        docs = []
        for f in files:
            d = parse_session_file(f)
            if d:
                docs.append(d)
        ingest_to_chronos(docs)
