# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI
#!/usr/bin/env python3
# PROOF: [L2/ドメイン] <- mekhane/symploke/ O4→perspective繁殖→自律進化
"""F25: Perspective Breeder — 高有用率 Perspective のバリエーションを生成する。

高スコア Perspective の特性を分析し、未カバー領域に対する
新たなバリエーションを提案する。LLM (Cortex API) を用いた
子孫生成と、ルールベースのバリエーション生成の両方をサポート。

Usage:
    from perspective_breeder import breed_perspectives
    result = breed_perspectives(store, max_children=5)
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 繁殖の閾値
MIN_USEFULNESS_RATE = 0.7    # 親になるための最低有用率
MIN_REVIEWS_FOR_PARENT = 10  # 親になるための最低レビュー数

# バリエーション戦略
VARIATION_STRATEGIES = [
    {
        "name": "axis_transfer",
        "description": "高有用率 domain の成功 axis を別 domain に転用",
    },
    {
        "name": "granularity_shift",
        "description": "粗粒度の perspective をより詳細に分割",
        "granularity_map": {
            "correctness": ["type_safety", "null_safety", "boundary_check"],
            "robustness": ["error_handling", "input_validation", "timeout_handling"],
            "maintainability": ["naming_clarity", "code_complexity", "dependency_management"],
            "security": ["injection_prevention", "auth_validation", "data_sanitization"],
        },
    },
    {
        "name": "combination",
        "description": "2つの高有用率 axis を組み合わせた複合 perspective",
    },
]


def _get_parent_candidates(store) -> list[dict]:
    """繁殖の親になれる高品質 Perspective を選出する。"""
    all_fb = store.get_all_feedback()
    parents = []

    for pid, fb in all_fb.items():
        if fb.total_reviews < MIN_REVIEWS_FOR_PARENT:
            continue
        rate = fb.usefulness_rate
        if rate < MIN_USEFULNESS_RATE:
            continue

        parts = pid.rsplit("-", 1)
        if len(parts) != 2:
            continue

        parents.append({
            "perspective_id": pid,
            "domain": parts[0],
            "axis": parts[1],
            "usefulness_rate": rate,
            "total_reviews": fb.total_reviews,
        })

    # 有用率順でソート
    parents.sort(key=lambda p: p["usefulness_rate"], reverse=True)
    return parents


def _breed_axis_transfer(parents: list[dict], existing_ids: set[str]) -> list[dict]:
    """高有用率ドメインの成功 axis を他ドメインに転用する。"""
    children = []
    # ドメイン一覧を収集
    domains = set(p["domain"] for p in parents)

    for parent in parents:
        for target_domain in domains:
            if target_domain == parent["domain"]:
                continue
            child_id = f"{target_domain}-{parent['axis']}"
            if child_id in existing_ids:
                continue

            children.append({
                "perspective_id": child_id,
                "domain": target_domain,
                "axis": parent["axis"],
                "strategy": "axis_transfer",
                "parent": parent["perspective_id"],
                "reason": f"'{parent['domain']}' で {parent['usefulness_rate']:.0%} の"
                          f" '{parent['axis']}' を '{target_domain}' に転用",
                "confidence": round(parent["usefulness_rate"] * 0.7, 3),
            })
            existing_ids.add(child_id)

    return children


def _breed_granularity_shift(parents: list[dict], existing_ids: set[str]) -> list[dict]:
    """粗粒度 axis をより詳細に分割する。"""
    children = []
    granularity_map = VARIATION_STRATEGIES[1]["granularity_map"]

    for parent in parents:
        subdivisions = granularity_map.get(parent["axis"], [])
        for sub_axis in subdivisions:
            child_id = f"{parent['domain']}-{sub_axis}"
            if child_id in existing_ids:
                continue

            children.append({
                "perspective_id": child_id,
                "domain": parent["domain"],
                "axis": sub_axis,
                "strategy": "granularity_shift",
                "parent": parent["perspective_id"],
                "reason": f"'{parent['axis']}' ({parent['usefulness_rate']:.0%})"
                          f" をサブ軸 '{sub_axis}' に細分化",
                "confidence": round(parent["usefulness_rate"] * 0.6, 3),
            })
            existing_ids.add(child_id)

    return children


def _breed_combination(parents: list[dict], existing_ids: set[str]) -> list[dict]:
    """2つの高有用率 axis を組み合わせた複合 perspective。"""
    children = []
    if len(parents) < 2:
        return children

    # 上位5組のペアのみ
    for i in range(min(len(parents), 5)):
        for j in range(i + 1, min(len(parents), 5)):
            p1, p2 = parents[i], parents[j]
            if p1["domain"] != p2["domain"]:
                continue  # 同一ドメイン内のみ

            combined_axis = f"{p1['axis']}_{p2['axis']}"
            child_id = f"{p1['domain']}-{combined_axis}"
            if child_id in existing_ids:
                continue

            avg_rate = (p1["usefulness_rate"] + p2["usefulness_rate"]) / 2
            children.append({
                "perspective_id": child_id,
                "domain": p1["domain"],
                "axis": combined_axis,
                "strategy": "combination",
                "parents": [p1["perspective_id"], p2["perspective_id"]],
                "reason": f"'{p1['axis']}' + '{p2['axis']}' の複合 perspective "
                          f"(平均有用率: {avg_rate:.0%})",
                "confidence": round(avg_rate * 0.5, 3),
            })
            existing_ids.add(child_id)

    return children


def breed_perspectives(
    store,
    max_children: int = 10,
    dry_run: bool = True,
) -> dict:
    """高品質 Perspective から子孫を生成する。

    Args:
        store: FeedbackStore インスタンス
        max_children: 最大生成数
        dry_run: True の場合は提案のみ、False なら提案ファイルにエクスポート

    Returns:
        {
            "parents": list[dict],
            "children": list[dict],
            "strategies_used": list[str],
            "dry_run": bool,
            "export_path": str | None,
        }
    """
    parents = _get_parent_candidates(store)
    if not parents:
        return {
            "parents": [],
            "children": [],
            "strategies_used": [],
            "dry_run": dry_run,
            "export_path": None,
        }

    existing_ids = set(store.get_all_feedback().keys())

    # 3つの戦略を並行実行
    all_children: list[dict] = []
    strategies_used: list[str] = []

    transfer = _breed_axis_transfer(parents, existing_ids)
    if transfer:
        all_children.extend(transfer)
        strategies_used.append("axis_transfer")

    granularity = _breed_granularity_shift(parents, existing_ids)
    if granularity:
        all_children.extend(granularity)
        strategies_used.append("granularity_shift")

    combination = _breed_combination(parents, existing_ids)
    if combination:
        all_children.extend(combination)
        strategies_used.append("combination")

    # confidence 降順でソート、上位 N 件
    all_children.sort(key=lambda c: c.get("confidence", 0), reverse=True)
    all_children = all_children[:max_children]

    export_path = None
    if not dry_run and all_children:
        export_dir = _PROJECT_ROOT / "logs" / "evolution"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = export_dir / f"bred_perspectives_{timestamp}.json"
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "parents_count": len(parents),
            "children": all_children,
            "strategies_used": strategies_used,
            "status": "pending_review",
        }
        export_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))

    return {
        "parents": parents[:5],  # 上位5親のみ返す
        "children": all_children,
        "strategies_used": strategies_used,
        "dry_run": dry_run,
        "export_path": str(export_path) if export_path else None,
    }


# CLI エントリポイント
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    from basanos_feedback import FeedbackStore

    store = FeedbackStore()
    mode = sys.argv[1] if len(sys.argv) > 1 else "report"

    if mode == "json":
        result = breed_perspectives(store, dry_run=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif mode == "apply":
        result = breed_perspectives(store, dry_run=False)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = breed_perspectives(store, dry_run=True)
        parents = result["parents"]
        children = result["children"]
        print(f"\n{'='*50}")
        print(f"Perspective Breeder Report")
        print(f"{'='*50}")
        print(f"  Parents: {len(parents)}")
        print(f"  Children: {len(children)}")
        print(f"  Strategies: {', '.join(result['strategies_used']) or 'none'}")
        if children:
            print(f"\n🧬 Top children:")
            for i, c in enumerate(children[:5], 1):
                print(f"  {i}. {c['perspective_id']} [{c['strategy']}]")
                print(f"     {c['reason']}")
                print(f"     confidence: {c.get('confidence', 0):.1%}")
        else:
            print("\n  No children generated (insufficient parent data)")
