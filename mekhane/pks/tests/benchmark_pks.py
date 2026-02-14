#!/usr/bin/env python3
# PURPOSE: PKS 検索品質ベンチマーク — Precision@K, MRR, Coverage, Latency を自動計測
"""
PKS Search Quality Benchmark

4 インデックス (Gnōsis, Kairos, Sophia, Chronos) の横断検索品質を
15 テストクエリで定量評価する。

Usage:
    cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/pks/tests/benchmark_pks.py
"""

import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Suppress proxy/offline warnings
for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(key, None)
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# ── Constants ──
MNEME_ROOT = Path.home() / "oikos" / "mneme" / ".hegemonikon"
INDICES_DIR = MNEME_ROOT / "indices"
REPORT_PATH = Path(__file__).parent / "benchmark_report.md"
RESULTS_JSON = Path(__file__).parent / "benchmark_results.json"


# ── Test Query Set (15 queries, 5 categories × 3) ──
BENCHMARK_QUERIES = [
    # Category 1: Theoretical Core (FEP / Active Inference)
    {
        "id": "T1",
        "category": "theoretical_core",
        "query": "FEP variational free energy minimization",
        "expected_sources": ["gnosis"],
        "relevance_keywords": ["free energy", "FEP", "variational", "Friston", "inference"],
        "description": "FEP の基礎理論",
    },
    {
        "id": "T2",
        "category": "theoretical_core",
        "query": "active inference expected free energy planning",
        "expected_sources": ["gnosis"],
        "relevance_keywords": ["active inference", "expected free energy", "planning", "EFE"],
        "description": "能動的推論と計画",
    },
    {
        "id": "T3",
        "category": "theoretical_core",
        "query": "Markov blanket self organization biological systems",
        "expected_sources": ["gnosis"],
        "relevance_keywords": ["Markov blanket", "self-organization", "biological", "partition"],
        "description": "マルコフ毛布と自己組織化",
    },
    # Category 2: HGK Concepts
    {
        "id": "H1",
        "category": "hgk_concepts",
        "query": "CCL cognitive control language workflow",
        "expected_sources": ["kairos", "sophia", "chronos"],
        "relevance_keywords": ["CCL", "cognitive", "control", "workflow", "Hegemonikón"],
        "description": "CCL ワークフロー言語",
    },
    {
        "id": "H2",
        "category": "hgk_concepts",
        "query": "Noēsis Boulēsis Zētēsis ousia series theorem",
        "expected_sources": ["kairos", "sophia", "gnosis"],
        "relevance_keywords": ["Noēsis", "Boulēsis", "Zētēsis", "ousia", "theorem", "O-series"],
        "description": "O-series 定理群",
    },
    {
        "id": "H3",
        "category": "hgk_concepts",
        "query": "二層フィルター criterion cognitive novelty tensor product",
        "expected_sources": ["kairos", "sophia", "gnosis"],
        "relevance_keywords": ["二層", "criterion", "novelty", "tensor", "フィルター"],
        "description": "二層フィルター理論",
    },
    # Category 3: Implementation
    {
        "id": "I1",
        "category": "implementation",
        "query": "PKS proactive knowledge surface push embedding",
        "expected_sources": ["kairos", "chronos"],
        "relevance_keywords": ["PKS", "proactive", "knowledge", "push", "embedding"],
        "description": "PKS 実装",
    },
    {
        "id": "I2",
        "category": "implementation",
        "query": "Dendron PROOF existence proof verification",
        "expected_sources": ["kairos", "chronos", "sophia"],
        "relevance_keywords": ["Dendron", "PROOF", "existence", "proof", "verification"],
        "description": "Dendron 存在証明",
    },
    {
        "id": "I3",
        "category": "implementation",
        "query": "Hermēneus parser CCL AST dispatch runtime",
        "expected_sources": ["kairos", "chronos"],
        "relevance_keywords": ["Hermēneus", "parser", "CCL", "AST", "dispatch", "runtime"],
        "description": "Hermēneus パーサー",
    },
    # Category 4: Cross-Domain
    {
        "id": "X1",
        "category": "cross_domain",
        "query": "category theory adjunction cognitive framework",
        "expected_sources": ["gnosis", "sophia"],
        "relevance_keywords": ["category", "adjunction", "cognitive", "functor", "圏論"],
        "description": "圏論と認知の接続",
    },
    {
        "id": "X2",
        "category": "cross_domain",
        "query": "precision weighting attention interoception prediction error",
        "expected_sources": ["gnosis"],
        "relevance_keywords": ["precision", "attention", "interoception", "prediction", "error"],
        "description": "精度加重と注意",
    },
    {
        "id": "X3",
        "category": "cross_domain",
        "query": "Cortex API direct access bypass language server",
        "expected_sources": ["kairos", "chronos"],
        "relevance_keywords": ["Cortex", "API", "direct", "bypass", "language server"],
        "description": "Cortex API 直接アクセス",
    },
    # Category 5: Edge Cases
    {
        "id": "E1",
        "category": "edge_case",
        "query": "xylophone quantum teleportation recipe cooking",
        "expected_sources": [],
        "relevance_keywords": [],
        "description": "完全無関係クエリ (ノイズ検出)",
    },
    {
        "id": "E2",
        "category": "edge_case",
        "query": "日本語だけのクエリ 自由エネルギー原理 予測誤差最小化",
        "expected_sources": ["gnosis", "kairos"],
        "relevance_keywords": ["自由エネルギー", "予測誤差", "FEP"],
        "description": "日本語クエリの精度",
    },
    {
        "id": "E3",
        "category": "edge_case",
        "query": "boot handoff session bye workflow",
        "expected_sources": ["kairos", "chronos", "sophia"],
        "relevance_keywords": ["boot", "handoff", "session", "bye", "workflow"],
        "description": "運用系キーワード",
    },
]


@dataclass
class SearchResult:
    """A single search result."""
    source: str
    score: float
    title: str
    snippet: str


@dataclass
class QueryResult:
    """Results for a single benchmark query."""
    query_id: str
    query: str
    category: str
    description: str
    results: list[SearchResult] = field(default_factory=list)
    latency_seconds: float = 0.0
    precision_at_5: float = 0.0
    mrr: float = 0.0
    source_coverage: float = 0.0
    keyword_hits: int = 0
    total_keywords: int = 0


def run_search(query: str, k: int = 10) -> tuple[list[SearchResult], float]:
    """Execute PKS search and return results with latency."""
    t0 = time.time()
    all_results = []

    # 1. Gnōsis (LanceDB)
    try:
        from mekhane.anamnesis.index import GnosisIndex
        gi = GnosisIndex()
        results = gi.search(query, k=k)
        for r in results:
            title = r.get("title", r.get("primary_key", "?"))
            dist = float(r.get("_distance", 1.0))
            score = max(0.0, min(1.0, 1.0 - dist / 2.0))
            snippet = r.get("abstract", r.get("content", ""))[:200]
            all_results.append(SearchResult("gnosis", score, title, snippet))
    except Exception as e:
        print(f"  ⚠️ Gnōsis error: {e}", file=sys.stderr)

    # 2-4. pkl indices
    try:
        from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
        adapter = EmbeddingAdapter()
        query_vec = adapter.encode(query)

        for name in ["kairos", "sophia", "chronos"]:
            pkl = INDICES_DIR / f"{name}.pkl"
            if not pkl.exists():
                continue
            try:
                idx = EmbeddingAdapter()
                idx.load(str(pkl))
                hits = idx.search(query_vec, k=k)
                for hit in hits:
                    meta = hit.metadata if hasattr(hit, "metadata") else {}
                    title = meta.get("title", meta.get("doc_id", str(hit.id)))
                    hit_score = hit.score if hasattr(hit, "score") else 0
                    all_results.append(SearchResult(name, hit_score, title, ""))
            except Exception as e:
                print(f"  ⚠️ {name} error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️ Embedder error: {e}", file=sys.stderr)

    elapsed = time.time() - t0
    all_results.sort(key=lambda x: x.score, reverse=True)
    return all_results, elapsed


def evaluate_relevance(result: SearchResult, keywords: list[str]) -> bool:
    """Check if a result is relevant based on keyword matching."""
    if not keywords:
        return False
    text = (result.title + " " + result.snippet).lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    return hits >= max(1, len(keywords) // 3)


def compute_metrics(
    results: list[SearchResult],
    expected_sources: list[str],
    keywords: list[str],
    k: int = 5,
) -> tuple[float, float, float, int, int]:
    """Compute Precision@K, MRR, and Source Coverage."""
    top_k = results[:k]

    # Precision@K: fraction of relevant results in top-k
    relevant_count = sum(1 for r in top_k if evaluate_relevance(r, keywords))
    precision = relevant_count / k if k > 0 else 0.0

    # MRR: reciprocal rank of first relevant result
    mrr = 0.0
    for i, r in enumerate(results):
        if evaluate_relevance(r, keywords):
            mrr = 1.0 / (i + 1)
            break

    # Source Coverage: fraction of expected sources present in results
    if expected_sources:
        found_sources = set(r.source for r in top_k)
        coverage = len(found_sources & set(expected_sources)) / len(expected_sources)
    else:
        # Edge case: if no sources expected, coverage = 1.0 if results have low scores
        avg_score = sum(r.score for r in top_k) / len(top_k) if top_k else 0
        coverage = 1.0 if avg_score < 0.3 else 0.0

    # Keyword hit count
    all_text = " ".join((r.title + " " + r.snippet).lower() for r in top_k)
    keyword_hits = sum(1 for kw in keywords if kw.lower() in all_text) if keywords else 0

    return precision, mrr, coverage, keyword_hits, len(keywords)


def run_benchmark() -> list[QueryResult]:
    """Run the full benchmark suite."""
    print("=" * 60)
    print("PKS Search Quality Benchmark")
    print("=" * 60)
    print()

    query_results = []

    for i, q in enumerate(BENCHMARK_QUERIES, 1):
        print(f"[{i:2d}/{len(BENCHMARK_QUERIES)}] {q['id']}: {q['description']}...")

        results, latency = run_search(q["query"])
        precision, mrr, coverage, kw_hits, kw_total = compute_metrics(
            results, q["expected_sources"], q["relevance_keywords"]
        )

        qr = QueryResult(
            query_id=q["id"],
            query=q["query"],
            category=q["category"],
            description=q["description"],
            results=results[:10],
            latency_seconds=latency,
            precision_at_5=precision,
            mrr=mrr,
            source_coverage=coverage,
            keyword_hits=kw_hits,
            total_keywords=kw_total,
        )
        query_results.append(qr)

        # Progress indicator
        status = "✅" if precision >= 0.4 else "⚠️" if precision > 0 else "❌"
        print(f"       {status} P@5={precision:.2f} MRR={mrr:.2f} Cov={coverage:.2f} {latency:.1f}s")

    return query_results


def generate_report(results: list[QueryResult]) -> str:
    """Generate markdown benchmark report."""
    lines = []
    lines.append("# PKS 検索品質ベンチマークレポート")
    lines.append("")
    lines.append(f"実行日時: {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Overall metrics
    avg_p5 = sum(r.precision_at_5 for r in results) / len(results)
    avg_mrr = sum(r.mrr for r in results) / len(results)
    avg_cov = sum(r.source_coverage for r in results) / len(results)
    avg_lat = sum(r.latency_seconds for r in results) / len(results)
    total_lat = sum(r.latency_seconds for r in results)

    lines.append("## サマリー")
    lines.append("")
    lines.append("| 指標 | 値 | 目標 | 判定 |")
    lines.append("|:-----|---:|:----:|:----:|")
    lines.append(f"| **Precision@5** (平均) | {avg_p5:.3f} | ≥ 0.60 | {'✅' if avg_p5 >= 0.6 else '⚠️' if avg_p5 >= 0.4 else '❌'} |")
    lines.append(f"| **MRR** (平均) | {avg_mrr:.3f} | ≥ 0.50 | {'✅' if avg_mrr >= 0.5 else '⚠️' if avg_mrr >= 0.3 else '❌'} |")
    lines.append(f"| **Source Coverage** (平均) | {avg_cov:.3f} | ≥ 0.70 | {'✅' if avg_cov >= 0.7 else '⚠️' if avg_cov >= 0.5 else '❌'} |")
    lines.append(f"| **Latency** (平均) | {avg_lat:.1f}s | ≤ 15s | {'✅' if avg_lat <= 15 else '❌'} |")
    lines.append(f"| **Latency** (合計) | {total_lat:.1f}s | — | — |")
    lines.append("")

    # Per-query results
    lines.append("## クエリ別結果")
    lines.append("")
    lines.append("| ID | カテゴリ | 説明 | P@5 | MRR | Cov | Latency | KW |")
    lines.append("|:---|:---------|:-----|----:|----:|----:|--------:|---:|")
    for r in results:
        cat_short = r.category[:12]
        p5_icon = "✅" if r.precision_at_5 >= 0.6 else "⚠️" if r.precision_at_5 > 0 else "❌"
        kw_str = f"{r.keyword_hits}/{r.total_keywords}" if r.total_keywords > 0 else "—"
        lines.append(
            f"| {r.query_id} | {cat_short} | {r.description} | "
            f"{r.precision_at_5:.2f} {p5_icon} | {r.mrr:.2f} | {r.source_coverage:.2f} | "
            f"{r.latency_seconds:.1f}s | {kw_str} |"
        )
    lines.append("")

    # Category analysis
    lines.append("## カテゴリ別分析")
    lines.append("")
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = []
        categories[r.category].append(r)

    cat_names = {
        "theoretical_core": "理論コア",
        "hgk_concepts": "HGK 概念",
        "implementation": "実装",
        "cross_domain": "クロスドメイン",
        "edge_case": "エッジケース",
    }

    for cat, cat_results in categories.items():
        cat_p5 = sum(r.precision_at_5 for r in cat_results) / len(cat_results)
        cat_mrr = sum(r.mrr for r in cat_results) / len(cat_results)
        cat_cov = sum(r.source_coverage for r in cat_results) / len(cat_results)
        icon = "✅" if cat_p5 >= 0.6 else "⚠️" if cat_p5 >= 0.3 else "❌"
        lines.append(f"### {icon} {cat_names.get(cat, cat)} (P@5={cat_p5:.2f}, MRR={cat_mrr:.2f}, Cov={cat_cov:.2f})")
        lines.append("")
        for r in cat_results:
            lines.append(f"- **{r.query_id}** {r.description}: P@5={r.precision_at_5:.2f}")
            if r.results:
                top3 = r.results[:3]
                for j, sr in enumerate(top3, 1):
                    title_short = sr.title[:50]
                    lines.append(f"  {j}. [{sr.source}] {sr.score:.3f} — {title_short}")
        lines.append("")

    # Source distribution
    lines.append("## ソース分布")
    lines.append("")
    source_counts: dict[str, int] = {}
    source_scores: dict[str, list[float]] = {}
    for r in results:
        for sr in r.results[:5]:
            source_counts[sr.source] = source_counts.get(sr.source, 0) + 1
            if sr.source not in source_scores:
                source_scores[sr.source] = []
            source_scores[sr.source].append(sr.score)

    lines.append("| ソース | 出現回数 (Top-5) | 平均スコア | 最高 | 最低 |")
    lines.append("|:-------|-----------------:|-----------:|-----:|-----:|")
    for src in ["gnosis", "kairos", "sophia", "chronos"]:
        cnt = source_counts.get(src, 0)
        scores = source_scores.get(src, [])
        if scores:
            avg_s = sum(scores) / len(scores)
            max_s = max(scores)
            min_s = min(scores)
            lines.append(f"| {src} | {cnt} | {avg_s:.3f} | {max_s:.3f} | {min_s:.3f} |")
        else:
            lines.append(f"| {src} | 0 | — | — | — |")
    lines.append("")

    # Weaknesses and recommendations
    lines.append("## 弱点分析 & 改善提案")
    lines.append("")

    weak_queries = [r for r in results if r.precision_at_5 < 0.4]
    if weak_queries:
        lines.append("### 弱いクエリ")
        lines.append("")
        for r in weak_queries:
            lines.append(f"- **{r.query_id}** ({r.description}): P@5={r.precision_at_5:.2f}")
            if r.category == "edge_case" and r.query_id == "E1":
                lines.append("  → 期待通り（無関係クエリ）")
            else:
                lines.append(f"  → キーワードヒット: {r.keyword_hits}/{r.total_keywords}")
        lines.append("")

    # Coverage issues
    low_cov = [r for r in results if r.source_coverage < 0.5 and r.category != "edge_case"]
    if low_cov:
        lines.append("### ソースカバレッジ不足")
        lines.append("")
        for r in low_cov:
            found = set(sr.source for sr in r.results[:5])
            expected = set(r.category)  # simplified
            lines.append(f"- **{r.query_id}**: 結果ソース={found}")
        lines.append("")

    lines.append("### 改善提案")
    lines.append("")
    lines.append("1. **スコア正規化**: Gnōsis (L2距離) と pkl (cosine) の異なるスコア体系を統一")
    lines.append("2. **日本語対応**: multilingual embedding モデルの評価")
    lines.append("3. **リランキング**: キーワード + セマンティックのハイブリッドスコアリング")
    lines.append("4. **インデックス更新**: Sophia (116件) の拡充")
    lines.append("")

    return "\n".join(lines)


def main():
    results = run_benchmark()

    # Generate report
    report = generate_report(results)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\n📝 Report: {REPORT_PATH}")

    # Save raw results as JSON
    json_data = []
    for r in results:
        d = {
            "query_id": r.query_id,
            "query": r.query,
            "category": r.category,
            "description": r.description,
            "precision_at_5": r.precision_at_5,
            "mrr": r.mrr,
            "source_coverage": r.source_coverage,
            "latency_seconds": r.latency_seconds,
            "keyword_hits": r.keyword_hits,
            "total_keywords": r.total_keywords,
            "top_results": [
                {"source": sr.source, "score": sr.score, "title": sr.title}
                for sr in r.results[:5]
            ],
        }
        json_data.append(d)
    RESULTS_JSON.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📊 Raw Data: {RESULTS_JSON}")

    # Summary
    avg_p5 = sum(r.precision_at_5 for r in results) / len(results)
    avg_mrr = sum(r.mrr for r in results) / len(results)
    print(f"\n{'='*40}")
    print(f"  Precision@5 = {avg_p5:.3f}  {'✅' if avg_p5 >= 0.6 else '⚠️'}")
    print(f"  MRR         = {avg_mrr:.3f}  {'✅' if avg_mrr >= 0.5 else '⚠️'}")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()
