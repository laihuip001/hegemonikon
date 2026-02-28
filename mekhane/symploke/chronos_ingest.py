#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/ A0->Existence
"""
Chronos Ingest - Conversation History を Chronos インデックスに自動投入

PURPOSE: /boot 時のセッション記憶復元に向けた会話ログ(Chronos)インジェスト機能を提供するモジュール。
"""

import os
from pathlib import Path

from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
from mekhane.symploke.indices.chronos import ChronosIndex
from mekhane.symploke.indices import Document

CHRONOS_INDEX_PATH = Path(
    os.environ.get(
        "HGK_CHRONOS_INDEX",
        str(
            Path.home() / "oikos" / "mneme" / ".hegemonikon" / "indices" / "chronos.pkl"
        ),
    )
)


# PURPOSE: Ingest conversation documents to Chronos index using real embeddings
def ingest_to_chronos(docs: list[Document], save_path: str = None) -> int:
    """Ingest conversation documents to Chronos index using real embeddings."""
    if not docs:
        return 0

    adapter = EmbeddingAdapter()

    # Auto-detect embedding dimension
    sample_vec = adapter.encode(["test"])
    dim = (
        sample_vec.shape[1]
        if hasattr(sample_vec, "shape") and len(sample_vec.shape) == 2
        else len(sample_vec[0])
    )

    index = ChronosIndex(adapter, "chronos", dimension=dim)
    index.initialize()

    count = index.ingest(docs)
    print(f"Ingested {count} documents to Chronos (real embeddings)")

    if save_path:
        path_obj = Path(save_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        adapter.save(save_path)
        print(f"💾 Saved Chronos index to: {save_path}")

    return count


# PURPOSE: Load a previously saved Chronos index
def load_chronos_index(load_path: str) -> EmbeddingAdapter:
    """Load a previously saved Chronos index."""
    adapter = EmbeddingAdapter()
    adapter.load(load_path)
    return adapter
