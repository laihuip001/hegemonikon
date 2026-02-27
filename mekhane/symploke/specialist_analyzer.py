# PROOF: [L2/Mekhane] <- mekhane/symploke/ A0->Auto->AddedByCI
#!/usr/bin/env python3
# PROOF: [L2/分析] <- mekhane/symploke/ A4→Specialist 効果測定→analyzer が担う
# PURPOSE: Basanos Perspective の効果分析 — 有用率ランキング + domain/axis 集計
"""
Specialist Analyzer — Perspective 品質ダッシュボード

basanos_feedback.py の FeedbackStore からデータを読み込み、
perspective / domain / axis 別の有用率を分析・表示する。

Usage:
    python specialist_analyzer.py rank [--top N]
    python specialist_analyzer.py domain
    python specialist_analyzer.py axis
    python specialist_analyzer.py json [--output FILE]
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from mekhane.symploke.basanos_feedback import FeedbackStore  # noqa: E402


# PURPOSE: Perspective 有用率ランキング
def rank_perspectives(store: FeedbackStore, top: int = 20) -> list[dict]:
    """有用率でソートした Perspective ランキングを返す。"""
    all_fb = store.get_all_feedback()
    ranked = []
    for pid, fb in all_fb.items():
        ranked.append({
            "perspective_id": pid,
            "domain": fb.domain,
            "axis": fb.axis,
            "total_reviews": fb.total_reviews,
            "useful_count": fb.useful_count,
            "usefulness_rate": round(fb.usefulness_rate, 3),
            "last_used": fb.last_used,
        })
    # 有用率降順、同率なら使用回数降順
    ranked.sort(key=lambda x: (-x["usefulness_rate"], -x["total_reviews"]))
    return ranked[:top]


# PURPOSE: Domain 別集計
def aggregate_by_domain(store: FeedbackStore) -> list[dict]:
    """Domain 別の集計を返す。"""
    all_fb = store.get_all_feedback()
    domains: dict[str, dict] = defaultdict(lambda: {
        "total_reviews": 0, "useful_count": 0, "perspectives": 0,
    })
    for fb in all_fb.values():
        d = domains[fb.domain]
        d["total_reviews"] += fb.total_reviews
        d["useful_count"] += fb.useful_count
        d["perspectives"] += 1

    result = []
    for domain, stats in sorted(domains.items()):
        rate = stats["useful_count"] / stats["total_reviews"] if stats["total_reviews"] > 0 else 0.0
        result.append({
            "domain": domain,
            "perspectives": stats["perspectives"],
            "total_reviews": stats["total_reviews"],
            "useful_count": stats["useful_count"],
            "usefulness_rate": round(rate, 3),
        })
    result.sort(key=lambda x: -x["usefulness_rate"])
    return result


# PURPOSE: Axis 別集計
def aggregate_by_axis(store: FeedbackStore) -> list[dict]:
    """Axis 別の集計を返す。"""
    all_fb = store.get_all_feedback()
    axes: dict[str, dict] = defaultdict(lambda: {
        "total_reviews": 0, "useful_count": 0, "perspectives": 0,
    })
    for fb in all_fb.values():
        a = axes[fb.axis]
        a["total_reviews"] += fb.total_reviews
        a["useful_count"] += fb.useful_count
        a["perspectives"] += 1

    result = []
    for axis, stats in sorted(axes.items()):
        rate = stats["useful_count"] / stats["total_reviews"] if stats["total_reviews"] > 0 else 0.0
        result.append({
            "axis": axis,
            "perspectives": stats["perspectives"],
            "total_reviews": stats["total_reviews"],
            "useful_count": stats["useful_count"],
            "usefulness_rate": round(rate, 3),
        })
    result.sort(key=lambda x: -x["usefulness_rate"])
    return result


# PURPOSE: 全分析データを JSON で出力
def full_analysis(store: FeedbackStore, top: int = 20) -> dict:
    """全分析データを辞書で返す。"""
    low_quality = store.get_low_quality_perspectives(threshold=0.1)
    return {
        "ranking": rank_perspectives(store, top=top),
        "by_domain": aggregate_by_domain(store),
        "by_axis": aggregate_by_axis(store),
        "low_quality_ids": low_quality,
        "total_perspectives": len(store.get_all_feedback()),
    }


# PURPOSE: CLI 表示
def display_rank(store: FeedbackStore, top: int = 20) -> None:
    """ランキングをテーブル形式で表示。"""
    ranked = rank_perspectives(store, top=top)
    if not ranked:
        print("  データなし")
        return

    print(f"\n{'#':>3}  {'Rate':>6}  {'Used':>5}  {'Useful':>6}  {'Domain':<20}  {'Axis':<12}  ID")
    print("-" * 90)
    for i, r in enumerate(ranked, 1):
        rate_pct = f"{r['usefulness_rate'] * 100:.1f}%"
        print(f"{i:>3}  {rate_pct:>6}  {r['total_reviews']:>5}  {r['useful_count']:>6}  "
              f"{r['domain']:<20}  {r['axis']:<12}  {r['perspective_id']}")


def display_domain(store: FeedbackStore) -> None:
    """Domain 別集計を表示。"""
    domains = aggregate_by_domain(store)
    if not domains:
        print("  データなし")
        return

    print(f"\n{'Rate':>6}  {'Used':>5}  {'Useful':>6}  {'#P':>4}  Domain")
    print("-" * 60)
    for d in domains:
        rate_pct = f"{d['usefulness_rate'] * 100:.1f}%"
        print(f"{rate_pct:>6}  {d['total_reviews']:>5}  {d['useful_count']:>6}  "
              f"{d['perspectives']:>4}  {d['domain']}")


def display_axis(store: FeedbackStore) -> None:
    """Axis 別集計を表示。"""
    axes = aggregate_by_axis(store)
    if not axes:
        print("  データなし")
        return

    print(f"\n{'Rate':>6}  {'Used':>5}  {'Useful':>6}  {'#P':>4}  Axis")
    print("-" * 60)
    for a in axes:
        rate_pct = f"{a['usefulness_rate'] * 100:.1f}%"
        print(f"{rate_pct:>6}  {a['total_reviews']:>5}  {a['useful_count']:>6}  "
              f"{a['perspectives']:>4}  {a['axis']}")


# PURPOSE: CLI エントリーポイント
def main() -> None:
    parser = argparse.ArgumentParser(description="Specialist Analyzer — Perspective 効果分析")
    parser.add_argument("command", choices=["rank", "domain", "axis", "json"],
                        help="分析コマンド")
    parser.add_argument("--top", type=int, default=20, help="ランキング表示数 (default: 20)")
    parser.add_argument("--output", type=str, default=None, help="JSON 出力ファイル")
    args = parser.parse_args()

    store = FeedbackStore()

    if args.command == "rank":
        print("=== Perspective 有用率ランキング ===")
        display_rank(store, top=args.top)
    elif args.command == "domain":
        print("=== Domain 別 集計 ===")
        display_domain(store)
    elif args.command == "axis":
        print("=== Axis 別 集計 ===")
        display_axis(store)
    elif args.command == "json":
        data = full_analysis(store, top=args.top)
        output = json.dumps(data, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(output)
            print(f"  → {args.output} に出力しました")
        else:
            print(output)


if __name__ == "__main__":
    main()
