# PROOF: [L2/ドメイン] <- mekhane/symploke/ O4→perspective進化→自律生成
"""F15: Perspective Evolver — 高スコア domain から新しい Perspective を自動提案する。

FeedbackStore の domain 集計を元に、高有用率 domain の未カバー axis に
新しい Perspective を提案する。

Usage:
    from perspective_evolver import propose_new_perspectives, evolve
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from basanos_feedback import FeedbackStore


# 全 axis 定義 (basanos_matrix.yaml の axes セクションと同期)
ALL_AXES = [
    "correctness", "robustness", "maintainability", "performance",
    "security", "testability", "documentation", "architecture",
]


def _get_domain_stats(store: FeedbackStore) -> dict[str, dict]:
    """domain 別の集計統計を取得する。"""
    all_fb = store.get_all_feedback()
    domain_stats: dict[str, dict] = {}

    for pid, fb in all_fb.items():
        # perspective_id 形式: "domain-axis" (例: "python-correctness")
        parts = pid.rsplit("-", 1)
        if len(parts) != 2:
            continue
        domain, axis = parts

        if domain not in domain_stats:
            domain_stats[domain] = {
                "total_reviews": 0,
                "useful_count": 0,
                "axes_covered": set(),
            }
        domain_stats[domain]["total_reviews"] += fb.total_reviews
        domain_stats[domain]["useful_count"] += fb.useful_count
        domain_stats[domain]["axes_covered"].add(axis)

    return domain_stats


def propose_new_perspectives(
    store: FeedbackStore,
    max_proposals: int = 5,
    min_usefulness_rate: float = 0.5,
    min_reviews: int = 5,
) -> list[dict]:
    """高有用率 domain の未カバー axis から新 Perspective を提案する。

    Args:
        store: FeedbackStore インスタンス
        max_proposals: 最大提案数
        min_usefulness_rate: 提案対象の最小有用率
        min_reviews: 提案対象の最小レビュー数

    Returns:
        提案リスト [{"domain": str, "axis": str, "reason": str, "score": float}]
    """
    domain_stats = _get_domain_stats(store)

    proposals: list[dict] = []
    for domain, stats in domain_stats.items():
        total = stats["total_reviews"]
        useful = stats["useful_count"]
        if total < min_reviews:
            continue
        rate = useful / total
        if rate < min_usefulness_rate:
            continue

        # 未カバーの axis を検出
        covered = stats["axes_covered"]
        uncovered = [a for a in ALL_AXES if a not in covered]

        for axis in uncovered:
            proposals.append({
                "domain": domain,
                "axis": axis,
                "reason": f"Domain '{domain}' has {rate:.0%} usefulness rate "
                          f"({useful}/{total} reviews) but lacks '{axis}' axis",
                "score": round(rate * (total / 10), 3),  # 有用率 × 信頼度
            })

    # スコア降順でソート、上位 N 件
    proposals.sort(key=lambda p: p["score"], reverse=True)
    return proposals[:max_proposals]


def evolve(
    store: FeedbackStore,
    matrix_path: Optional[Path] = None,
    max_proposals: int = 5,
    dry_run: bool = True,
) -> dict:
    """進化レポートを生成する。

    dry_run=True (デフォルト) ではレポートのみ生成。
    dry_run=False では BasanosMatrix に新 Perspective を追加する。

    Returns:
        {"proposals": list[dict], "applied": int, "dry_run": bool}
    """
    proposals = propose_new_perspectives(store, max_proposals=max_proposals)

    applied = 0
    export_path = None
    if not dry_run and proposals:
        # F20: 提案を pending_perspectives.json にエクスポート
        # NOTE: specialist 定義はコードベースにハードコードされているため、
        # 直接追加ではなく提案ファイルに書き出し、手動レビュー後に取り込む。
        import json
        from datetime import datetime

        _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
        export_dir = _PROJECT_ROOT / "logs" / "evolution"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = export_dir / f"pending_perspectives_{timestamp}.json"
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "proposals": proposals,
            "status": "pending_review",
        }
        export_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))
        applied = len(proposals)

    return {
        "proposals": proposals,
        "applied": applied,
        "dry_run": dry_run,
        "total_proposals": len(proposals),
        "export_path": str(export_path) if export_path else None,
    }


# CLI エントリポイント
if __name__ == "__main__":
    import json
    import sys

    store = FeedbackStore()
    mode = sys.argv[1] if len(sys.argv) > 1 else "report"

    if mode == "json":
        result = evolve(store, dry_run=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = evolve(store, dry_run=True)
        proposals = result["proposals"]
        if not proposals:
            print("🔬 No evolution proposals — all axes covered or insufficient data")
        else:
            print(f"🔬 {len(proposals)} evolution proposals:")
            for i, p in enumerate(proposals, 1):
                print(f"  {i}. {p['domain']}/{p['axis']} (score={p['score']})")
                print(f"     {p['reason']}")
