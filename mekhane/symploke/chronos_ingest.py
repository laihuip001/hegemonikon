#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→chronos_ingest が担う
"""
Chronos Ingest - Conversation logs を Chronos インデックスに自動投入

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
_THIS_DIR = Path(__file__).parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from mekhane.symploke.indices import Document, ChronosIndex

# Configurable via env — defaults to mneme indices
CONVERSATION_DIR = Path(
    os.environ.get(
        "HGK_SESSIONS_DIR",
        str(_PROJECT_ROOT.parent / "mneme" / ".hegemonikon" / "sessions"),
    )
)

DEFAULT_INDEX_PATH = Path(
    os.environ.get(
        "HGK_CHRONOS_INDEX",
        str(_PROJECT_ROOT.parent / "mneme" / ".hegemonikon" / "indices" / "chronos.pkl"),
    )
)


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

    msg_count = len(re.findall(r"## 🤖 Claude", content))

    # Embedding text: Title + first 2000 chars
    # タイトルを重複して含めることで検索精度向上
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
) -> list[Document]:
    """Parse a conversation into multiple chunks for better search coverage.

    各ファイルを複数チャンクに分割し、より細かい粒度で検索可能にする。
    """
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
def get_conversation_files() -> list[Path]:
    """Get all conversation log files sorted by date (newest first)."""
    if not CONVERSATION_DIR.exists():
        return []
    files = list(CONVERSATION_DIR.glob("*_conv_*.md"))
    return sorted(files, reverse=True)


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
    parser.add_argument("--all", action="store_true", help="Ingest all conversation logs")
    parser.add_argument(
        "--chunked",
        action="store_true",
        help="Use chunked mode for better search coverage",
    )
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
                if doc_type in ("conversation", "conversation_chunk"):
                    label = r.metadata.get("title", "N/A")
                    if doc_type == "conversation_chunk":
                        label += f" [chunk {r.metadata.get('chunk_idx', '?')}]"
                else:
                    label = r.metadata.get("primary_task", "N/A")
                print(f"Score: {r.score:.3f} | [{doc_type}] {label}")
                print(f"  ID: {r.metadata.get('doc_id', 'N/A')}")
                print(f"  Timestamp: {r.metadata.get('timestamp', 'N/A')}")
                print()
        return

    # Ingest mode
    docs = []

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
                print(
                    f"  → {doc.id}: {doc.metadata.get('title', 'N/A')} ({doc.metadata.get('msg_count', 0)} msgs)"
                )
    elif args.all:
        files = get_conversation_files()
        print(f"📝 Found {len(files)} conversation logs")
        if args.chunked:
            print("🔀 Using chunked mode for better coverage")
            for f in files:
                chunks = parse_conversation_chunks(f)
                docs.extend(chunks)
                print(f"  → {f.name}: {len(chunks)} chunks")
        else:
            for f in files:
                print(f"Parsing: {f.name}")
                doc = parse_conversation(f)
                docs.append(doc)
                print(
                    f"  → {doc.id}: {doc.metadata.get('title', 'N/A')} ({doc.metadata.get('msg_count', 0)} msgs)"
                )
    else:
        # Default: latest conversation only
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
                print(
                    f"  → {doc.id}: {doc.metadata.get('title', 'N/A')} ({doc.metadata.get('msg_count', 0)} msgs)"
                )

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
