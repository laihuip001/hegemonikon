# F15: Multi-objective Fitness テスト
"""
multi_objective_fitness() の2目的加重和テスト。
cost_fitness() の後方互換性も検証。
"""
import pytest
from aristos.pt_optimizer import cost_fitness, multi_objective_fitness
from aristos.evolve import Chromosome, FeedbackEntry


def _make_chromosome(genes: dict) -> Chromosome:
    return Chromosome(genes=genes, fitness=None)


def _make_feedback(quality: float) -> FeedbackEntry:
    return FeedbackEntry(
        theorem="O1",
        selected="noe+",
        confidence=quality,
        problem="test_problem",
    )


class TestMultiObjectiveFitnessBasic:
    """基本動作"""

    def test_empty_feedback(self):
        ch = _make_chromosome({"pt": 1.0})
        assert multi_objective_fitness(ch, []) == 0.0

    def test_all_high_quality(self):
        """全 fb が高品質 → fitness 高い"""
        ch = _make_chromosome({"pt": 1.0, "depth": 2.0})
        fbs = [_make_feedback(0.9) for _ in range(5)]
        f = multi_objective_fitness(ch, fbs)
        assert f > 0.5

    def test_all_low_quality(self):
        """全 fb が低品質 → fitness 低い"""
        ch = _make_chromosome({"pt": 1.0, "depth": 2.0})
        fbs = [_make_feedback(0.1) for _ in range(5)]
        f = multi_objective_fitness(ch, fbs)
        assert f < 0.5

    def test_mixed_quality(self):
        """混合品質 → 中間"""
        ch = _make_chromosome({"pt": 1.0})
        fbs = [_make_feedback(0.9), _make_feedback(0.1), _make_feedback(0.5)]
        f = multi_objective_fitness(ch, fbs)
        assert 0.0 <= f <= 1.0

    def test_output_bounded(self):
        """出力は 0-1"""
        ch = _make_chromosome({"pt": 1.0})
        for q in [0.0, 0.3, 0.5, 0.7, 1.0]:
            fbs = [_make_feedback(q)]
            f = multi_objective_fitness(ch, fbs)
            assert 0.0 <= f <= 1.0


class TestMultiObjectiveWeights:
    """加重パラメータのテスト"""

    def test_cost_only(self):
        """cost_weight=1.0, quality_weight=0.0"""
        ch = _make_chromosome({"pt": 1.0})
        fbs = [_make_feedback(0.9) for _ in range(3)]
        f = multi_objective_fitness(ch, fbs, cost_weight=1.0, quality_weight=0.0)
        assert f > 0.0

    def test_quality_only(self):
        """cost_weight=0.0, quality_weight=1.0"""
        ch = _make_chromosome({"pt": 1.0})
        fbs = [_make_feedback(0.9) for _ in range(3)]
        f = multi_objective_fitness(ch, fbs, cost_weight=0.0, quality_weight=1.0)
        assert f > 0.0


class TestBackwardCompatibility:
    """cost_fitness の後方互換"""

    def test_cost_fitness_delegates(self):
        """cost_fitness は multi_objective_fitness を呼ぶ"""
        ch = _make_chromosome({"pt": 1.0, "depth": 2.0})
        fbs = [_make_feedback(0.8), _make_feedback(0.2)]
        assert cost_fitness(ch, fbs) == multi_objective_fitness(ch, fbs)

    def test_cost_fitness_empty(self):
        ch = _make_chromosome({"pt": 1.0})
        assert cost_fitness(ch, []) == 0.0
