#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- scripts/
# PURPOSE: Gnōsis ベクトルインデックスのブート時自動構築
"""Gnōsis Boot Integration — /boot Phase 3 expansion.

Boot 時に知識ベースから未解決タスクと保留事項を自動照会し、
セッション開始時の文脈を構築する。

Usage:
    python scripts/boot_gnosis.py [--queries N]

Resilience:
    HF_HUB_OFFLINE=1 でローカルキャッシュのみ使用。
    Reranker 失敗時は bi-encoder のみにフォールバック。
    クエリごとに 30 秒タイムアウト。
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

# ── Network Resilience ──────────────────────────────────────
# 全モデルはローカルキャッシュ済み。Boot 時にリモート確認を行わない。
# これが無いと AutoTokenizer.from_pretrained が HuggingFace Hub に
# HTTP 接続を試み、ネットワーク不安定時に ReadTimeout で失敗する。
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

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


# Per-query timeout (seconds)
QUERY_TIMEOUT = 30


def _create_chat(top_k: int = 3, use_reranker: bool = True):
    """GnosisChat を生成。Reranker 失敗時はフォールバック。"""
    from mekhane.anamnesis.gnosis_chat import GnosisChat

    try:
        chat = GnosisChat(
            search_papers=False,  # Boot needs sessions/handoffs, not papers
            search_knowledge=True,
            top_k=top_k,
            use_reranker=use_reranker,
            steering_profile="hegemonikon",
        )
        # Reranker のプリロードを試行 (ローカルキャッシュのみ)
        if use_reranker and chat._reranker:
            chat._reranker._load()
        return chat
    except Exception as e:
        if use_reranker:
            print(f"  ⚠️ Reranker load failed ({e}), falling back to bi-encoder only",
                  flush=True)
            return _create_chat(top_k=top_k, use_reranker=False)
        raise


def _run_query(chat, query: str) -> dict:
    """1 クエリを タイムアウト付きで実行。"""
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(chat.retrieve_only, query)
        return future.result(timeout=QUERY_TIMEOUT)


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
    print(f"   (HF_HUB_OFFLINE={os.environ.get('HF_HUB_OFFLINE', 'unset')})")
    print("=" * 60)

    t0 = time.time()
    chat = _create_chat(top_k=args.top_k)

    success = 0
    for i, q in enumerate(queries, 1):
        print(f"\n--- [{i}/{len(queries)}] {q}")
        try:
            result = _run_query(chat, q)
        except FutureTimeout:
            print(f"  ⏰ Timeout ({QUERY_TIMEOUT}s) — skipping")
            continue
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

        success += 1
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
    status = "✅" if success == len(queries) else f"⚠️ ({success}/{len(queries)} queries succeeded)"
    print(f"{status} Boot knowledge recall complete ({elapsed:.1f}s)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
