#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→sophia_ingest が担う
"""
Sophia Ingest - Knowledge Items を Sophia インデックスに自動投入

Usage:
    python sophia_ingest.py                    # 全KIを投入
    python sophia_ingest.py --dry-run          # パースのみ
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, SophiaIndex

KNOWLEDGE_DIR = Path("/home/laihuip001/oikos/.gemini/antigravity/knowledge")


def parse_ki_directory(ki_path: Path) -> list[Document]:
    """Parse a KI directory into Documents.

    Note: Uses rglob to capture nested .md files in subdirectories.
    """
    docs = []

    # Read metadata.json
    metadata_file = ki_path / "metadata.json"
    if not metadata_file.exists():
        return docs

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    ki_name = metadata.get("name", ki_path.name)
    summary = metadata.get("summary", "")

    # Read artifact files (including nested directories)
    artifacts_dir = ki_path / "artifacts"
    if artifacts_dir.exists():
        for artifact_file in artifacts_dir.rglob("*.md"):  # Changed: glob -> rglob
            content = artifact_file.read_text(encoding="utf-8")

            # Use relative path from artifacts_dir as part of ID
            rel_path = artifact_file.relative_to(artifacts_dir)
            doc_id = (
                f"ki-{ki_path.name}-{str(rel_path.with_suffix('')).replace('/', '-')}"
            )

            doc = Document(
                id=doc_id,
                content=f"{ki_name}\n\n{summary}\n\n{content[:1500]}",  # Combine for context
                metadata={
                    "type": "knowledge_item",
                    "ki_name": ki_name,
                    "summary": summary[:200],
                    "artifact": artifact_file.name,
                    "file_path": str(artifact_file),
                    "subdir": (
                        str(rel_path.parent) if rel_path.parent != Path(".") else None
                    ),
                },
            )
            docs.append(doc)

    # If no artifacts, create doc from summary
    if not docs and summary:
        docs.append(
            Document(
                id=f"ki-{ki_path.name}",
                content=f"{ki_name}\n\n{summary}",
                metadata={
                    "type": "knowledge_item",
                    "ki_name": ki_name,
                    "summary": summary[:200],
                },
            )
        )

    return docs


def get_ki_directories() -> list[Path]:
    """Get all KI directories."""
    dirs = [d for d in KNOWLEDGE_DIR.iterdir() if d.is_dir()]
    return sorted(dirs)


def ingest_to_sophia(docs: list[Document], save_path: str = None) -> int:
    """Ingest documents to Sophia index using real embeddings (returns count).

    Args:
        docs: Documents to ingest
        save_path: If provided, save the index to this path after ingestion
    """
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    index = SophiaIndex(adapter, "sophia", dimension=384)  # MiniLM = 384 dims
    index.initialize()

    count = index.ingest(docs)
    print(f"Ingested {count} documents to Sophia (real embeddings)")

    if save_path:
        adapter.save(save_path)
        print(f"💾 Saved index to: {save_path}")

    return count


def load_sophia_index(load_path: str):
    """Load a previously saved Sophia index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    adapter.load(load_path)
    print(f"📂 Loaded index from: {load_path} ({adapter.count()} vectors)")
    return adapter


def search_loaded_index(adapter, query: str, top_k: int = 5):
    """Search using a loaded adapter directly."""
    # Encode query
    query_vec = adapter.encode([query])[0]
    results = adapter.search(query_vec, k=top_k)
    return results


# デフォルトの保存パス
DEFAULT_INDEX_PATH = Path(
    "/home/laihuip001/oikos/mneme/.hegemonikon/indices/sophia.pkl"
)


def get_boot_ki(context: str = None, mode: str = "standard") -> dict:
    """
    /boot 統合 API: コンテキストに基づいて関連 KI を自動プッシュ

    Args:
        context: 現在のセッションコンテキスト（Handoff の主題や目的など）
        mode: "fast" (0件), "standard" (3件), "detailed" (5件)

    Returns:
        dict: {
            "ki_items": List[dict],  # 関連 KI リスト
            "count": int
        }
    """
    # モードによる件数
    top_k = {"fast": 0, "standard": 3, "detailed": 5}.get(mode, 3)

    if top_k == 0 or not context:
        return {"ki_items": [], "count": 0}

    # インデックス読み込み
    if not DEFAULT_INDEX_PATH.exists():
        return {"ki_items": [], "count": 0}

    adapter = load_sophia_index(str(DEFAULT_INDEX_PATH))

    # 検索
    results = search_loaded_index(adapter, context, top_k=top_k)

    # 結果を整形
    ki_items = []
    for r in results:
        ki_items.append(
            {
                "ki_name": r.metadata.get("ki_name", "Unknown"),
                "summary": r.metadata.get("summary", ""),
                "artifact": r.metadata.get("artifact", ""),
                "score": r.score,
                "file_path": r.metadata.get("file_path", ""),
            }
        )

    return {"ki_items": ki_items, "count": len(ki_items)}


def format_ki_output(result: dict) -> str:
    """
    /boot 用の KI 出力フォーマット
    """
    if not result["ki_items"]:
        return "📚 関連する知識: なし"

    lines = [f"📚 今日関連しそうな知識 ({result['count']}件):"]

    for item in result["ki_items"]:
        ki_name = item["ki_name"]
        summary = (
            item["summary"][:60] + "..."
            if len(item["summary"]) > 60
            else item["summary"]
        )
        lines.append(f"  • [{ki_name}] {summary}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ingest KIs to Sophia index")
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse only, don't ingest"
    )
    parser.add_argument(
        "--save", action="store_true", help="Save index after ingestion (default: True)"
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save index after ingestion"
    )
    parser.add_argument(
        "--load", action="store_true", help="Load existing index and show stats"
    )
    parser.add_argument("--search", type=str, help="Search query (requires --load)")
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only ingest new/modified KIs (diff mode)",
    )
    args = parser.parse_args()

    # Ensure index directory exists
    DEFAULT_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load mode
    if args.load:
        if not DEFAULT_INDEX_PATH.exists():
            print(f"❌ Index not found: {DEFAULT_INDEX_PATH}")
            return
        adapter = load_sophia_index(str(DEFAULT_INDEX_PATH))

        if args.search:
            results = search_loaded_index(adapter, args.search, top_k=5)
            print(f"\n=== Search: {args.search} ===")
            for r in results:
                print(f"Score: {r.score:.3f} | {r.metadata.get('doc_id', 'N/A')}")
                print(f"  KI: {r.metadata.get('ki_name', 'N/A')}")
                print(f"  Summary: {r.metadata.get('summary', 'N/A')[:80]}...")
                print()
        return

    # Ingest mode
    ki_dirs = get_ki_directories()
    print(f"Found {len(ki_dirs)} KI directories")

    all_docs = []
    for ki_dir in ki_dirs:
        print(f"\nParsing: {ki_dir.name}")
        docs = parse_ki_directory(ki_dir)
        for doc in docs:
            print(f"  → {doc.id}")
            all_docs.append(doc)

    print(f"\nTotal: {len(all_docs)} documents")

    # Incremental mode: filter out existing docs
    if args.incremental and DEFAULT_INDEX_PATH.exists():
        adapter = load_sophia_index(str(DEFAULT_INDEX_PATH))
        existing_count = adapter.count()

        # Get existing doc IDs from adapter metadata
        existing_ids = set()
        if existing_count > 0:
            # Use a broad search to get all existing docs
            dummy_vec = adapter.encode([""])[0]
            existing_results = adapter.search(dummy_vec, k=existing_count)
            existing_ids = {r.metadata.get("doc_id", "") for r in existing_results}

        # Filter to only new docs
        new_docs = [d for d in all_docs if d.id not in existing_ids]
        skipped = len(all_docs) - len(new_docs)

        print(
            f"\n[Incremental] Existing: {len(existing_ids)}, New: {len(new_docs)}, Skipped: {skipped}"
        )

        if not new_docs:
            print("No new documents to ingest.")
            return

        all_docs = new_docs

    if args.dry_run:
        print("\n[Dry run] Would ingest documents")
        return

    # Save by default unless --no-save
    save_path = None if args.no_save else str(DEFAULT_INDEX_PATH)
    ingest_to_sophia(all_docs, save_path=save_path)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
