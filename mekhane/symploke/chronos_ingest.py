#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/
"""
Chronos Ingest - 会話履歴（Chronos）インデックス生成機能

このモジュールは会話履歴をChronosベクトルインデックスとして
取り込むための機能を提供する。
"""

import sys
import os
import re
from typing import List
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document
from mekhane.symploke.indices.chronos import ChronosIndex

DEFAULT_INDEX_PATH = Path(
    os.environ.get(
        "HGK_CHRONOS_INDEX",
        str(Path(__file__).parent.parent.parent.parent / "mneme" / ".hegemonikon" / "indices" / "chronos.pkl"),
    )
)

HANDOFF_DIR = Path(
    os.environ.get(
        "HGK_SESSIONS_DIR",
        str(Path(__file__).parent.parent.parent.parent / "mneme" / ".hegemonikon" / "sessions"),
    )
)

# PURPOSE: 履歴ファイルのパース (Kairosと同様の会話ログ処理)
def parse_conversation_chunks(
    file_path: Path, chunk_size: int = 1500
) -> list[Document]:
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

    # Create session_id for chronos
    session_id = f"{date_str}-{conv_num}"

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
                        "session_id": session_id,
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
                    "session_id": session_id,
                },
            )
        )

    # Fallback to single chunk if no chunks were created
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
                    "session_id": session_id,
                },
            )
        )

    return chunks

# PURPOSE: Get all conversation log files sorted by date (newest first)
def get_conversation_files() -> list[Path]:
    """Get all conversation log files sorted by date (newest first)."""
    if not HANDOFF_DIR.exists():
        return []
    files = list(HANDOFF_DIR.glob("*_conv_*.md"))
    return sorted(files, reverse=True)


# PURPOSE: Chronosインデックスへのインジェスト
def ingest_to_chronos(docs: List[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index using real embeddings."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
    # Auto-detect embedding dimension from the model
    sample_vec = adapter.encode(["test"])
    dim = sample_vec.shape[1] if sample_vec.ndim == 2 else len(sample_vec[0])

    # ChronosIndex uses 'chronos' as name
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
    return adapter
