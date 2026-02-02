#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→chronos_ingest が担う
"""
Chronos Ingest - Conversation History を Chronos インデックスに自動投入

Usage:
    python chronos_ingest.py                    # 全件を投入
    python chronos_ingest.py --dry-run          # パースのみ
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

# Configuration with environment variable fallback
SESSIONS_DIR = Path(
    os.environ.get(
        "SYMPLOKE_SESSIONS_DIR", "/home/laihuip001/oikos/mneme/.hegemonikon/sessions"
    )
)
DEFAULT_INDEX_PATH = Path(
    os.environ.get(
        "SYMPLOKE_CHRONOS_INDEX",
        "/home/laihuip001/oikos/mneme/.hegemonikon/indices/chronos.pkl",
    )
)


def parse_conversation_chunks(
    file_path: Path, chunk_size: int = 1500
) -> list[Document]:
    """Parse a conversation into multiple chunks for better search coverage.

    各ファイルを複数チャンクに分割し、より細かい粒度で検索可能にする。
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
        return []

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

    msg_count = len(re.findall(r"## 🤖 Claude", content))

    # Split by message markers (## 🤖 Claude)
    # Using a lookahead to keep the delimiter
    messages = re.split(r"(?=## 🤖 Claude|## 👤 User)", content)
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
                        "session_id": f"{date_str}-{conv_num}",
                        "content": current_chunk[:1000],  # Store preview for search results
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
                    "session_id": f"{date_str}-{conv_num}",
                    "content": current_chunk[:1000],  # Store preview for search results
                },
            )
        )

    # Fallback if no chunks created (e.g. very short content)
    if not chunks:
        chunks.append(
            Document(
                id=f"conv-{date_str}-{conv_num}",
                content=content[:2000],
                metadata={
                    "timestamp": timestamp,
                    "type": "conversation",
                    "title": title,
                    "conv_num": int(conv_num),
                    "msg_count": msg_count,
                    "file_path": str(file_path),
                    "session_id": f"{date_str}-{conv_num}",
                    "content": content[:1000],  # Store preview for search results
                },
            )
        )

    return chunks


def get_conversation_files() -> list[Path]:
    """Get all conversation log files sorted by date (newest first)."""
    if not SESSIONS_DIR.exists():
        return []
    files = list(SESSIONS_DIR.glob("*_conv_*.md"))
    return sorted(files, reverse=True)


def ingest_to_chronos(docs: list[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index using real embeddings."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    # ChronosIndex uses time decay, handled in its search method.
    # We pass embed_fn to ensure real embeddings are generated (if sentence_transformers is available)
    index = ChronosIndex(
        adapter,
        "chronos",
        dimension=384,
        embed_fn=lambda x: adapter.encode([x])[0],
    )
    index.initialize()

    count = index.ingest(docs)
    print(f"Ingested {count} documents to Chronos (real embeddings)")

    if save_path:
        # Ensure parent directory exists
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            adapter.save(save_path)
            print(f"💾 Saved index to: {save_path}")
        except PermissionError:
            print(f"❌ Permission denied: Cannot save to {save_path}")
        except Exception as e:
            print(f"❌ Error saving index: {e}")

    return count


def load_chronos_index(load_path: str):
    """Load a previously saved Chronos index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    adapter.load(load_path)
    print(f"📂 Loaded index from: {load_path} ({adapter.count()} vectors)")
    return adapter


def search_loaded_index(adapter, query: str, top_k: int = 5):
    """Search using a loaded adapter directly (via ChronosIndex wrapper for time decay)."""
    # To use time decay, we need to wrap the adapter in ChronosIndex again
    # assuming we can re-instantiate it.
    # However, ChronosIndex keeps _doc_store in memory which is lost if we just load the adapter.
    # The adapter only stores vectors and metadata.
    # ChronosIndex.search uses metadata['timestamp'] for decay.
    # So we can just use ChronosIndex logic here.

    # We need to populate _doc_store if we want full content,
    # but adapter search returns metadata which might be enough for a CLI search result
    # or the adapter might have content in metadata if configured so.
    # But usually _doc_store is ephemeral unless persisted separately.
    # For now, we will rely on metadata returned by adapter.

    # We need to initialize it to set the adapter? No, constructor sets it.
    # But search calls self._embed(query).
    # And adapter.search needs vectors.

    # Since we can't easily reconstruct _doc_store without re-reading files,
    # we will do a basic search here, similar to kairos_ingest.

    query_vec = adapter.encode([query])[0]
    results = adapter.search(query_vec, k=top_k)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Ingest conversation logs to Chronos index"
    )
    parser.add_argument("--all", action="store_true", help="Ingest all conversation logs (default)")
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
    except PermissionError:
        # Ignore permission error here, it will be caught during save if needed.
        # This allows dry-run to proceed even if directory is not writable.
        pass
    except Exception as e:
        print(f"Warning: Could not create index directory: {e}")

    # Load mode
    if args.load:
        if not DEFAULT_INDEX_PATH.exists():
            print(f"❌ Index not found: {DEFAULT_INDEX_PATH}")
            return
        adapter = load_chronos_index(str(DEFAULT_INDEX_PATH))

        if args.search:
            # We use simple search here as reconstructing ChronosIndex fully is complex without doc store
            results = search_loaded_index(adapter, args.search, top_k=5)
            print(f"\n=== Search: {args.search} ===")
            for r in results:
                print(f"Score: {r.score:.3f} | {r.metadata.get('title', 'N/A')}")
                print(f"  Chunk: {r.metadata.get('chunk_idx', '0')}")
                print(f"  Timestamp: {r.metadata.get('timestamp', 'N/A')}")
                print(f"  Snippet: {r.metadata.get('content', '')[:100].replace(chr(10), ' ')}...")
                print()
        return

    # Ingest mode
    docs = []

    if args.file:
        files = [Path(args.file)]
    else:
        files = get_conversation_files()

    print(f"📝 Found {len(files)} conversation logs")

    for f in files:
        print(f"Parsing: {f.name}")
        chunks = parse_conversation_chunks(f)
        docs.extend(chunks)
        print(f"  → {len(chunks)} chunks")

    print(f"📊 Total: {len(docs)} documents")

    if not docs:
        print("No documents to ingest")
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
