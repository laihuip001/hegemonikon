#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→チャット履歴管理が必要→chronos_ingest が担う
"""
Chronos Ingest - 会話履歴(Conversation history)をChronosインデックスに自動投入

Usage:
    python chronos_ingest.py                    # 全件を投入
    python chronos_ingest.py --dry-run          # パースのみ
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, ChronosIndex

_PROJECT_ROOT = Path(__file__).parent.parent.parent

# Configurable via env — defaults to mneme indices
DEFAULT_INDEX_PATH = Path(
    os.environ.get(
        "HGK_CHRONOS_INDEX",
        str(_PROJECT_ROOT.parent / "mneme" / ".hegemonikon" / "indices" / "chronos.pkl"),
    )
)

# PURPOSE: 会話ファイルリスト取得（Kairosのロジックを再利用）
def _get_conversation_files() -> list[Path]:
    from mekhane.symploke.kairos_ingest import get_conversation_files

    return get_conversation_files()


# PURPOSE: 会話ファイルのチャンク分割パース
def _parse_conversation_chunks(file_path: Path) -> list[Document]:
    from mekhane.symploke.kairos_ingest import parse_conversation_chunks

    return parse_conversation_chunks(file_path)


# PURPOSE: 会話ファイルのパース
def _parse_conversation(file_path: Path) -> Document:
    from mekhane.symploke.kairos_ingest import parse_conversation

    return parse_conversation(file_path)

# PURPOSE: Ingest documents to Chronos index using real embeddings
def ingest_to_chronos(docs: list[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index using real embeddings."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
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
def load_chronos_index(load_path: str, quiet: bool = False):
    """Load a previously saved Chronos index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
    adapter.load(load_path)
    if not quiet:
        print(f"📂 Loaded index from: {load_path} ({adapter.count()} vectors)")
    return adapter

# PURPOSE: Main execution
def main():
    parser = argparse.ArgumentParser(description="Ingest conversations to Chronos index")
    parser.add_argument("--dry-run", action="store_true", help="Parse without ingesting")
    parser.add_argument("--no-save", action="store_true", help="Skip saving to disk")
    parser.add_argument("--chunked", action="store_true", help="Use chunked mode for better search coverage (default=True)")
    parser.add_argument("--no-chunked", action="store_true", help="Disable chunked mode")
    parser.add_argument("--load", action="store_true", help="Load existing index")
    args = parser.parse_args()

    # Determine chunked mode
    use_chunked = not args.no_chunked

    # Load mode
    if args.load:
        if not DEFAULT_INDEX_PATH.exists():
            print(f"❌ Index not found: {DEFAULT_INDEX_PATH}")
            return
        adapter = load_chronos_index(str(DEFAULT_INDEX_PATH))
        return

    # Ingest mode
    docs = []

    try:
        files = _get_conversation_files()
    except Exception as e:
        print(f"Failed to find conversation files: {e}")
        files = []

    print(f"📝 Found {len(files)} conversation logs")
    if use_chunked:
        print("🔀 Using chunked mode for better coverage")
        for f in files:
            chunks = _parse_conversation_chunks(f)
            docs.extend(chunks)
            print(f"  → {f.name}: {len(chunks)} chunks")
    else:
        for f in files:
            print(f"Parsing: {f.name}")
            doc = _parse_conversation(f)
            docs.append(doc)
            print(f"  → {doc.id}: {doc.metadata.get('title', 'N/A')} ({doc.metadata.get('msg_count', 0)} msgs)")

    if not docs:
        print("No documents found")
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
