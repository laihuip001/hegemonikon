#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ]

P3 → 記憶の横断検索が必要
   → 意味記憶+エピソード記憶の統合
   → memory_search が担う

Q.E.D.

---

統合長期記憶検索 API — M8 Anamnēsis
====================================

意味記憶（chat-history-kb.py ベクトル検索）と
エピソード記憶（lancedb_indexer.py FTS）を統合した検索 API。

Usage:
    python memory_search.py "query"           # ハイブリッド検索
    python memory_search.py --vector "query"  # ベクトル検索のみ
    python memory_search.py --fts "query"     # FTS 検索のみ
"""

import sys
import subprocess
from pathlib import Path

# Paths
SCRIPTS_DIR = Path(__file__).parent
PEIRA_SCRIPTS = Path(r"M:\Hegemonikon\mekhane\peira\scripts")
ANAMNESIS_DIR = Path(r"M:\Hegemonikon\mekhane\anamnesis")


# PURPOSE: ベクトル検索（chat-history-kb.py）
def search_vector(query: str, limit: int = 3) -> str:
    """ベクトル検索（chat-history-kb.py）"""
    try:
        result = subprocess.run(
            ["python", str(PEIRA_SCRIPTS / "chat-history-kb.py"), "search", query],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        return result.stdout
    except Exception as e:
        return f"[ERROR] Vector search failed: {e}"


# PURPOSE: FTS 検索（lancedb_indexer.py）
def search_fts(query: str, limit: int = 3) -> str:
    """FTS 検索（lancedb_indexer.py）"""
    try:
        result = subprocess.run(
            ["python", str(ANAMNESIS_DIR / "lancedb_indexer.py"), "search", query],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return result.stdout
    except Exception as e:
        return f"[ERROR] FTS search failed: {e}"


# PURPOSE: モジュール検索（module_indexer.py）
def search_modules(query: str, limit: int = 3) -> str:
    """モジュール検索（module_indexer.py）"""
    try:
        result = subprocess.run(
            ["python", str(ANAMNESIS_DIR / "module_indexer.py"), "search", query],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return result.stdout
    except Exception as e:
        return f"[ERROR] Module search failed: {e}"


# PURPOSE: ハイブリッド検索（全ソースを実行）
def hybrid_search(query: str) -> str:
    """ハイブリッド検索（全ソースを実行）"""
    output = []

    output.append("[Hegemonikon] M8 Anamnēsis — 統合長期記憶検索")
    output.append(f"  クエリ: {query}")
    output.append("")

    # ベクトル検索（意味記憶）
    output.append("=== 意味記憶（ベクトル検索）===")
    vector_result = search_vector(query)
    output.append(vector_result)

    # FTS 検索（エピソード記憶）
    output.append("\n=== エピソード記憶（FTS）===")
    fts_result = search_fts(query)
    output.append(fts_result)

    # モジュール検索（開発用モジュール）
    output.append("\n=== 開発用モジュール ===")
    module_result = search_modules(query)
    output.append(module_result)

    return "\n".join(output)


# PURPOSE: 関数: main
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    # Windows UTF-8 対応
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    mode = "hybrid"
    query_start = 1

    if sys.argv[1] == "--vector":
        mode = "vector"
        query_start = 2
    elif sys.argv[1] == "--fts":
        mode = "fts"
        query_start = 2

    query = " ".join(sys.argv[query_start:])

    if not query:
        print("Error: No query provided")
        sys.exit(1)

    if mode == "vector":
        print(search_vector(query))
    elif mode == "fts":
        print(search_fts(query))
    else:
        print(hybrid_search(query))


if __name__ == "__main__":
    main()
