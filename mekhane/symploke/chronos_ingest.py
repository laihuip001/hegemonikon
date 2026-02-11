#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→chronos_ingest が担う
"""
Chronos Ingest - Conversation Logs (Chat History) を Chronos インデックスに自動投入

Usage:
    python chronos_ingest.py                    # 全ログを投入
    python chronos_ingest.py --dry-run          # パースのみ
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document
from mekhane.symploke.indices.chronos import ChronosIndex
from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

# Default directories
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_HOME = Path.home()

# Priority: env override > mneme sessions > local sessions
CHRONOS_LOGS_DIR = os.environ.get("HGK_CHRONOS_LOGS_DIR")
if not CHRONOS_LOGS_DIR:
    # Try multiple locations
    candidates = [
        _HOME / "oikos" / "mneme" / ".hegemonikon" / "sessions",
        _PROJECT_ROOT / ".hegemonikon" / "sessions",
    ]
    for d in candidates:
        if d.exists():
            CHRONOS_LOGS_DIR = d
            break

    if not CHRONOS_LOGS_DIR:
        # Fallback to local default (even if not exists yet)
        CHRONOS_LOGS_DIR = _PROJECT_ROOT / ".hegemonikon" / "sessions"

CHRONOS_LOGS_DIR = Path(CHRONOS_LOGS_DIR)

DEFAULT_INDEX_PATH = Path(
    os.environ.get(
        "HGK_CHRONOS_INDEX",
        str(_PROJECT_ROOT / ".hegemonikon" / "indices" / "chronos.pkl"),
    )
)


# PURPOSE: Parse a Chronos logs directory into Documents
def parse_chronos_logs(log_dir: Path) -> list[Document]:
    """Parse a Chronos logs directory into Documents."""
    docs = []
    if not log_dir.exists():
        print(f"Warning: Logs directory not found: {log_dir}")
        return docs

    for log_file in log_dir.glob("*.md"):
        try:
            content = log_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
            continue

        # Parse metadata from header
        chat_id = "unknown"
        export_time = None
        title = "Untitled Chat"

        # Extract title (first line usually starts with #)
        first_line = content.split('\n', 1)[0]
        if first_line.startswith('# '):
            title = first_line[2:].strip()

        id_match = re.search(r"- \*\*ID\*\*: `(.*?)`", content)
        if id_match:
            chat_id = id_match.group(1)

        time_match = re.search(r"- \*\*エクスポート日時\*\*: (.*)", content)
        if time_match:
            try:
                export_time = datetime.fromisoformat(time_match.group(1).strip())
            except ValueError:
                pass

        # Split into messages
        # Pattern matches: ## 👤 User OR ## 🤖 Claude
        # Capture group keeps the separator in the result list
        parts = re.split(r"(## .*)", content)

        # parts structure: [header, role_marker1, content1, role_marker2, content2, ...]

        turn_id = 0
        current_role = None

        # Skip header (parts[0])
        for i in range(1, len(parts), 2):
            if i+1 >= len(parts):
                break

            role_marker = parts[i]
            msg_content = parts[i+1].strip()

            if not msg_content:
                continue

            role = "user" if "User" in role_marker else "assistant"

            doc_id = f"{chat_id}-{turn_id}"

            # Metadata construction
            metadata = {
                "type": "conversation_history",
                "chat_id": chat_id,
                "title": title,
                "turn_id": turn_id,
                "role": role,
                "timestamp": export_time.isoformat() if export_time else None,
                "file_path": str(log_file)
            }

            doc = Document(
                id=doc_id,
                content=msg_content,
                metadata=metadata
            )
            docs.append(doc)
            turn_id += 1

    return docs


# PURPOSE: Ingest documents to Chronos index using real embeddings (returns count)
def ingest_to_chronos(docs: list[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index using real embeddings (returns count).

    Args:
        docs: Documents to ingest
        save_path: If provided, save the index to this path after ingestion
    """
    adapter = EmbeddingAdapter()

    # Auto-detect embedding dimension
    try:
        sample_vec = adapter.encode(["test"])
        dim = sample_vec.shape[1] if sample_vec.ndim == 2 else len(sample_vec[0])
    except Exception as e:
        print(f"Error initializing embedding model: {e}")
        return 0

    # Define embed_fn to bridge adapter.encode (batch) and ChronosIndex expectations (single)
    def embed_fn(text):
        vecs = adapter.encode([text])
        return vecs[0]

    index = ChronosIndex(adapter, "chronos", dimension=dim, embed_fn=embed_fn)
    index.initialize()

    count = index.ingest(docs)
    print(f"Ingested {count} documents to Chronos (real embeddings)")

    if save_path:
        # Create parent directory if needed
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        adapter.save(save_path)
        print(f"💾 Saved index to: {save_path}")

    return count


# PURPOSE: Load a previously saved Chronos index
def load_chronos_index(load_path: str):
    """Load a previously saved Chronos index."""
    if not os.path.exists(load_path):
        raise FileNotFoundError(f"Index file not found: {load_path}")

    adapter = EmbeddingAdapter()
    adapter.load(load_path)
    print(f"📂 Loaded index from: {load_path} ({adapter.count()} vectors)")
    return adapter


# PURPOSE: Search using a loaded adapter directly
def search_loaded_index(adapter, query: str, top_k: int = 5):
    """Search using a loaded adapter directly."""
    # Encode query
    query_vec = adapter.encode([query])[0]
    results = adapter.search(query_vec, k=top_k)
    return results


# PURPOSE: main の処理
def main():
    parser = argparse.ArgumentParser(description="Ingest Chat Logs to Chronos index")
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

    args = parser.parse_args()

    # Load mode
    if args.load:
        if not DEFAULT_INDEX_PATH.exists():
            print(f"❌ Index not found: {DEFAULT_INDEX_PATH}")
            return

        try:
            adapter = load_chronos_index(str(DEFAULT_INDEX_PATH))

            if args.search:
                results = search_loaded_index(adapter, args.search, top_k=5)
                print(f"\n=== Search: {args.search} ===")
                for r in results:
                    print(f"Score: {r.score:.3f} | {r.metadata.get('doc_id', 'N/A')}")
                    print(f"  Role: {r.metadata.get('role', 'unknown')}")
                    # Content is not stored in metadata by default in Document, need to rely on metadata if we want it back
                    # But parse_chronos_logs puts content in Document.content, not metadata['content']
                    # EmbeddingAdapter saves metadata but not content.
                    # Ideally we should add content to metadata for retrieval.
                    print(f"  Chat ID: {r.metadata.get('chat_id', 'N/A')}")
                    print()
        except Exception as e:
            print(f"Error loading index: {e}")
        return

    # Ingest mode
    print(f"Scanning logs from: {CHRONOS_LOGS_DIR}")
    docs = parse_chronos_logs(CHRONOS_LOGS_DIR)

    # Enrich metadata with content snippet for search display
    for doc in docs:
        doc.metadata["content_snippet"] = doc.content[:100]

    print(f"Found {len(docs)} documents (messages)")

    if args.dry_run:
        print("\n[Dry run] Would ingest documents")
        for doc in docs[:3]:
            print(f"  ID: {doc.id}")
            print(f"  Role: {doc.metadata.get('role')}")
            print(f"  Content: {doc.content[:50]}...")
        return

    # Save by default unless --no-save
    save_path = None if args.no_save else str(DEFAULT_INDEX_PATH)
    ingest_to_chronos(docs, save_path=save_path)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
