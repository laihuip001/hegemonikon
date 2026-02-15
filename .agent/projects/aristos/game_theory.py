# PROOF: [L3/設計] <- aristos/ L4 ゲーム理論的 WF 配分最適化
"""
Aristos Game Theory — WF 間の Nash 均衡ベース配分

L3 (PTOptimizer) が個別 WF のコスト重みを最適化するのに対し、
L4 は複数 WF を同時に考慮したゲーム理論的アプローチで
リソース（時間・認知コスト）の最適配分を探索する。

Key Concepts:
- PayoffMatrix: WF ペアのペイオフを計算
- NashSolver: 2-player 純粋戦略 Nash 均衡探索
- L4Coordinator: PTOptimizer 出力 → WF 間配分最適化

Usage:
    from aristos.game_theory import L4Coordinator
    coord = L4Coordinator()
    allocation = coord.optimize_allocation(["noe", "dia", "ene"])
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .cost import CostCalculator, CostVector, Depth


# =============================================================================
# Types
# =============================================================================

@dataclass
class Payoff:
    """WF ペアのペイオフ値"""
    wf_a: str
    wf_b: str
    payoff_a: float  # WF A が先に実行される場合の利得
    payoff_b: float  # WF B が先に実行される場合の利得


@dataclass
class NashEquilibrium:
    """Nash 均衡の結果"""
    pure_strategies: List[Tuple[str, str]]  # [(wf, "cooperate"/"defect"), ...]
    is_pareto_optimal: bool = False
    total_payoff: float = 0.0
    notes: str = ""


@dataclass
class Allocation:
    """WF リソース配分結果"""
    wf_weights: Dict[str, float]  # WF名 → 配分比率 (合計1.0)
    total_cost: float = 0.0
    equilibria: List[NashEquilibrium] = field(default_factory=list)
    method: str = "proportional"  # "proportional", "nash", "utilitarian"


# =============================================================================
# Payoff Matrix
# =============================================================================

class PayoffMatrix:
    """WF ペアからペイオフ行列を生成

    ペイオフ計算の直感:
    - 先に実行する WF の品質が後続に影響する (情報の前方伝播)
    - 高コストな WF を先に実行すると失敗時のリスクが大きい
    - 低コストな WF を先に実行すると情報収集コストが低い
    """

    def __init__(self, calc: Optional[CostCalculator] = None):
        self._calc = calc or CostCalculator()

    def compute(
        self,
        wf_a: str,
        wf_b: str,
        depth: Depth = Depth.L2,
    ) -> Payoff:
        """2つの WF 間のペイオフを計算

        ペイオフ = 1 / (cost + 1) で正規化。
        低コスト → 高ペイオフ。
        """
        cost_a = self._calc.calculate(wf_a, depth=depth)
        cost_b = self._calc.calculate(wf_b, depth=depth)

        scalar_a = cost_a.scalar()
        scalar_b = cost_b.scalar()

        # A → B 順序のペイオフ: A が低コストなら高い
        payoff_a = 1.0 / (scalar_a + 1.0)
        # B → A 順序のペイオフ: B が低コストなら高い
        payoff_b = 1.0 / (scalar_b + 1.0)

        return Payoff(
            wf_a=wf_a,
            wf_b=wf_b,
            payoff_a=round(payoff_a, 4),
            payoff_b=round(payoff_b, 4),
        )

    def build_matrix(
        self,
        wfs: List[str],
        depth: Depth = Depth.L2,
    ) -> Dict[Tuple[str, str], Payoff]:
        """全ペアのペイオフ行列を構築"""
        matrix = {}
        for i, a in enumerate(wfs):
            for j, b in enumerate(wfs):
                if i < j:
                    matrix[(a, b)] = self.compute(a, b, depth)
        return matrix


# =============================================================================
# Nash Solver
# =============================================================================

class NashSolver:
    """2-player 純粋戦略 Nash 均衡の探索

    各 WF ペアについて、どちらの順序が均衡かを判定。
    """

    def find_pure_equilibria(
        self,
        matrix: Dict[Tuple[str, str], Payoff],
    ) -> List[NashEquilibrium]:
        """全ペアの純粋戦略均衡を探索"""
        equilibria = []

        for (a, b), payoff in matrix.items():
            strategies = []

            if payoff.payoff_a >= payoff.payoff_b:
                # A 先行が支配戦略
                strategies.append((a, "first"))
                strategies.append((b, "second"))
                total = payoff.payoff_a
            else:
                strategies.append((b, "first"))
                strategies.append((a, "second"))
                total = payoff.payoff_b

            # Pareto 最適性: 一方を改善すると他方が悪化するか
            is_pareto = abs(payoff.payoff_a - payoff.payoff_b) > 0.01

            equilibria.append(NashEquilibrium(
                pure_strategies=strategies,
                is_pareto_optimal=is_pareto,
                total_payoff=round(total, 4),
            ))

        return equilibria


# =============================================================================
# L4 Coordinator
# =============================================================================

class L4Coordinator:
    """L3 PTOptimizer 出力を受け取り、WF 間配分を最適化

    3つの配分戦略:
    - proportional: コストの逆数で比例配分
    - nash: Nash 均衡に基づく順序最適化
    - utilitarian: 総ペイオフ最大化
    """

    def __init__(
        self,
        calc: Optional[CostCalculator] = None,
        evolved_weights: Optional[Dict[str, float]] = None,
    ):
        if calc is None:
            calc = CostCalculator(evolved_weights=evolved_weights)
        self._calc = calc
        self._matrix = PayoffMatrix(calc=self._calc)
        self._solver = NashSolver()

    def optimize_allocation(
        self,
        wfs: List[str],
        depth: Depth = Depth.L2,
        method: str = "proportional",
    ) -> Allocation:
        """WF 群のリソース配分を最適化

        Args:
            wfs: 最適化対象の WF リスト
            depth: 深度レベル
            method: 配分戦略

        Returns:
            Allocation: 配分結果
        """
        if not wfs:
            return Allocation(wf_weights={}, method=method)

        # コスト計算
        costs = {}
        for wf in wfs:
            cost = self._calc.calculate(wf, depth=depth)
            costs[wf] = cost.scalar()

        # 配分計算
        if method == "proportional":
            return self._proportional(costs, wfs)
        elif method == "nash":
            return self._nash(costs, wfs, depth)
        else:
            return self._proportional(costs, wfs)

    def _proportional(
        self,
        costs: Dict[str, float],
        wfs: List[str],
    ) -> Allocation:
        """コスト逆数に基づく比例配分

        低コスト WF により多くのリソースを配分。
        """
        inv_costs = {wf: 1.0 / (c + 1.0) for wf, c in costs.items()}
        total_inv = sum(inv_costs.values())

        weights = {
            wf: round(inv / total_inv, 4)
            for wf, inv in inv_costs.items()
        }

        return Allocation(
            wf_weights=weights,
            total_cost=sum(costs.values()),
            method="proportional",
        )

    def _nash(
        self,
        costs: Dict[str, float],
        wfs: List[str],
        depth: Depth,
    ) -> Allocation:
        """Nash 均衡に基づく配分"""
        matrix = self._matrix.build_matrix(wfs, depth)
        equilibria = self._solver.find_pure_equilibria(matrix)

        # 均衡から勝率ベースの重みを計算
        wins: Dict[str, int] = {wf: 0 for wf in wfs}
        for eq in equilibria:
            for wf, strategy in eq.pure_strategies:
                if strategy == "first":
                    wins[wf] = wins.get(wf, 0) + 1

        total_wins = sum(wins.values()) or 1
        weights = {
            wf: round(w / total_wins, 4)
            for wf, w in wins.items()
        }

        return Allocation(
            wf_weights=weights,
            total_cost=sum(costs.values()),
            equilibria=equilibria,
            method="nash",
        )
