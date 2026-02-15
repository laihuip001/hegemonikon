# PROOF: [L3/テスト] <- aristos/ PT 最適化テスト
"""
Aristos L3 PT Optimizer テスト

コスト重み最適化の統合テスト。
"""

import json
import tempfile
from pathlib import Path

import pytest

from aristos.cost import CostCalculator, CostVector, Depth
from aristos.route_feedback import (
    RouteFeedback,
    load_route_feedback,
    log_route_feedback,
    clear_route_feedback,
)
from aristos.pt_optimizer import (
    PTOptimizer,
    DEFAULT_COST_WEIGHTS,
    COST_GENE_KEYS,
    cost_fitness,
)
from aristos.evolve import Chromosome, FeedbackEntry, FitnessVector


# =============================================================================
# RouteFeedback Tests
# =============================================================================


class TestRouteFeedback:
    """ルーティングフィードバック I/O テスト"""

    def test_log_and_load(self, tmp_path: Path):
        """YAML ログの書込みと読込み"""
        path = tmp_path / "fb.yaml"

        fb = RouteFeedback(
            source="noe",
            target="dia",
            chosen_route=["noe", "bou", "dia"],
            quality=0.85,
            cost_scalar=12.5,
            actual_time_min=15.0,
            depth="L3",
        )
        log_route_feedback(fb, path=path)

        loaded = load_route_feedback(path=path)
        assert len(loaded) == 1
        assert loaded[0].source == "noe"
        assert loaded[0].target == "dia"
        assert loaded[0].quality == 0.85
        assert loaded[0].chosen_route == ["noe", "bou", "dia"]

    def test_append_multiple(self, tmp_path: Path):
        """複数フィードバックの追記"""
        path = tmp_path / "fb.yaml"

        for i in range(5):
            fb = RouteFeedback(
                source=f"wf{i}",
                target="dia",
                chosen_route=[f"wf{i}", "dia"],
                quality=0.1 * (i + 1),
            )
            log_route_feedback(fb, path=path)

        loaded = load_route_feedback(path=path)
        assert len(loaded) == 5

    def test_clear(self, tmp_path: Path):
        """クリア"""
        path = tmp_path / "fb.yaml"

        fb = RouteFeedback(
            source="noe", target="dia",
            chosen_route=["noe", "dia"], quality=0.9,
        )
        log_route_feedback(fb, path=path)
        count = clear_route_feedback(path=path)
        assert count == 1
        assert not path.exists()

    def test_load_empty(self, tmp_path: Path):
        """存在しないファイルの読込み"""
        path = tmp_path / "nonexistent.yaml"
        loaded = load_route_feedback(path=path)
        assert loaded == []


# =============================================================================
# CostCalculator Evolved Weights Tests
# =============================================================================


class TestCostCalculatorEvolved:
    """CostCalculator evolved_weights 統合テスト"""

    def test_default_scalar(self):
        """デフォルト重みでのスカラー計算"""
        calc = CostCalculator()
        cost = calc.calculate("noe")
        s1 = cost.scalar()
        s2 = calc.scalar_with_evolved(cost)
        assert s1 == s2  # evolved_weights=None → デフォルト

    def test_evolved_scalar(self):
        """進化済み重みでのスカラー計算"""
        evolved = {"pt": 0.0, "depth": 5.0, "time_min": 0.0, "bc_count": 0.0, "tier_weight": 0.0}
        calc = CostCalculator(evolved_weights=evolved)
        cost = calc.calculate("noe")  # depth=L2 → depth_cost=2.0

        evolved_scalar = calc.scalar_with_evolved(cost)
        default_scalar = cost.scalar()

        # evolved: depth=2.0 * 5.0 = 10.0
        assert evolved_scalar == 2.0 * 5.0
        # default は複数要素の合計
        assert default_scalar != evolved_scalar

    def test_evolved_vs_manual(self):
        """進化済み重みの手動計算との一致"""
        w = {"pt": 2.0, "depth": 1.0, "time_min": 0.0, "bc_count": 0.0, "tier_weight": 3.0}
        calc = CostCalculator(evolved_weights=w)
        cost = CostVector(pt=5.0, depth=2.0, time_min=10.0, bc_count=8, tier_weight=2.0)

        expected = 5.0 * 2.0 + 2.0 * 1.0 + 10.0 * 0.0 + 8 * 0.0 + 2.0 * 3.0
        assert calc.scalar_with_evolved(cost) == expected


# =============================================================================
# PTOptimizer Tests
# =============================================================================


class TestPTOptimizer:
    """PT Optimizer テスト"""

    def test_gene_keys(self):
        """遺伝子キーがコスト重みと一致"""
        assert set(COST_GENE_KEYS) == set(DEFAULT_COST_WEIGHTS.keys())

    def test_get_weights_default(self, tmp_path: Path):
        """保存済み重みなし → デフォルト"""
        opt = PTOptimizer(weights_path=tmp_path / "w.json")
        w = opt.get_weights_or_default()
        assert w == DEFAULT_COST_WEIGHTS

    def test_save_and_load(self, tmp_path: Path):
        """重みの保存と読込み"""
        opt = PTOptimizer(weights_path=tmp_path / "w.json")

        # Fake chromosome
        genes = {"pt": 1.5, "depth": 3.0, "time_min": 0.2, "bc_count": 0.1, "tier_weight": 2.0}
        best = Chromosome(
            genes=genes,
            fitness=FitnessVector(depth=0.0, precision=0.8, efficiency=0.0, novelty=0.0),
            generation=10,
        )
        opt.save_weights(best)

        loaded = opt.load_weights()
        assert loaded is not None
        assert loaded["pt"] == 1.5
        assert loaded["depth"] == 3.0

    def test_optimize_with_feedback(self, tmp_path: Path):
        """フィードバックからの最適化"""
        opt = PTOptimizer(
            population_size=10,
            weights_path=tmp_path / "w.json",
        )

        # Synthetic feedback
        feedback = [
            RouteFeedback(
                source="noe", target="dia",
                chosen_route=["noe", "bou", "dia"],
                quality=0.9,
                cost_scalar=10.0,
            )
            for _ in range(20)
        ]

        best = opt.optimize(generations=10, feedback=feedback)
        assert best is not None
        assert isinstance(best.genes, dict)
        assert all(k in best.genes for k in COST_GENE_KEYS)

    def test_weights_format_compatible(self, tmp_path: Path):
        """保存形式が CostCalculator と互換"""
        opt = PTOptimizer(weights_path=tmp_path / "w.json")
        genes = {"pt": 1.5, "depth": 3.0, "time_min": 0.2, "bc_count": 0.1, "tier_weight": 2.0}
        best = Chromosome(
            genes=genes,
            fitness=FitnessVector(),
            generation=0,
        )
        opt.save_weights(best)

        loaded = opt.load_weights()
        calc = CostCalculator(evolved_weights=loaded)
        cost = calc.calculate("noe")
        result = calc.scalar_with_evolved(cost)
        assert isinstance(result, float)
        assert result > 0


# =============================================================================
# Cost Fitness Function Tests
# =============================================================================


class TestCostFitness:
    """コスト適合度関数テスト"""

    def test_empty_feedback(self):
        """空フィードバック → 0.0"""
        genes = {k: 1.0 for k in COST_GENE_KEYS}
        chrom = Chromosome(genes=genes, fitness=FitnessVector(), generation=0)
        assert cost_fitness(chrom, []) == 0.0

    def test_high_quality_feedback(self):
        """高品質フィードバックのみ → 1.0"""
        genes = {k: 1.0 for k in COST_GENE_KEYS}
        chrom = Chromosome(genes=genes, fitness=FitnessVector(), generation=0)

        feedback = [
            FeedbackEntry(
                theorem="noe",
                problem="test",
                selected="noe->dia",
                confidence=0.9,  # high quality
            )
            for _ in range(10)
        ]
        result = cost_fitness(chrom, feedback)
        assert result == 1.0

    def test_low_quality_feedback(self):
        """低品質フィードバックのみ → obj1=0, obj2>0 (品質分布成分)"""
        genes = {k: 1.0 for k in COST_GENE_KEYS}
        chrom = Chromosome(genes=genes, fitness=FitnessVector(), generation=0)

        feedback = [
            FeedbackEntry(
                theorem="noe",
                problem="test",
                selected="noe->dia",
                confidence=0.1,  # low quality
            )
            for _ in range(10)
        ]
        result = cost_fitness(chrom, feedback)
        # multi_objective: obj1=0.0 (正解なし), obj2=1.0 (全員>=avg)
        # fitness = 0.6*0.0 + 0.4*1.0 = 0.4
        assert result == 0.4
