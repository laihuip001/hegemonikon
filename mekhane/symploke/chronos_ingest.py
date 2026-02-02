#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→索引管理が必要→chronos_ingest が担う
"""
Chronos Ingest - 会話履歴 (Conversation History) を Chronos インデックスに自動投入

Usage:
    python chronos_ingest.py                    # 全履歴を投入
    python chronos_ingest.py --file <path>      # 指定ファイルを投入
    python chronos_ingest.py --load --search "query"  # 検索
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, ChronosIndex

SESSION_DIR = Path(
    os.environ.get(
        "MNEME_SESSION_DIR", str(Path.home() / "oikos/mneme/.hegemonikon/sessions")
    )
)
DEFAULT_INDEX_PATH = Path(
    os.environ.get(
        "MNEME_CHRONOS_INDEX",
        str(Path.home() / "oikos/mneme/.hegemonikon/indices/chronos.pkl"),
    )
)


def get_conversation_files() -> List[Path]:
    """Get all conversation log files sorted by date (newest first)."""
    if not SESSION_DIR.exists():
        return []
    # export_chats.py outputs files like YYYY-MM-DD_conv_N_Title.md or just Title.md
    # We look for all .md files that look like sessions
    files = list(SESSION_DIR.glob("*.md"))
    # Filter out handoff files if they are in the same directory (export_chats puts them there?)
    # export_chats output: sessions/
    # kairos_ingest looks for handoff_*.md in the same dir?
    # Let's filter out files starting with "handoff_" just in case.
    files = [f for f in files if not f.name.startswith("handoff_")]
    return sorted(files, reverse=True)


def parse_conversation_messages(file_path: Path) -> List[Document]:
    """Parse a conversation log markdown file into a list of message Documents."""
    content = file_path.read_text(encoding="utf-8")

    # Extract metadata from filename
    # Expected: YYYY-MM-DD_conv_N_Title.md or YYYY-MM-DD_ID_Title.md
    # export_chats.py: {date_prefix}_{id_prefix}_{safe_title}.md
    match = re.match(r"(\d{4}-\d{2}-\d{2})_([^_]+)_(.+)\.md", file_path.name)
    structured_filename = False
    if match:
        date_str, conv_id, title = match.groups()
        title = title.replace("_", " ")
        base_timestamp = datetime.strptime(date_str, "%Y-%m-%d")
        structured_filename = True
    else:
        # Fallback
        base_timestamp = datetime.now()
        conv_id = file_path.stem
        title = file_path.stem

    # Extract ID from content if available
    id_match = re.search(r"- \*\*ID\*\*: `([^`]+)`", content)
    if id_match:
        full_id = id_match.group(1)
        if not structured_filename or not conv_id or conv_id == "noname":
            conv_id = full_id

    # Split content by headers
    # Format:
    # # Title
    # ...
    # ---
    #
    # ## 👤 User (or ## User)
    # ...
    # ## 🤖 Claude (or ## Claude)
    # ...

    parts = re.split(r"## (?:👤|🤖)?\s*(User|Claude)", content)

    # parts[0] is header/preamble
    # parts[1] is role (User/Claude)
    # parts[2] is content
    # parts[3] is role...

    docs = []
    turn_id = 0

    # Estimate time per message (e.g. 1 minute increment)
    current_time = base_timestamp

    # Skip preamble (parts[0])
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break

        role_str = parts[i].strip() # "User" or "Claude"
        msg_content = parts[i+1].strip()

        if not msg_content:
            continue

        role = "user" if "User" in role_str else "assistant"

        # Increment time
        current_time += timedelta(minutes=1)
        turn_id += 1

        doc_id = f"msg-{conv_id}-{turn_id}"

        docs.append(Document(
            id=doc_id,
            content=msg_content,
            metadata={
                "timestamp": current_time.isoformat(),
                "session_id": conv_id,
                "turn_id": turn_id,
                "role": role,
                "title": title,
                "file_path": str(file_path),
                "content": msg_content  # IMPORTANT: Add content to metadata for persistence
            }
        ))

    return docs


def ingest_to_chronos(docs: List[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    # Dimension 384 for MiniLM
    index = ChronosIndex(adapter, "chronos", dimension=384)
    index.initialize()

    count = index.ingest(docs)
    print(f"Ingested {count} messages to Chronos")

    if save_path:
        adapter.save(save_path)
        print(f"💾 Saved index to: {save_path}")

    return count


def load_chronos_index(load_path: str) -> ChronosIndex:
    """Load a previously saved Chronos index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    adapter.load(load_path)

    index = ChronosIndex(adapter, "chronos", dimension=384)
    # Note: index._doc_store will be empty, so content retrieval relies on metadata

    print(f"📂 Loaded index from: {load_path} ({adapter.count()} vectors)")
    return index


def search_loaded_index(index: ChronosIndex, query: str, top_k: int = 5):
    """Search using a loaded ChronosIndex."""
    results = index.search(query, k=top_k)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Ingest conversation history to Chronos index"
    )
    parser.add_argument("--all", action="store_true", help="Ingest all conversation files")
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

        index = load_chronos_index(str(DEFAULT_INDEX_PATH))

        if args.search:
            results = index.search(args.search, k=5)
            print(f"\n=== Search: {args.search} ===")
            for r in results:
                # Retrieve content from metadata if doc_store is empty
                content = r.content
                if not content and 'content' in r.metadata:
                    content = r.metadata['content']

                print(f"Score: {r.score:.3f} | [{r.metadata.get('role', '?')}]")
                print(f"  {content[:100]}...")
                print(f"  Session: {r.metadata.get('title', 'N/A')}")
                print(f"  Time: {r.metadata.get('timestamp', 'N/A')}")
                print()
        return

    # Ingest mode
    docs = []

    if args.file:
        files = [Path(args.file)]
    else:
        files = get_conversation_files()

    print(f"Found {len(files)} conversation files")

    for f in files:
        if not f.exists():
            print(f"File not found: {f}")
            continue

        print(f"Parsing: {f.name}")
        file_docs = parse_conversation_messages(f)
        docs.extend(file_docs)
        print(f"  → {len(file_docs)} messages")

    if not docs:
        print("No messages found")
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
