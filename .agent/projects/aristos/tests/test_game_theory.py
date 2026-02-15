# F7: L4 Game Theory テスト
"""
PayoffMatrix, NashSolver, L4Coordinator の基本動作検証。
"""
import pytest
from aristos.game_theory import (
    L4Coordinator,
    NashSolver,
    PayoffMatrix,
)
from aristos.cost import Depth


class TestPayoffMatrix:
    """ペイオフ行列テスト"""

    def test_compute_payoff(self):
        pm = PayoffMatrix()
        payoff = pm.compute("noe", "dia")
        assert payoff.wf_a == "noe"
        assert payoff.wf_b == "dia"
        assert payoff.payoff_a > 0
        assert payoff.payoff_b > 0

    def test_build_matrix(self):
        pm = PayoffMatrix()
        matrix = pm.build_matrix(["noe", "dia", "ene"])
        # C(3,2) = 3 pairs
        assert len(matrix) == 3

    def test_single_wf_empty_matrix(self):
        pm = PayoffMatrix()
        matrix = pm.build_matrix(["noe"])
        assert len(matrix) == 0

    def test_payoff_inverse_of_cost(self):
        """低コスト WF は高ペイオフ"""
        pm = PayoffMatrix()
        payoff = pm.compute("now", "ax")  # now=L1 cheap, ax=L3 expensive
        # now (低コスト) のペイオフが ax より高いはず
        assert payoff.payoff_a > payoff.payoff_b


class TestNashSolver:
    """Nash 均衡探索テスト"""

    def test_find_equilibria(self):
        pm = PayoffMatrix()
        matrix = pm.build_matrix(["noe", "dia"])
        solver = NashSolver()
        equilibria = solver.find_pure_equilibria(matrix)
        assert len(equilibria) == 1
        assert len(equilibria[0].pure_strategies) == 2

    def test_strategies_have_first_and_second(self):
        pm = PayoffMatrix()
        matrix = pm.build_matrix(["noe", "dia"])
        solver = NashSolver()
        equilibria = solver.find_pure_equilibria(matrix)
        strategies = dict(equilibria[0].pure_strategies)
        assert "first" in strategies.values()
        assert "second" in strategies.values()


class TestL4Coordinator:
    """L4 Coordinator テスト"""

    def test_empty_wfs(self):
        coord = L4Coordinator()
        alloc = coord.optimize_allocation([])
        assert alloc.wf_weights == {}

    def test_proportional(self):
        coord = L4Coordinator()
        alloc = coord.optimize_allocation(
            ["noe", "dia", "ene"],
            method="proportional",
        )
        assert len(alloc.wf_weights) == 3
        total = sum(alloc.wf_weights.values())
        assert abs(total - 1.0) < 0.01  # 合計 ≈ 1.0

    def test_nash_allocation(self):
        coord = L4Coordinator()
        alloc = coord.optimize_allocation(
            ["noe", "dia", "ene"],
            method="nash",
        )
        assert alloc.method == "nash"
        assert len(alloc.equilibria) > 0
        assert len(alloc.wf_weights) == 3

    def test_with_evolved_weights(self):
        """evolved weights 付きで動作する"""
        coord = L4Coordinator(
            evolved_weights={"pt": 1.5, "depth": 3.0, "time_min": 0.2},
        )
        alloc = coord.optimize_allocation(["noe", "dia"])
        assert len(alloc.wf_weights) == 2
        assert alloc.total_cost > 0

    def test_depth_affects_allocation(self):
        """深度変更で配分が変わる"""
        coord = L4Coordinator()
        alloc_l1 = coord.optimize_allocation(["noe", "dia"], depth=Depth.L1)
        alloc_l3 = coord.optimize_allocation(["noe", "dia"], depth=Depth.L3)
        # L3 はコスト高 → total_cost が異なる
        assert alloc_l1.total_cost != alloc_l3.total_cost
