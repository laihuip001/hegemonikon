#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→会話履歴管理が必要→chronos_ingest が担う
"""
Chronos Ingest - 会話履歴を Chronos インデックスに自動投入

Usage:
    python chronos_ingest.py                    # 全件を投入
    python chronos_ingest.py --file <path>      # 指定ファイルを投入
    python chronos_ingest.py --chunked          # チャンク分割モード (default: True)
    python chronos_ingest.py --load --search "query"  # 検索
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, ChronosIndex

# Configuration
_HOME = Path.home()
SESSION_DIR = _HOME / "oikos" / "mneme" / ".hegemonikon" / "sessions"
DEFAULT_INDEX_PATH = _HOME / "oikos" / "mneme" / ".hegemonikon" / "indices" / "chronos.pkl"

# PURPOSE: Parse a conversation log markdown file into a Document
def parse_conversation(file_path: Path) -> Document:
    """Parse a conversation log markdown file into a Document.

    Expected filename: 2026-01-31_conv_50_Implementing O-Series Derivatives.md
    """
    content = file_path.read_text(encoding="utf-8")

    # Extract metadata from filename: YYYY-MM-DD_conv_N_Title.md
    match = re.match(r"(\d{4}-\d{2}-\d{2})_conv_(\d+)_(.+)\.md", file_path.name)
    if match:
        date_str, conv_num, title = match.groups()
        title = title.replace("_", " ")
        timestamp = f"{date_str}T00:00:00"
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        conv_num = "0"
        title = file_path.stem
        timestamp = datetime.now().isoformat()

    # Extract message count (count ## 🤖 Claude occurrences)
    msg_count = len(re.findall(r"## 🤖 Claude", content))

    # Build embedding text: Title + first 2000 chars
    embedding_text = f"{title}\n{title}\n{content[:2000]}"

    return Document(
        id=f"conv-{date_str}-{conv_num}",
        content=embedding_text,
        metadata={
            "timestamp": timestamp,
            "type": "conversation",
            "title": title,
            "conv_num": int(conv_num),
            "msg_count": msg_count,
            "file_path": str(file_path),
        },
    )


# PURPOSE: Parse a conversation into multiple chunks for better search coverage
def parse_conversation_chunks(
    file_path: Path, chunk_size: int = 1500
) -> List[Document]:
    """Parse a conversation into multiple chunks for better search coverage."""
    content = file_path.read_text(encoding="utf-8")

    # Extract metadata from filename
    match = re.match(r"(\d{4}-\d{2}-\d{2})_conv_(\d+)_(.+)\.md", file_path.name)
    if match:
        date_str, conv_num, title = match.groups()
        title = title.replace("_", " ")
        timestamp = f"{date_str}T00:00:00"
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        conv_num = "0"
        title = file_path.stem
        timestamp = datetime.now().isoformat()

    msg_count = len(re.findall(r"## 🤖 Claude", content))

    # Split by message markers (## 🤖 Claude)
    messages = re.split(r"(?=## 🤖 Claude)", content)
    messages = [m.strip() for m in messages if m.strip()]

    # Create chunks
    chunks = []
    current_chunk = f"# {title}\n\n"
    chunk_idx = 0

    for msg in messages:
        if len(current_chunk) + len(msg) > chunk_size and len(current_chunk) > 100:
            chunks.append(
                Document(
                    id=f"conv-{date_str}-{conv_num}-c{chunk_idx}",
                    content=current_chunk,
                    metadata={
                        "timestamp": timestamp,
                        "type": "conversation_chunk",
                        "title": title,
                        "conv_num": int(conv_num),
                        "chunk_idx": chunk_idx,
                        "msg_count": msg_count,
                        "file_path": str(file_path),
                    },
                )
            )
            chunk_idx += 1
            current_chunk = f"# {title}\n\n"
        current_chunk += msg + "\n\n"

    # Last chunk
    if len(current_chunk) > 100:
        chunks.append(
            Document(
                id=f"conv-{date_str}-{conv_num}-c{chunk_idx}",
                content=current_chunk,
                metadata={
                    "timestamp": timestamp,
                    "type": "conversation_chunk",
                    "title": title,
                    "conv_num": int(conv_num),
                    "chunk_idx": chunk_idx,
                    "msg_count": msg_count,
                    "file_path": str(file_path),
                },
            )
        )

    return chunks if chunks else [parse_conversation(file_path)]  # Fallback


# PURPOSE: Get all conversation log files sorted by date (newest first)
def get_conversation_files() -> List[Path]:
    """Get all conversation log files sorted by date (newest first)."""
    if not SESSION_DIR.exists():
        return []
    files = list(SESSION_DIR.glob("*_conv_*.md"))
    return sorted(files, reverse=True)


# PURPOSE: Ingest documents to Chronos index using real embeddings
def ingest_to_chronos(docs: List[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index using real embeddings."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
    # Auto-detect dimension from the model
    sample_vec = adapter.encode(["test"])
    dim = sample_vec.shape[1] if sample_vec.ndim == 2 else len(sample_vec[0])

    # Define embedding function for ChronosIndex
    def embed_fn(text):
        vecs = adapter.encode([text])
        return vecs[0]

    index = ChronosIndex(adapter, "chronos", dimension=dim, embed_fn=embed_fn)
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
    # Note: embed_fn is not persisted, so search needs to re-instantiate it or adapter directly
    # For simple search using adapter directly is enough as shown below
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
        description="Ingest conversation logs to Chronos index"
    )
    parser.add_argument("--all", action="store_true", help="Ingest all conversation logs")
    parser.add_argument("--file", type=str, help="Ingest specific file")
    parser.add_argument(
        "--chunked",
        action="store_true",
        default=True,
        help="Use chunked mode for better search coverage (default: True)",
    )
    parser.add_argument(
        "--no-chunked",
        action="store_false",
        dest="chunked",
        help="Disable chunked mode",
    )
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
    DEFAULT_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

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
                title = r.metadata.get("title", "N/A")
                if doc_type == "conversation_chunk":
                    title += f" [chunk {r.metadata.get('chunk_idx', '?')}]"

                print(f"Score: {r.score:.3f} | [{doc_type}] {title}")
                print(f"  ID: {r.metadata.get('doc_id', 'N/A')}")
                print(f"  Timestamp: {r.metadata.get('timestamp', 'N/A')}")
                print()
        return

    # Ingest mode
    docs = []

    files = []
    if args.file:
        files = [Path(args.file)]
    else:
        files = get_conversation_files()

    print(f"📝 Found {len(files)} conversation logs")

    if args.chunked:
        print("🔀 Using chunked mode for better coverage")
        for f in files:
            if not f.exists():
                print(f"Warning: File not found: {f}")
                continue
            chunks = parse_conversation_chunks(f)
            docs.extend(chunks)
            if args.file: # Verbose for single file
                print(f"  → {f.name}: {len(chunks)} chunks")
    else:
        for f in files:
            if not f.exists():
                print(f"Warning: File not found: {f}")
                continue
            print(f"Parsing: {f.name}")
            doc = parse_conversation(f)
            docs.append(doc)
            print(
                f"  → {doc.id}: {doc.metadata.get('title', 'N/A')} ({doc.metadata.get('msg_count', 0)} msgs)"
            )

    if not docs:
        print("No documents found or processed")
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
