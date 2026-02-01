#!/usr/bin/env python3
# PROOF: [L2/インフラ] A0→知識管理が必要→kairos_ingest が担う
"""
Kairos Ingest - Handoff を Kairos インデックスに自動投入

Usage:
    python kairos_ingest.py                    # 最新1件を投入
    python kairos_ingest.py --all              # 全件を投入
    python kairos_ingest.py --file <path>      # 指定ファイルを投入
    python kairos_ingest.py --load --search "query"  # 検索
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, KairosIndex


HANDOFF_DIR = Path("/home/laihuip001/oikos/mneme/.hegemonikon/sessions")
DEFAULT_INDEX_PATH = Path("/home/laihuip001/oikos/mneme/.hegemonikon/indices/kairos.pkl")


def parse_handoff(file_path: Path) -> Document:
    """Parse a handoff markdown file into a Document."""
    content = file_path.read_text(encoding="utf-8")
    
    # Extract metadata from filename: handoff_YYYY-MM-DD_HHMM.md
    match = re.match(r"handoff_(\d{4}-\d{2}-\d{2})_(\d{4})\.md", file_path.name)
    if match:
        date_str, time_str = match.groups()
        timestamp = f"{date_str}T{time_str[:2]}:{time_str[2:]}:00"
    else:
        timestamp = datetime.now().isoformat()
    
    # Extract primary task from content (look for **主題**: or **セッション**:)
    primary_task = "Unknown"
    task_match = re.search(r"\*\*主題\*\*:\s*(.+?)(?:\n|$)", content)
    if task_match:
        primary_task = task_match.group(1).strip()
    
    return Document(
        id=f"handoff-{file_path.stem}",
        content=content[:2000],  # Truncate for embedding
        metadata={
            "timestamp": timestamp,
            "type": "handoff",
            "primary_task": primary_task,
            "file_path": str(file_path),
        }
    )


def get_handoff_files() -> list[Path]:
    """Get all handoff files sorted by date (newest first)."""
    files = list(HANDOFF_DIR.glob("handoff_*.md"))
    return sorted(files, reverse=True)


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
        }
    )


def parse_conversation_chunks(file_path: Path, chunk_size: int = 1500) -> list[Document]:
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
            chunks.append(Document(
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
                }
            ))
            chunk_idx += 1
            current_chunk = f"# {title}\n\n"
        current_chunk += msg + "\n\n"
    
    # Last chunk
    if len(current_chunk) > 100:
        chunks.append(Document(
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
            }
        ))
    
    return chunks if chunks else [parse_conversation(file_path)]  # Fallback


def get_conversation_files() -> list[Path]:
    """Get all conversation log files sorted by date (newest first)."""
    files = list(HANDOFF_DIR.glob("*_conv_*.md"))
    return sorted(files, reverse=True)




def ingest_to_kairos(docs: list[Document], save_path: str = None) -> int:
    """Ingest documents to Kairos index using real embeddings."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
    
    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    index = KairosIndex(adapter, "kairos", dimension=384)  # MiniLM = 384 dims
    index.initialize()
    
    count = index.ingest(docs)
    print(f"Ingested {count} documents to Kairos (real embeddings)")
    
    if save_path:
        adapter.save(save_path)
        print(f"💾 Saved index to: {save_path}")
    
    return count


def load_kairos_index(load_path: str):
    """Load a previously saved Kairos index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
    
    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    adapter.load(load_path)
    print(f"📂 Loaded index from: {load_path} ({adapter.count()} vectors)")
    return adapter


def search_loaded_index(adapter, query: str, top_k: int = 5):
    """Search using a loaded adapter directly."""
    query_vec = adapter.encode([query])[0]
    results = adapter.search(query_vec, k=top_k)
    return results


def main():
    parser = argparse.ArgumentParser(description="Ingest handoffs and conversations to Kairos index")
    parser.add_argument("--all", action="store_true", help="Ingest all handoff files")
    parser.add_argument("--conversations", action="store_true", help="Ingest conversation logs")
    parser.add_argument("--unified", action="store_true", help="Ingest both handoffs and conversations into one index")
    parser.add_argument("--chunked", action="store_true", help="Use chunked mode for better search coverage")
    parser.add_argument("--file", type=str, help="Ingest specific file")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, don't ingest")
    parser.add_argument("--no-save", action="store_true", help="Don't save index after ingestion")
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
        adapter = load_kairos_index(str(DEFAULT_INDEX_PATH))
        
        if args.search:
            results = search_loaded_index(adapter, args.search, top_k=5)
            print(f"\n=== Search: {args.search} ===")
            for r in results:
                doc_type = r.metadata.get('type', 'unknown')
                if doc_type in ('conversation', 'conversation_chunk'):
                    label = r.metadata.get('title', 'N/A')
                    if doc_type == 'conversation_chunk':
                        label += f" [chunk {r.metadata.get('chunk_idx', '?')}]"
                else:
                    label = r.metadata.get('primary_task', 'N/A')
                print(f"Score: {r.score:.3f} | [{doc_type}] {label}")
                print(f"  ID: {r.metadata.get('doc_id', 'N/A')}")
                print(f"  Timestamp: {r.metadata.get('timestamp', 'N/A')}")
                print()
        return
    
    # Ingest mode
    docs = []
    
    # Collect handoff files
    if args.file:
        files = [Path(args.file)]
        for f in files:
            print(f"Parsing: {f.name}")
            doc = parse_handoff(f)
            docs.append(doc)
            print(f"  → {doc.id}: {doc.metadata.get('primary_task', 'N/A')}")
    elif args.conversations:
        # Conversation logs
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
                print(f"  → {doc.id}: {doc.metadata.get('title', 'N/A')} ({doc.metadata.get('msg_count', 0)} msgs)")
    elif args.all:
        # Handoffs only (use --conversations for conv logs)
        files = get_handoff_files()
        for f in files:
            print(f"Parsing: {f.name}")
            doc = parse_handoff(f)
            docs.append(doc)
            print(f"  → {doc.id}: {doc.metadata.get('primary_task', 'N/A')}")
    elif hasattr(args, 'unified') and args.unified:
        # 統合モード: Handoff + 会話ログを一つのインデックスに
        print("🔗 Unified mode: Handoffs + Conversations")
        
        # Handoffs
        handoff_files = get_handoff_files()
        print(f"📋 Found {len(handoff_files)} handoffs")
        for f in handoff_files:
            doc = parse_handoff(f)
            docs.append(doc)
        
        # Conversations (chunked)
        conv_files = get_conversation_files()
        print(f"📝 Found {len(conv_files)} conversations")
        if args.chunked:
            for f in conv_files:
                chunks = parse_conversation_chunks(f)
                docs.extend(chunks)
        else:
            for f in conv_files:
                doc = parse_conversation(f)
                docs.append(doc)
        
        print(f"📊 Total: {len(docs)} documents")
    else:
        # Default: latest handoff only
        files = get_handoff_files()[:1]
        for f in files:
            print(f"Parsing: {f.name}")
            doc = parse_handoff(f)
            docs.append(doc)
            print(f"  → {doc.id}: {doc.metadata.get('primary_task', 'N/A')}")
    
    if not docs:
        print("No files found")
        return
    
    if args.dry_run:
        print(f"\n[Dry run] Would ingest {len(docs)} documents")
        return
    
    # Save by default unless --no-save
    save_path = None if args.no_save else str(DEFAULT_INDEX_PATH)
    ingest_to_kairos(docs, save_path=save_path)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

