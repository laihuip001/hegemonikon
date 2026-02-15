# PROOF: [L1/算出] <- aristos/ ステータス集約
"""
Aristos Status — 進化状態とフィードバック統計の集約

Desktop Dashboard や CLI から呼び出される統一ステータスAPI。
evolved weights, feedback 統計, 進化履歴を集約して返す。

Usage:
    from aristos.status import get_aristos_status
    status = get_aristos_status()
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .route_feedback import load_route_feedback, ROUTE_FEEDBACK_PATH
from .pt_optimizer import COST_WEIGHTS_PATH, DEFAULT_COST_WEIGHTS


# =============================================================================
# Types
# =============================================================================

@dataclass
class FeedbackStats:
    """フィードバック統計"""
    total_count: int = 0
    avg_quality: float = 0.0
    high_quality_count: int = 0   # > 0.7
    low_quality_count: int = 0    # < 0.3
    depth_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class EvolvedWeightsInfo:
    """進化済み重み情報"""
    available: bool = False
    weights: Dict[str, float] = field(default_factory=dict)
    fitness_scalar: float = 0.0
    generation: int = 0


@dataclass
class AristosStatus:
    """Aristos システム全体のステータス"""
    feedback: FeedbackStats = field(default_factory=FeedbackStats)
    evolved_weights: EvolvedWeightsInfo = field(default_factory=EvolvedWeightsInfo)
    default_weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_COST_WEIGHTS))

    def to_dict(self) -> dict:
        return asdict(self)


# =============================================================================
# API
# =============================================================================

def get_feedback_stats(path: Optional[Path] = None) -> FeedbackStats:
    """フィードバック統計を集約"""
    feedbacks = load_route_feedback(path or ROUTE_FEEDBACK_PATH)

    if not feedbacks:
        return FeedbackStats()

    qualities = [fb.quality for fb in feedbacks]
    depth_dist: Dict[str, int] = {}
    for fb in feedbacks:
        depth_dist[fb.depth] = depth_dist.get(fb.depth, 0) + 1

    return FeedbackStats(
        total_count=len(feedbacks),
        avg_quality=round(sum(qualities) / len(qualities), 3),
        high_quality_count=sum(1 for q in qualities if q > 0.7),
        low_quality_count=sum(1 for q in qualities if q < 0.3),
        depth_distribution=depth_dist,
    )


def get_evolved_weights_info(
    path: Optional[Path] = None,
) -> EvolvedWeightsInfo:
    """進化済み重み情報を取得"""
    p = path or COST_WEIGHTS_PATH
    if not p.exists():
        return EvolvedWeightsInfo()

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        weights = data.get("cost_weights", {})
        fitness = data.get("fitness", {})
        generation = data.get("generation", 0)

        return EvolvedWeightsInfo(
            available=bool(weights),
            weights=weights,
            fitness_scalar=fitness.get("scalar", 0.0),
            generation=generation,
        )
    except (json.JSONDecodeError, KeyError):
        return EvolvedWeightsInfo()


def get_aristos_status(
    feedback_path: Optional[Path] = None,
    weights_path: Optional[Path] = None,
) -> AristosStatus:
    """Aristos システム全体のステータスを取得

    Desktop Dashboard の /api/aristos/status から呼び出される想定。
    """
    return AristosStatus(
        feedback=get_feedback_stats(feedback_path),
        evolved_weights=get_evolved_weights_info(weights_path),
    )
