#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L3/ユーティリティ]

P3 → 開発モジュールの検索が必要
   → LanceDB での FTS 索引
   → module_indexer が担う

Q.E.D.

---

開発用モジュール インデクサー

.agent/skills/ 以下の全スキルモジュールを LanceDB にインデックスする。
HGK_MODULES_DIR 環境変数でソースディレクトリを変更可能。
"""

from pathlib import Path
import os
from typing import List, Optional

import lancedb
from pydantic import BaseModel

# 設定 — 環境変数でオーバーライド可能
_PROJECT_ROOT = Path(__file__).parent.parent.parent
MODULES_DIR = Path(
    os.environ.get(
        "HGK_MODULES_DIR",
        str(_PROJECT_ROOT / ".agent" / "skills"),
    )
)
DB_PATH = Path(
    os.environ.get(
        "HGK_MODULE_DB_PATH",
        str(_PROJECT_ROOT / "gnosis_data" / "lancedb"),
    )
)
TABLE_NAME = "dev_modules"


# PURPOSE: モジュールドキュメントのスキーマ
class ModuleDocument(BaseModel):
    """モジュールドキュメントのスキーマ"""

    filename: str
    title: str
    category: str  # hypervisor or individual
    content: str
    content_preview: str


# PURPOSE: モジュール md ファイルをパースしてドキュメントに変換
def parse_module_file(filepath: Path, category: str) -> Optional[ModuleDocument]:
    """モジュール md ファイルをパースしてドキュメントに変換"""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        # タイトル抽出（# で始まる行）
        title = filepath.stem
        for line in lines[:5]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # コンテンツをクリーンアップ
        full_content = content.strip()

        # プレビュー（最初の 500 文字）
        preview = full_content[:500].replace("\n", " ")

        return ModuleDocument(
            filename=filepath.name,
            title=title,
            category=category,
            content=full_content[:15000],  # 最大 15KB
            content_preview=preview,
        )

    except Exception as e:
        print(f"[!] Error parsing {filepath.name}: {e}")
        return None


# PURPOSE: 全モジュールファイルをインデックス
def index_modules():
    """全モジュールファイルをインデックス"""
    print("[*] 開発用モジュール インデクサー")
    print(f"    Modules: {MODULES_DIR}")
    print(f"    Database: {DB_PATH}")

    # データベース接続
    DB_PATH.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(DB_PATH))

    # モジュールファイルを収集
    documents: List[ModuleDocument] = []

    # ハイパーバイザー
    hypervisor_dir = MODULES_DIR / "ハイパーバイザー（Hypervisor）"
    if hypervisor_dir.exists():
        for filepath in hypervisor_dir.glob("*.md"):
            doc = parse_module_file(filepath, "hypervisor")
            if doc:
                documents.append(doc)
                print(f"    [+] Hypervisor: {filepath.name}")

    # 個別モジュール
    individual_dir = MODULES_DIR / "個別のモジュール"
    if individual_dir.exists():
        for filepath in individual_dir.glob("*.md"):
            doc = parse_module_file(filepath, "individual")
            if doc:
                documents.append(doc)
                print(f"    [+] Module: {filepath.name}")

    print(f"\n[*] Parsed {len(documents)} modules")

    if not documents:
        print("[!] No modules to index")
        return

    # テーブルが存在する場合は削除して再作成
    if TABLE_NAME in db.list_tables():
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

    print("[✓] モジュールインデックス完了!")

    return db, table


# PURPOSE: モジュールを検索
def search_modules(query: str, limit: int = 5):
    """モジュールを検索"""
    db = lancedb.connect(str(DB_PATH))

    if TABLE_NAME not in db.list_tables():
        print("[!] No modules indexed. Run index_modules() first.")
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
            print("Usage: python module_indexer.py search <query>")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        print(f"[*] Searching modules for: {query}")

        results = search_modules(query)

        if results:
            print(f"\n=== Found {len(results)} results ===\n")
            for i, r in enumerate(results, 1):
                print(f"[{i}] {r['title']}")
                print(f"    Category: {r['category']}")
                print(f"    File: {r['filename']}")
                print(f"    Preview: {r['content_preview'][:100]}...")
                print()
        else:
            print("[!] No results found")
    else:
        # インデックスモード
        index_modules()
