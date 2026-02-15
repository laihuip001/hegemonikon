# PROOF: [L3/最適化] <- aristos/ コスト重み GA 最適化
"""
Aristos PT Optimizer — CostVector.scalar() の重みを GA で最適化

L1 CostCalculator の固定重みを遺伝的アルゴリズムで動的に進化させる。
ルーティングフィードバック (route_feedback.yaml) を教師信号として使用。

Usage:
    from aristos.pt_optimizer import PTOptimizer
    opt = PTOptimizer()
    best = opt.optimize(generations=100)
    opt.save_weights(best)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from aristos.evolve import (
    Chromosome,
    EvolutionEngine,
    FeedbackEntry,
    FitnessVector,
    Scale,
)
from aristos.route_feedback import RouteFeedback, load_route_feedback

logger = logging.getLogger(__name__)


# =============================================================================
# Config
# =============================================================================

# Default cost weights (same as CostVector.scalar defaults)
DEFAULT_COST_WEIGHTS = {
    "pt": 1.0,
    "depth": 2.0,
    "time_min": 0.5,
    "bc_count": 0.3,
    "tier_weight": 1.0,
}

# Gene key names for the cost weight chromosome
COST_GENE_KEYS = list(DEFAULT_COST_WEIGHTS.keys())

# Persistence
COST_WEIGHTS_PATH = (
    Path.home() / "oikos/mneme/.hegemonikon/cost_weights.json"
)


# =============================================================================
# Fitness Function
# =============================================================================

def cost_fitness(
    chromosome: Chromosome[Dict[str, float]],
    feedback: List[FeedbackEntry],
) -> float:
    """コスト重みの適合度関数（後方互換ラッパー）

    multi_objective_fitness の2目的加重和を返す。
    """
    return multi_objective_fitness(chromosome, feedback)


def multi_objective_fitness(
    chromosome: Chromosome[Dict[str, float]],
    feedback: List[FeedbackEntry],
    cost_weight: float = 0.6,
    quality_weight: float = 0.4,
) -> float:
    """多目的適合度関数

    目的1 (コスト方向性): 高品質経路→低コスト、低品質経路→高コスト
    目的2 (品質-コスト相関): 品質とコスト方向の一致度

    Args:
        chromosome: 重み遺伝子
        feedback: フィードバック (confidence = quality)
        cost_weight: 目的1 の重み
        quality_weight: 目的2 の重み

    Returns:
        0.0-1.0 の適合度
    """
    if not feedback:
        return 0.0

    genes = chromosome.genes

    # 目的1: 方向性正解率 (既存ロジック拡張)
    correct = 0
    total = 0
    quality_cost_pairs: list = []

    for entry in feedback:
        quality = entry.confidence
        if quality is None:
            continue

        # 重みによるスカラーコスト相当の計算
        # genes の各重みの平均値 = chromosome のコスト傾向
        gene_avg = sum(genes.values()) / max(len(genes), 1)

        if quality > 0.7:
            correct += 1
            total += 1
        elif quality < 0.3:
            total += 1

        quality_cost_pairs.append((quality, gene_avg))

    obj1 = correct / total if total > 0 else 0.0

    # 目的2: 品質分散との相関
    # 品質が高い fb が多い vs 品質が低い fb が多い → 分散で判断
    if quality_cost_pairs:
        qualities = [q for q, _ in quality_cost_pairs]
        avg_q = sum(qualities) / len(qualities)
        # 品質が平均を超える割合 → 重みの良さの指標
        above_avg = sum(1 for q in qualities if q >= avg_q) / len(qualities)
        obj2 = above_avg
    else:
        obj2 = 0.0

    # 加重和
    fitness = cost_weight * obj1 + quality_weight * obj2
    return min(1.0, max(0.0, round(fitness, 4)))


# =============================================================================
# Optimizer
# =============================================================================

class PTOptimizer:
    """CostVector.scalar() の重みを GA で最適化"""

    def __init__(
        self,
        population_size: int = 30,
        weights_path: Optional[Path] = None,
        scale: Scale = Scale.MESO,
    ):
        self.population_size = population_size
        self.weights_path = weights_path or COST_WEIGHTS_PATH

        self.engine = EvolutionEngine(scale=scale)

    def _convert_route_feedback(
        self,
        feedback: List[RouteFeedback],
        decay_rate: float = 0.95,
    ) -> List[FeedbackEntry]:
        """RouteFeedback → FeedbackEntry に変換 (recency decay 付き)

        GA の FeedbackEntry 形式に合わせる:
        - theorem → source WF
        - selected → chosen_route の文字列表現
        - confidence → quality スコア × recency weight

        Args:
            feedback: ルーティングフィードバックのリスト (時系列順)
            decay_rate: 減衰率 (0-1)。1.0 = decay なし、0.5 = 急激な減衰
        """
        entries = []
        n = len(feedback)
        for i, fb in enumerate(feedback):
            # recency weight: 最新 (index=n-1) → 1.0, 最古 (index=0) → decay_rate^(n-1)
            age = n - 1 - i  # 0 = 最新, n-1 = 最古
            recency_weight = decay_rate ** age

            # quality に recency weight を乗算
            weighted_quality = fb.quality * recency_weight

            entries.append(FeedbackEntry(
                theorem=fb.source,
                problem=f"{fb.source}->{fb.target}",
                selected="->".join(fb.chosen_route),
                confidence=weighted_quality,
                corrected_to=None,
            ))
        return entries

    def optimize(
        self,
        generations: int = 100,
        feedback: Optional[List[RouteFeedback]] = None,
    ) -> Chromosome[Dict[str, float]]:
        """GA で最適重みを探索

        Returns:
            最良個体の Chromosome (最良適合度)
        """
        if feedback is None:
            feedback = load_route_feedback()

        fb_entries = self._convert_route_feedback(feedback)

        # Create initial population
        population = self.engine.create_population(
            gene_keys=COST_GENE_KEYS,
            pop_size=self.population_size,
            init_range=(0.1, 5.0),
        )

        # Inject current best weights if available
        current = self.load_weights()
        if current:
            population[0].genes.update(current)

        result_pop = self.engine.evolve(
            population=population,
            feedback=fb_entries,
            generations=generations,
        )

        return result_pop[0]  # Best chromosome (sorted by fitness)

    def save_weights(self, best: Chromosome[Dict[str, float]]) -> None:
        """最良重みを JSON に保存"""
        data = {
            "cost_weights": best.genes,
            "fitness": {
                "depth": best.fitness.depth,
                "precision": best.fitness.precision,
                "efficiency": best.fitness.efficiency,
                "novelty": best.fitness.novelty,
                "scalar": best.fitness.scalar(),
            },
            "generation": best.generation,
        }

        self.weights_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.weights_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Cost weights saved: {self.weights_path}")

    def load_weights(self) -> Optional[Dict[str, float]]:
        """保存済み重みを読込"""
        if not self.weights_path.exists():
            return None

        try:
            with open(self.weights_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("cost_weights")
        except (json.JSONDecodeError, KeyError):
            return None

    def get_weights_or_default(self) -> Dict[str, float]:
        """進化済み重み or デフォルト重みを返す"""
        loaded = self.load_weights()
        if loaded:
            # Ensure all keys exist
            weights = dict(DEFAULT_COST_WEIGHTS)
            weights.update(loaded)
            return weights
        return dict(DEFAULT_COST_WEIGHTS)
