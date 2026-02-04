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

# 設定
SESSIONS_DIR = Path(r"M:\Brain\.hegemonikon\sessions")
DB_PATH = Path(r"M:\Brain\.hegemonikon\lancedb")
TABLE_NAME = "sessions"

# Regex patterns
RE_EXPORTED_AT = re.compile(r"\d{4}-\d{2}-\d{2}T[\d:.]+")
RE_MESSAGE_COUNT = re.compile(r"(\d+)")
RE_CSS_COMMENT = re.compile(r"/\*.*?\*/", flags=re.DOTALL)
RE_CSS_MEDIA = re.compile(r"@media\s*\([^)]*\)\s*\{[^}]*\}")
RE_CSS_MARKDOWN_ALERT = re.compile(r"\.markdown[-\w]*\s*\{[^}]*\}")
RE_THOUGHT_FOR = re.compile(r"Thought for \d+s\s*")
RE_THOUGHT_FOR_LESS = re.compile(r"Thought for <\d+s\s*")
RE_MULTI_NEWLINE = re.compile(r"\n{3,}")


class SessionDocument(BaseModel):
    """セッションドキュメントのスキーマ"""

    filename: str
    title: str
    exported_at: str
    message_count: int
    content: str  # メッセージ全文
    content_preview: str  # 検索結果表示用


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
                match = RE_EXPORTED_AT.search(line)
                if match:
                    exported_at = match.group()
                break

        # メッセージ数抽出
        message_count = 0
        for line in lines[:10]:
            if "**Messages**" in line:
                match = RE_MESSAGE_COUNT.search(line)
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
        # /* ... */ コメントを除去
        full_content = RE_CSS_COMMENT.sub("", full_content)

        # @media { ... } ブロックを除去
        full_content = RE_CSS_MEDIA.sub("", full_content)

        # .markdown-alert などの CSS ルールを除去
        full_content = RE_CSS_MARKDOWN_ALERT.sub("", full_content)

        # "Thought for Xs" を除去
        full_content = RE_THOUGHT_FOR.sub("", full_content)
        full_content = RE_THOUGHT_FOR_LESS.sub("", full_content)

        # 連続する空行を除去
        full_content = RE_MULTI_NEWLINE.sub("\n\n", full_content).strip()

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


def generate_session_docs(session_files: List[Path]):
    """セッションドキュメントを生成するジェネレーター"""
    count = 0
    for filepath in session_files:
        doc = parse_session_file(filepath)
        if doc and len(doc.content) > 50:
            yield doc.model_dump()
            count += 1
            if count % 100 == 0:
                print(f"    ... processed {count} docs", end="\r")


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

    if not session_files:
        print("[!] No session files found")
        return

    # テーブルが存在する場合は削除して再作成
    # lancedb v0.27+ list_tables returns object with .tables
    tables_response = db.list_tables()
    existing_tables = getattr(tables_response, "tables", tables_response)

    if TABLE_NAME in existing_tables:
        db.drop_table(TABLE_NAME)
        print(f"[*] Dropped existing table: {TABLE_NAME}")

    print("[*] Creating table with streaming data...")
    # テーブル作成 (ジェネレーターを使用してメモリ使用量を削減)
    table = db.create_table(TABLE_NAME, generate_session_docs(session_files))

    # 行数を確認 (ジェネレーター消費後なのでここで取得)
    row_count = table.count_rows()
    print(f"\n[✓] Created table: {TABLE_NAME} ({row_count} rows)")

    # Full-Text Search インデックスを作成
    try:
        table.create_fts_index("content", replace=True)
        print(f"[✓] Created FTS index on 'content'")
    except Exception as e:
        print(f"[!] FTS index creation failed: {e}")

    print("[✓] Indexing complete!")

    return db, table


def search_sessions(query: str, limit: int = 5):
    """セッションを検索"""
    db = lancedb.connect(str(DB_PATH))

    tables_response = db.list_tables()
    existing_tables = getattr(tables_response, "tables", tables_response)

    if TABLE_NAME not in existing_tables:
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
