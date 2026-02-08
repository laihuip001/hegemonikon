#!/usr/bin/env python3
"""Gnōsis Boot Integration — /boot Phase 3 expansion.

Boot 時に知識ベースから未解決タスクと保留事項を自動照会し、
セッション開始時の文脈を構築する。

Usage:
    python scripts/boot_gnosis.py [--queries N]
"""
import sys
import time
from pathlib import Path

# Hegemonikon root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Fixed queries for boot context
BOOT_QUERIES = [
    "最近のセッションで未解決の問題や保留中のタスク",
    "最近の設計決定とアーキテクチャの変更",
    "最近の失敗と学んだ教訓",
]

# Lighter query set for fast boot
FAST_QUERIES = [
    "未解決の問題と保留タスク",
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gnōsis Boot Integration")
    parser.add_argument(
        "--queries", type=int, default=len(BOOT_QUERIES),
        help="Number of queries to run (1=fast, 3=standard)"
    )
    parser.add_argument(
        "--top-k", type=int, default=3,
        help="Number of results per query"
    )
    args = parser.parse_args()

    queries = BOOT_QUERIES[:args.queries]

    print("=" * 60)
    print("🧠 Gnōsis Boot — Knowledge Recall")
    print("=" * 60)

    from mekhane.anamnesis.gnosis_chat import GnosisChat

    t0 = time.time()
    chat = GnosisChat(
        search_papers=False,  # Boot needs sessions/handoffs, not papers
        search_knowledge=True,
        top_k=args.top_k,
        use_reranker=True,
        steering_profile="hegemonikon",
    )

    for i, q in enumerate(queries, 1):
        print(f"\n--- [{i}/{len(queries)}] {q}")
        result = chat.retrieve_only(q)

        conf = result.get("confidence", "?")
        icon = {"high": "🟢", "medium": "🟡", "low": "🟠", "none": "🔴"}.get(conf, "❓")
        print(f"  {icon} Confidence: {conf} ({result['context_docs']} docs)")

        if result.get("sources"):
            for j, s in enumerate(result["sources"][:3], 1):
                title = s.get("title", "?")[:50]
                dist = s.get("distance", "?")
                print(f"  [{j}] d={dist:.3f} {title}")

        if result.get("context"):
            # Show context snippet for boot summary
            ctx = result["context"][:400]
            if len(result["context"]) > 400:
                ctx += "..."
            print(f"  📚 {ctx}")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"✅ Boot knowledge recall complete ({elapsed:.1f}s)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
