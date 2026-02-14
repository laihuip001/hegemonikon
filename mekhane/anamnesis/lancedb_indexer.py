#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/anamnesis/
r"""
PROOF: [L2/インフラ]

P3 → セッションの検索が必要
   → LanceDB によるセッション索引
   → lancedb_indexer が担う

Q.E.D.

---

LanceDB インデクサー for セッションファイル

M:\Brain\.hegemonikon\sessions\ に保存されたセッションファイルを
LanceDB にインデックスし、全文検索・ベクトル検索を可能にする。
"""

import re
from pathlib import Path
from typing import List, Optional

import lancedb
from pydantic import BaseModel
from mekhane.anamnesis.lancedb_compat import get_table_names

# 設定
SESSIONS_DIR = Path(r"M:\Brain\.hegemonikon\sessions")
DB_PATH = Path(r"M:\Brain\.hegemonikon\lancedb")
TABLE_NAME = "sessions"

# Compiled Regexes
RE_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RE_MEDIA = re.compile(r"@media\s*\([^)]*\)\s*\{[^}]*\}")
RE_MARKDOWN_CSS = re.compile(r"\.markdown[-\w]*\s*\{[^}]*\}")
RE_THOUGHT = re.compile(r"Thought for <?\d+s\s*")
RE_NEWLINES = re.compile(r"\n{3,}")
RE_EXPORTED = re.compile(r"\d{4}-\d{2}-\d{2}T[\d:.]+")
RE_MESSAGES = re.compile(r"(\d+)")


# PURPOSE: セッションドキュメントのスキーマ
class SessionDocument(BaseModel):
    """セッションドキュメントのスキーマ"""

    filename: str
    title: str
    exported_at: str
    message_count: int
    content: str  # メッセージ全文
    content_preview: str  # 検索結果表示用


# PURPOSE: セッション md ファイルをパースしてドキュメントに変換
def parse_session_file(filepath: Path) -> Optional[SessionDocument]:
    """セッション md ファイルをパースしてドキュメントに変換"""
    try:
        # Optimized single-pass streaming parser
        with filepath.open(encoding="utf-8") as f:
            title = "Untitled"
            exported_at = ""
            message_count = 0

            body_lines = []
            in_body = False
            line_count = 0

            for line in f:
                stripped = line.strip()

                if not in_body:
                    line_count += 1

                    # Metadata extraction (limited to first few lines)
                    if line_count <= 5:
                        if line.startswith("# "):
                            title = line[2:].strip()

                    if line_count <= 10:
                        if "**Exported**" in line and not exported_at:
                            match = RE_EXPORTED.search(line)
                            if match:
                                exported_at = match.group()

                        if "**Messages**" in line and message_count == 0:
                            match = RE_MESSAGES.search(line)
                            if match:
                                message_count = int(match.group(1))

                    if stripped == "---":
                        in_body = True
                    continue

                # In body
                if line.startswith("## 🤖") or line.startswith("## 👤"):
                    continue
                if stripped == "---":
                    continue
                if stripped:
                    body_lines.append(stripped)

        full_content = "\n".join(body_lines)

        # CSS ノイズを除去
        full_content = RE_COMMENT.sub("", full_content)
        full_content = RE_MEDIA.sub("", full_content)
        full_content = RE_MARKDOWN_CSS.sub("", full_content)
        full_content = RE_THOUGHT.sub("", full_content)

        # 連続する空行を除去
        full_content = RE_NEWLINES.sub("\n\n", full_content).strip()

        # プレビュー（最初の 500 文字）
        preview = full_content[:500].replace("\n", " ")

        return SessionDocument(
            filename=filepath.name,
            title=title,
            exported_at=exported_at,
            message_count=message_count,
            content=full_content[:10000],  # 最大 10KB
            content_preview=preview,
        )

    except Exception as e:
        print(f"[!] Error parsing {filepath.name}: {e}")
        return None


# PURPOSE: 全セッションファイルをインデックス
def index_sessions():
    """全セッションファイルをインデックス"""
    print("[*] LanceDB Session Indexer")
    print(f"    Sessions: {SESSIONS_DIR}")
    print(f"    Database: {DB_PATH}")

    # データベース接続
    DB_PATH.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(DB_PATH))

    # セッションファイルを収集
    session_files = list(SESSIONS_DIR.glob("*.md"))
    print(f"[*] Found {len(session_files)} session files")

    # ドキュメントを作成
    documents: List[SessionDocument] = []

    for filepath in session_files:
        doc = parse_session_file(filepath)
        if doc and len(doc.content) > 50:
            documents.append(doc)

    print(f"[*] Parsed {len(documents)} valid documents")

    if not documents:
        print("[!] No documents to index")
        return

    # テーブルが存在する場合は削除して再作成
    if TABLE_NAME in get_table_names(db):
        db.drop_table(TABLE_NAME)
        print(f"[*] Dropped existing table: {TABLE_NAME}")

    # ドキュメントを辞書に変換
    data = [doc.model_dump() for doc in documents]

    # テーブル作成
    table = db.create_table(TABLE_NAME, data)
    print(f"[✓] Created table: {TABLE_NAME} ({len(documents)} rows)")

    # Full-Text Search インデックスを作成
    try:
        table.create_fts_index("content", replace=True)
        print(f"[✓] Created FTS index on 'content'")
    except Exception as e:
        print(f"[!] FTS index creation failed: {e}")

    print("[✓] Indexing complete!")

    return db, table


# PURPOSE: セッションを検索
def search_sessions(query: str, limit: int = 5):
    """セッションを検索"""
    db = lancedb.connect(str(DB_PATH))

    if TABLE_NAME not in get_table_names(db):
        print("[!] No sessions indexed. Run index_sessions() first.")
        return []

    table = db.open_table(TABLE_NAME)

    # Full-Text Search
    try:
        results = table.search(query, query_type="fts").limit(limit).to_list()
        return results
    except Exception as e:
        print(f"[!] Search error: {e}")
        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "search":
        # 検索モード
        if len(sys.argv) < 3:
            print("Usage: python lancedb_indexer.py search <query>")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        print(f"[*] Searching for: {query}")

        results = search_sessions(query)

        if results:
            print(f"\n=== Found {len(results)} results ===\n")
            for i, r in enumerate(results, 1):
                print(f"[{i}] {r['title']}")
                print(f"    File: {r['filename']}")
                print(f"    Preview: {r['content_preview'][:100]}...")
                print()
        else:
            print("[!] No results found")
    else:
        # インデックスモード
        index_sessions()
