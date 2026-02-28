#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→chronos_ingest が担う
"""
Chronos Ingest - 会話履歴 (Conversation logs) を Chronos インデックスに自動投入

Usage:
    python chronos_ingest.py                    # 最新1件を投入
    python chronos_ingest.py --all              # 全件を投入
    python chronos_ingest.py --file <path>      # 指定ファイルを投入
    python chronos_ingest.py --load --search "query"  # 検索
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, ChronosIndex
from mekhane.symploke.kairos_ingest import (
    HANDOFF_DIR,
    get_conversation_files,
    parse_conversation,
    parse_conversation_chunks,
)

from mekhane.symploke.kairos_ingest import DEFAULT_INDEX_PATH as KAIROS_INDEX_PATH
DEFAULT_INDEX_PATH = KAIROS_INDEX_PATH.parent / "chronos.pkl"

# PURPOSE: Ingest documents to Chronos index using real embeddings
def ingest_to_chronos(docs: list[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index using real embeddings."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
    # Auto-detect dimension from the model (bge-m3 = 1024d, MiniLM = 384d)
    sample_vec = adapter.encode(["test"])
    dim = sample_vec.shape[1] if sample_vec.ndim == 2 else len(sample_vec[0])
    index = ChronosIndex(adapter, "chronos", dimension=dim)
    index.initialize()

    count = index.ingest(docs)
    print(f"Ingested {count} documents to Chronos (real embeddings)")

    if save_path:
        adapter.save(save_path)
        print(f"💾 Saved index to: {save_path}")

    return count

# PURPOSE: Load a previously saved Chronos index
def load_chronos_index(load_path: str):
    """Load a previously saved Chronos index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
    adapter.load(load_path)
    print(f"📂 Loaded index from: {load_path} ({adapter.count()} vectors)")
    return adapter

# PURPOSE: Search using a loaded adapter directly
def search_loaded_index(adapter, query: str, top_k: int = 5):
    """Search using a loaded adapter directly."""
    query_vec = adapter.encode([query])[0]
    results = adapter.search(query_vec, k=top_k)
    return results

# PURPOSE: main の処理
def main():
    parser = argparse.ArgumentParser(
        description="Ingest conversations to Chronos index"
    )
    parser.add_argument("--all", action="store_true", help="Ingest all conversation files")
    parser.add_argument(
        "--chunked",
        action="store_true",
        help="Use chunked mode for better search coverage (default)",
    )
    parser.add_argument(
        "--no-chunked",
        dest="chunked",
        action="store_false",
        help="Do not use chunked mode",
    )
    parser.set_defaults(chunked=True)
    parser.add_argument("--file", type=str, help="Ingest specific file")
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse only, don't ingest"
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save index after ingestion"
    )
    parser.add_argument("--load", action="store_true", help="Load existing index")
    parser.add_argument("--search", type=str, help="Search query (requires --load)")
    args = parser.parse_args()

    # Ensure index directory exists
    try:
        DEFAULT_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create index directory: {e}")

    # Load mode
    if args.load:
        if not DEFAULT_INDEX_PATH.exists():
            print(f"❌ Index not found: {DEFAULT_INDEX_PATH}")
            return
        adapter = load_chronos_index(str(DEFAULT_INDEX_PATH))

        if args.search:
            results = search_loaded_index(adapter, args.search, top_k=5)
            print(f"\n=== Search: {args.search} ===")
            for r in results:
                doc_type = r.metadata.get("type", "unknown")
                label = r.metadata.get("title", "N/A")
                if doc_type == "conversation_chunk":
                    label += f" [chunk {r.metadata.get('chunk_idx', '?')}]"
                print(f"Score: {r.score:.3f} | [{doc_type}] {label}")
                print(f"  ID: {r.metadata.get('doc_id', 'N/A')}")
                print(f"  Timestamp: {r.metadata.get('timestamp', 'N/A')}")
                print()
        return

    # Ingest mode
    docs = []

    # Collect conversation files
    if args.file:
        files = [Path(args.file)]
        for f in files:
            print(f"Parsing: {f.name}")
            if args.chunked:
                chunks = parse_conversation_chunks(f)
                docs.extend(chunks)
                print(f"  → {f.name}: {len(chunks)} chunks")
            else:
                doc = parse_conversation(f)
                docs.append(doc)
                print(f"  → {doc.id}: {doc.metadata.get('title', 'N/A')}")
    elif args.all:
        files = get_conversation_files()
        print(f"📝 Found {len(files)} conversation logs")
        for f in files:
            if args.chunked:
                chunks = parse_conversation_chunks(f)
                docs.extend(chunks)
            else:
                doc = parse_conversation(f)
                docs.append(doc)
    else:
        # Default: latest conversation log only
        files = get_conversation_files()[:1]
        for f in files:
            print(f"Parsing: {f.name}")
            if args.chunked:
                chunks = parse_conversation_chunks(f)
                docs.extend(chunks)
                print(f"  → {f.name}: {len(chunks)} chunks")
            else:
                doc = parse_conversation(f)
                docs.append(doc)
                print(f"  → {doc.id}: {doc.metadata.get('title', 'N/A')}")

    if not docs:
        print("No files found")
        return

    if args.dry_run:
        print(f"\n[Dry run] Would ingest {len(docs)} documents")
        return

    # Save by default unless --no-save
    save_path = None if args.no_save else str(DEFAULT_INDEX_PATH)
    ingest_to_chronos(docs, save_path=save_path)
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
