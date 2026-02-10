#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ O4→FEP 知識基盤の体系的構築
# PURPOSE: FEP 関連論文のバッチ収集 + Gnōsis 投入
"""
FEP Literature Collector
=========================

Semantic Scholar API + Perplexity API で FEP/Active Inference 関連論文を
体系的に収集し、Gnōsis にインデックスする。

Usage:
    # ドライラン（収集のみ、Gnōsis 投入なし）
    python scripts/collect_fep_papers.py --dry-run

    # 本番実行（Gnōsis にも投入）
    python scripts/collect_fep_papers.py

    # 特定カテゴリのみ
    python scripts/collect_fep_papers.py --category core

    # 収集済みデータの統計
    python scripts/collect_fep_papers.py --stats
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mekhane.pks.semantic_scholar import SemanticScholarClient, Paper

# ---------------------------------------------------------------------------
# Query definitions — FEP 分野の体系的なクエリリスト
# ---------------------------------------------------------------------------

# 目標: 200-300 のユニーク論文を収集
# 戦略: 15カテゴリ × 各 20-30 件 = 300-450 件（重複除去後 200-300）

FEP_QUERIES: dict[str, list[dict]] = {
    # === A. FEP Core Theory ===
    "core": [
        {"query": "free energy principle brain", "limit": 30},
        {"query": "free energy principle unified theory", "limit": 20},
        {"query": "variational free energy minimization", "limit": 20},
    ],
    # === B. Active Inference ===
    "active_inference": [
        {"query": "active inference framework", "limit": 30},
        {"query": "active inference decision making", "limit": 20},
        {"query": "active inference planning as inference", "limit": 20},
    ],
    # === C. Expected Free Energy ===
    "efe": [
        {"query": "expected free energy action selection", "limit": 20},
        {"query": "epistemic pragmatic value active inference", "limit": 20},
        {"query": "information gain exploration exploitation", "limit": 20},
    ],
    # === D. Precision & Attention ===
    "precision": [
        {"query": "precision weighting predictive processing", "limit": 20},
        {"query": "precision estimation attention free energy", "limit": 20},
        {"query": "aberrant precision psychopathology", "limit": 15},
    ],
    # === E. Markov Blankets ===
    "markov_blanket": [
        {"query": "Markov blanket free energy principle", "limit": 20},
        {"query": "Markov blanket boundaries cognition", "limit": 15},
    ],
    # === F. Predictive Processing ===
    "predictive_processing": [
        {"query": "predictive coding cortical hierarchy", "limit": 20},
        {"query": "predictive processing perception action", "limit": 20},
    ],
    # === G. FEP + AI/LLM ===
    "fep_ai": [
        {"query": "active inference artificial intelligence agent", "limit": 25},
        {"query": "active inference reinforcement learning comparison", "limit": 20},
        {"query": "free energy principle large language model", "limit": 15},
        {"query": "active inference robot control", "limit": 15},
    ],
    # === H. Mathematical Foundations ===
    "mathematics": [
        {"query": "variational Bayes generative model", "limit": 20},
        {"query": "free energy variational inference neural", "limit": 20},
    ],
    # === I. Criticisms & Limitations ===
    "criticism": [
        {"query": "free energy principle criticism limitations", "limit": 15},
        {"query": "Markov blanket criticism suitability", "limit": 10},
        {"query": "predictive processing criticism dark room", "limit": 10},
    ],
    # === J. Consciousness & Self ===
    "consciousness": [
        {"query": "free energy principle consciousness self-model", "limit": 15},
        {"query": "active inference self-organization autonomy", "limit": 15},
    ],
    # === K. Emotion & Interoception ===
    "emotion": [
        {"query": "interoceptive inference emotion free energy", "limit": 15},
        {"query": "allostasis active inference homeostasis", "limit": 10},
    ],
    # === L. Friston Seminal Works ===
    "friston": [
        {"query": "Karl Friston free energy principle", "limit": 30},
    ],
    # === M. Latest Research (2024-2026) ===
    "latest": [
        {"query": "active inference 2024 2025", "limit": 25, "year": (2024, 2026)},
        {"query": "free energy principle 2025", "limit": 20, "year": (2025, 2026)},
    ],
    # === N. Computational Implementations ===
    "implementation": [
        {"query": "pymdp active inference implementation", "limit": 15},
        {"query": "active inference POMDP discrete", "limit": 15},
        {"query": "deep active inference neural network", "limit": 15},
    ],
    # === O. Scale-Free / Nested Systems ===
    "scale": [
        {"query": "free energy principle scale free nested", "limit": 15},
        {"query": "renormalization group free energy brain", "limit": 10},
    ],
}

# Output
OUTPUT_DIR = PROJECT_ROOT / "data" / "fep_papers"
COLLECTED_FILE = OUTPUT_DIR / "collected_papers.json"
STATS_FILE = OUTPUT_DIR / "collection_stats.json"


# ---------------------------------------------------------------------------
# Collection Logic
# ---------------------------------------------------------------------------

def collect_category(
    client: SemanticScholarClient,
    category: str,
    queries: list[dict],
    existing_ids: set[str],
) -> list[Paper]:
    """1カテゴリ分の論文を収集"""
    category_papers: list[Paper] = []

    for q in queries:
        query_text = q["query"]
        limit = q.get("limit", 20)
        year_range = q.get("year")

        print(f"\n  📚 Query: '{query_text}' (limit={limit})")
        papers = client.search(query_text, limit=limit, year_range=year_range)

        new_count = 0
        for p in papers:
            if p.paper_id not in existing_ids:
                category_papers.append(p)
                existing_ids.add(p.paper_id)
                new_count += 1

        print(f"     → {len(papers)} found, {new_count} new")

    return category_papers


def collect_all(
    categories: list[str] | None = None,
    dry_run: bool = True,
) -> dict:
    """全カテゴリの論文を収集"""
    client = SemanticScholarClient()

    # 既存データの読み込み
    existing_papers: list[dict] = []
    existing_ids: set[str] = set()
    if COLLECTED_FILE.exists():
        existing_papers = json.loads(COLLECTED_FILE.read_text())
        existing_ids = {p["paper_id"] for p in existing_papers}
        print(f"📂 既存データ: {len(existing_papers)} papers")

    # 対象カテゴリ
    target_categories = categories or list(FEP_QUERIES.keys())

    all_new_papers: list[Paper] = []
    category_stats: dict[str, int] = {}

    for cat in target_categories:
        if cat not in FEP_QUERIES:
            print(f"⚠️  Unknown category: {cat}")
            continue

        queries = FEP_QUERIES[cat]
        print(f"\n{'='*60}")
        print(f"📂 Category: {cat} ({len(queries)} queries)")
        print(f"{'='*60}")

        papers = collect_category(client, cat, queries, existing_ids)
        all_new_papers.extend(papers)
        category_stats[cat] = len(papers)

    # 統計
    total_with_abstract = sum(1 for p in all_new_papers if p.has_abstract)
    year_dist = Counter(p.year for p in all_new_papers if p.year)

    stats = {
        "timestamp": datetime.now().isoformat(),
        "new_papers": len(all_new_papers),
        "existing_papers": len(existing_papers),
        "total_papers": len(existing_papers) + len(all_new_papers),
        "with_abstract": total_with_abstract,
        "without_abstract": len(all_new_papers) - total_with_abstract,
        "category_stats": category_stats,
        "year_distribution": dict(sorted(year_dist.items())),
        "api_requests": client._total_requests,
        "authenticated": client.authenticated,
        "dry_run": dry_run,
    }

    print(f"\n{'='*60}")
    print(f"📊 Collection Summary")
    print(f"{'='*60}")
    print(f"  新規: {stats['new_papers']} papers")
    print(f"  既存: {stats['existing_papers']} papers")
    print(f"  合計: {stats['total_papers']} papers")
    print(f"  Abstract あり: {stats['with_abstract']}")
    print(f"  Abstract なし: {stats['without_abstract']}")
    print(f"  API requests: {stats['api_requests']}")
    print(f"\n  Year distribution:")
    for year, count in sorted(year_dist.items()):
        bar = "█" * min(count, 50)
        print(f"    {year}: {count:>3} {bar}")

    # 保存
    if not dry_run:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # 新規論文を追加して保存
        all_paper_dicts = existing_papers + [p.to_dict() for p in all_new_papers]
        COLLECTED_FILE.write_text(
            json.dumps(all_paper_dicts, indent=2, ensure_ascii=False)
        )
        print(f"\n  💾 Saved to {COLLECTED_FILE}")

        # 統計を保存
        STATS_FILE.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
        print(f"  📊 Stats saved to {STATS_FILE}")
    else:
        print(f"\n  🔍 DRY RUN — データは保存されません")

    return stats


def show_stats():
    """収集済みデータの統計を表示"""
    if not COLLECTED_FILE.exists():
        print("❌ No collected data found")
        return

    papers = json.loads(COLLECTED_FILE.read_text())
    year_dist = Counter(p.get("year") for p in papers if p.get("year"))
    abstract_count = sum(1 for p in papers if p.get("abstract") and len(p["abstract"]) > 20)

    print(f"\n📊 FEP Literature Collection Stats")
    print(f"{'='*50}")
    print(f"  Total papers: {len(papers)}")
    print(f"  With abstract: {abstract_count}")
    print(f"  Without abstract: {len(papers) - abstract_count}")

    print(f"\n  Top cited:")
    by_cite = sorted(papers, key=lambda p: p.get("citation_count", 0), reverse=True)
    for p in by_cite[:10]:
        print(f"    {p.get('citation_count', 0):>5}c | [{p.get('year')}] {p.get('title', '')[:60]}")

    print(f"\n  Year distribution:")
    for year, count in sorted(year_dist.items()):
        bar = "█" * min(count, 50)
        print(f"    {year}: {count:>3} {bar}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="FEP Literature Collector")
    parser.add_argument("--dry-run", action="store_true", default=False, help="収集のみ、保存しない")
    parser.add_argument("--category", type=str, default=None, help="特定カテゴリのみ")
    parser.add_argument("--stats", action="store_true", help="統計表示")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    categories = [args.category] if args.category else None
    collect_all(categories=categories, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
