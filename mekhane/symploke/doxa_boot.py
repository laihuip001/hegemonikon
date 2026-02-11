#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/
# PURPOSE: /boot Phase 3 で Doxa 信念を読込み、Sophia 昇格候補を検出する
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → 信念は /dox で記録される
   → しかし /boot は信念を参照しない
   → doxa_boot.py が /boot Phase 3 で信念を読込み、
     Creator に提示し、Sophia 昇格候補を検出する

Q.E.D.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from mekhane.fep.doxa_persistence import (
    Belief,
    BeliefStrength,
    DoxaStore,
)


# =============================================================================
# Constants
# =============================================================================

# Sophia 昇格閾値
# ⚠️ PROVISIONAL: 以下は全て仮値。実データ収集後に calibration すべき。
# Calibration Plan:
#   1. 10+ 信念が蓄積されたら precision/recall を測定
#   2. Sophia に昇格した信念の「使われ度」を追跡
#   3. 使われない昇格 = 閾値が低すぎる証拠
PROMOTION_MIN_STRENGTH = BeliefStrength.STRONG  # PROVISIONAL
PROMOTION_MIN_CONFIDENCE = 0.85  # PROVISIONAL: 実感として 0.8-0.9 の範囲
PROMOTION_MIN_AGE_DAYS = 14.0  # PROVISIONAL: 2週間の定着期間
PROMOTION_MIN_EVIDENCE = 2  # PROVISIONAL: 最低2件の根拠


# =============================================================================
# Data Classes
# =============================================================================


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class PromotionCandidate:
    """Sophia 昇格候補。"""

    belief: Belief
    reasons: List[str] = field(default_factory=list)
    score: float = 0.0


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class DoxaBootResult:
    """Doxa boot 読込結果。"""

    beliefs_loaded: int = 0
    active_count: int = 0
    archived_count: int = 0
    promotion_candidates: List[PromotionCandidate] = field(default_factory=list)
    summary: str = ""


# =============================================================================
# Core Functions
# =============================================================================


# PURPOSE: /boot Phase 3 で Doxa 信念を読込む
def load_doxa_for_boot(
    store_path: Optional[Path] = None,
) -> DoxaBootResult:
    """/boot Phase 3 で Doxa 信念を読込む。

    Args:
        store_path: beliefs.yaml のパス (省略時: DEFAULT_STORE_PATH)

    Returns:
        DoxaBootResult with loaded beliefs and promotion candidates
    """
    store = DoxaStore()
    loaded = store.load_from_file(store_path)

    result = DoxaBootResult(
        beliefs_loaded=loaded,
        active_count=len(store.list_all()),
        archived_count=len(store.list_archived()),
    )

    # Sophia 昇格候補を検出
    result.promotion_candidates = check_promotion_candidates(store)

    # サマリー生成
    result.summary = format_doxa_summary(store, result.promotion_candidates)

    return result


# PURPOSE: Sophia 昇格候補を検出する
def check_promotion_candidates(
    store: DoxaStore,
) -> List[PromotionCandidate]:
    """Sophia 昇格候補を検出する。

    昇格条件:
    1. strength >= STRONG
    2. confidence >= 0.85
    3. age_days >= 14
    4. len(evidence) >= 2

    Returns:
        昇格候補のリスト (スコア降順)
    """
    # 強さの序列
    strength_order = {
        BeliefStrength.WEAK: 0,
        BeliefStrength.MODERATE: 1,
        BeliefStrength.STRONG: 2,
        BeliefStrength.CORE: 3,
    }

    candidates = []

    for belief in store.list_all():
        # 昇格済みはスキップ
        if belief.is_promoted:
            continue

        reasons = []
        score = 0.0

        # 条件1: 強さ
        if strength_order.get(belief.strength, 0) >= strength_order[PROMOTION_MIN_STRENGTH]:
            reasons.append(f"strength={belief.strength.value}")
            score += 0.25
        else:
            continue  # 強さ不足は即スキップ

        # 条件2: 確信度
        if belief.confidence >= PROMOTION_MIN_CONFIDENCE:
            reasons.append(f"confidence={belief.confidence:.0%}")
            score += 0.25
        else:
            continue

        # 条件3: 定着期間
        if belief.age_days >= PROMOTION_MIN_AGE_DAYS:
            reasons.append(f"age={belief.age_days:.0f}d")
            score += 0.25
        else:
            continue

        # 条件4: 根拠数
        if len(belief.evidence) >= PROMOTION_MIN_EVIDENCE:
            reasons.append(f"evidence={len(belief.evidence)}")
            score += 0.25
        else:
            continue

        # 全条件クリア
        candidates.append(
            PromotionCandidate(belief=belief, reasons=reasons, score=score)
        )

    # スコア降順
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates


# PURPOSE: Creator 向け Doxa サマリーを生成
def format_doxa_summary(
    store: DoxaStore,
    candidates: List[PromotionCandidate],
) -> str:
    """Creator 向け Doxa サマリーを生成。"""
    beliefs = store.list_all()
    archived = store.list_archived()

    lines = [
        "### H4 Doxa — 信念ストア",
        f"| 項目 | 数 |",
        f"|:-----|---:|",
        f"| Active | {len(beliefs)} |",
        f"| Archived | {len(archived)} |",
    ]

    if beliefs:
        # 強さ別集計
        strength_counts = {}
        for b in beliefs:
            s = b.strength.value
            strength_counts[s] = strength_counts.get(s, 0) + 1

        lines.append("")
        lines.append("| 強さ | 数 |")
        lines.append("|:-----|---:|")
        for s, c in sorted(strength_counts.items()):
            lines.append(f"| {s} | {c} |")

    if candidates:
        lines.append("")
        lines.append("#### 📈 Sophia 昇格候補")
        for c in candidates:
            reasons_str = ", ".join(c.reasons)
            lines.append(
                f"- **{c.belief.content[:50]}** ({reasons_str})"
            )

    return "\n".join(lines)
