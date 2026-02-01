#!/usr/bin/env python3
# PROOF: [L2/インフラ] A0→知識管理が必要→seed_data が担う
"""
MVP Seed Data for Mneme Server

最小限のテストデータを各インデックスに投入する。
1インデックスあたり2-3件のサンプルデータ。
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import (
    Document,
    GnosisIndex,
    ChronosIndex,
    SophiaIndex,
    KairosIndex,
)
from mekhane.symploke.adapters.mock_adapter import MockAdapter
from mekhane.symploke.search.engine import SearchEngine

# ============ Seed Data ============

GNOSIS_SEED = [
    Document(
        id="fep-friston-2010",
        content="Free Energy Principle: A unified brain theory proposing that biological systems minimize variational free energy. Active inference and predictive processing.",
        metadata={
            "title": "The Free-Energy Principle",
            "author": "Karl Friston",
            "year": 2010,
        },
    ),
    Document(
        id="transformer-attention-2017",
        content="Attention Is All You Need: Transformer architecture with self-attention mechanism. Foundation for modern LLMs like GPT and BERT.",
        metadata={
            "title": "Attention Is All You Need",
            "author": "Vaswani et al.",
            "year": 2017,
        },
    ),
]

CHRONOS_SEED = [
    Document(
        id="chat-2026-01-27-boot",
        content="Session started with /boot command. Loaded Hegemonikón profile, patterns.yaml (3 patterns), values.json (6 values). Perplexity Inbox has 48 files.",
        metadata={"timestamp": "2026-01-27T16:23:57", "session": "boot"},
    ),
    Document(
        id="chat-2026-01-27-noe",
        content="Executed /noe /why /u workflow for .agent backup strategy. Conclusion: oikos as canonical source, symlink or rsync approach. Creator plans Windows Linux migration on 1/30.",
        metadata={"timestamp": "2026-01-27T16:33:42", "session": "planning"},
    ),
]

SOPHIA_SEED = [
    Document(
        id="ki-hegemonikon-system",
        content="Hegemonikón Integrated System: FEP-based cognitive framework with O/S/T-series theorems. Stoic philosophy + active inference. 48 theorems total.",
        metadata={"type": "knowledge_item", "domain": "architecture"},
    ),
    Document(
        id="ki-skill-optimization",
        content="SKILL.md Structure Optimization v2.1: Three-layer progressive disclosure, primacy effect, JSON output for LLM efficiency.",
        metadata={"type": "knowledge_item", "domain": "skill_design"},
    ),
]

KAIROS_SEED = [
    Document(
        id="handoff-2026-01-27-1613",
        content="Session Handoff: O/S/T-series SKILL.md v2.1 optimization completed. Git push done. Long-term memory initialized. Next: H/P-series update, Perplexity Inbox processing.",
        metadata={"timestamp": "2026-01-27T16:13:00", "type": "handoff"},
    ),
]


def seed_all():
    """全インデックスにシードデータを投入"""
    engine = SearchEngine()

    seed_data = [
        (GnosisIndex, "gnosis", GNOSIS_SEED),
        (ChronosIndex, "chronos", CHRONOS_SEED),
        (SophiaIndex, "sophia", SOPHIA_SEED),
        (KairosIndex, "kairos", KAIROS_SEED),
    ]

    for IndexClass, name, docs in seed_data:
        adapter = MockAdapter()
        index = IndexClass(adapter, name, dimension=768)
        index.initialize()

        # Ingest documents
        count = index.ingest(docs)
        print(f"[{name}] Seeded {count} documents")

        engine.register(index)

    return engine


def test_search(engine: SearchEngine):
    """シードデータの検索テスト"""
    queries = [
        "free energy principle",
        "session handoff",
        "skill optimization",
    ]

    print("\n=== Search Tests ===")
    for q in queries:
        results = engine.search(q, k=3)
        print(f"\nQuery: '{q}'")
        for r in results:
            print(f"  [{r.source.value}] {r.doc_id}: {r.score:.3f}")


if __name__ == "__main__":
    print("=== MVP Seed Data ===\n")
    engine = seed_all()

    print(f"\nStats: {engine.stats()}")
    print(f"Sources: {engine.registered_sources}")

    test_search(engine)
    print("\n✅ Seeding complete!")
