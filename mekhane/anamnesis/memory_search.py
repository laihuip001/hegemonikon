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
import importlib.util
from pathlib import Path

# Paths
SCRIPTS_DIR = Path(__file__).parent
PEIRA_SCRIPTS = SCRIPTS_DIR.parent / "peira" / "scripts"
ANAMNESIS_DIR = SCRIPTS_DIR

# Import indexers directly
try:
    # Try importing as part of the mekhane package
    from mekhane.anamnesis import lancedb_indexer, module_indexer
except ImportError:
    # Fallback for script execution
    sys.path.append(str(ANAMNESIS_DIR))
    import lancedb_indexer
    import module_indexer

# Dynamically import chat-history-kb (due to hyphens in filename)
def import_chat_history_kb():
    try:
        spec = importlib.util.spec_from_file_location(
            "chat_history_kb", PEIRA_SCRIPTS / "chat-history-kb.py"
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception as e:
        # Silently fail if file not found (will be handled in search_vector)
        return None

chat_history_kb = import_chat_history_kb()


# PURPOSE: ベクトル検索（chat-history-kb.py）
def search_vector(query: str, limit: int = 3) -> str:
    """ベクトル検索（chat-history-kb.py）"""
    if not chat_history_kb:
        return "[ERROR] Vector search unavailable (module not loaded)"

    try:
        results = chat_history_kb.search_chat_history(query, n_results=limit)

        output = []
        output.append(f'\n[SEARCH] Query: "{query}"\n')
        output.append("-" * 60)

        if results:
            for i, r in enumerate(results):
                output.append(f"\n[{i+1}] Session: {r['session_id'][:8]}...")
                output.append(f"    Type: {r['artifact_type']}")
                output.append(f"    Summary: {r['summary'][:100]}...")
                output.append(f"    Updated: {r['updated_at']}")
        else:
            output.append("\nNo results found.")

        output.append("\n" + "-" * 60)
        return "\n".join(output)
    except Exception as e:
        return f"[ERROR] Vector search failed: {e}"


# PURPOSE: FTS 検索（lancedb_indexer.py）
def search_fts(query: str, limit: int = 3) -> str:
    """FTS 検索（lancedb_indexer.py）"""
    try:
        results = lancedb_indexer.search_sessions(query, limit=limit)

        output = []
        if results:
            output.append(f"\n=== Found {len(results)} results ===\n")
            for i, r in enumerate(results, 1):
                output.append(f"[{i}] {r['title']}")
                output.append(f"    File: {r['filename']}")
                output.append(f"    Preview: {r['content_preview'][:100]}...")
                output.append("")
        else:
            output.append("[!] No results found")

        return "\n".join(output)
    except Exception as e:
        return f"[ERROR] FTS search failed: {e}"


# PURPOSE: モジュール検索（module_indexer.py）
def search_modules(query: str, limit: int = 3) -> str:
    """モジュール検索（module_indexer.py）"""
    try:
        results = module_indexer.search_modules(query, limit=limit)

        output = []
        if results:
            output.append(f"\n=== Found {len(results)} results ===\n")
            for i, r in enumerate(results, 1):
                output.append(f"[{i}] {r['title']}")
                output.append(f"    Category: {r['category']}")
                output.append(f"    File: {r['filename']}")
                output.append(f"    Preview: {r['content_preview'][:100]}...")
                output.append("")
        else:
            output.append("[!] No results found")

        return "\n".join(output)
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


# PURPOSE: CLI エントリポイント — 知識基盤の直接実行
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
