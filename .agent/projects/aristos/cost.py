# PROOF: [L1/算出] <- aristos/ WF コスト計算
"""
Aristos Cost — WF 実行コスト計算

WF の実行コストを多次元で計算し、
ルーティング最適化のエッジ重みとして使用する。

Usage:
    from aristos.cost import CostCalculator, CostVector
    calc = CostCalculator()
    cost = calc.calculate("noe", depth="L3")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


# =============================================================================
# Types
# =============================================================================


class Depth(Enum):
    """WF 深度レベル"""
    L0 = 0  # Bypass
    L1 = 1  # Quick
    L2 = 2  # Standard
    L3 = 3  # Deep


class Tier(Enum):
    """WF 階層"""
    OMEGA = "omega"   # Ω: 1-2文字, 統合オーケストレーター
    DELTA = "delta"   # Δ: 3文字, ドメイン専門家
    TAU = "tau"       # τ: 3-4文字, 個別タスク
    MACRO = "macro"   # CCL マクロ (ccl-*)
    SPECIAL = "special"  # 特殊 (/u, /m)


@dataclass
class CostVector:
    """多次元コストベクトル

    WF の実行コストを複数の軸で表現する。
    スカラーコストは weighted sum で算出。
    """
    pt: float = 0.0        # CCL 演算ポイント (演算子の重み合計)
    depth: float = 0.0     # 認知深度コスト (L0=0, L1=1, L2=2, L3=4)
    time_min: float = 0.0  # 推定実行時間 (分)
    bc_count: int = 0      # 適用される BC の数
    tier_weight: float = 0.0  # 階層重み (Ω=4, Δ=2, τ=1)

    def scalar(self, weights: Optional[Dict[str, float]] = None) -> float:
        """加重スカラーコストを算出"""
        w = weights or {
            "pt": 1.0,
            "depth": 2.0,
            "time_min": 0.5,
            "bc_count": 0.3,
            "tier_weight": 1.0,
        }
        return (
            self.pt * w.get("pt", 1.0)
            + self.depth * w.get("depth", 2.0)
            + self.time_min * w.get("time_min", 0.5)
            + self.bc_count * w.get("bc_count", 0.3)
            + self.tier_weight * w.get("tier_weight", 1.0)
        )

    def __repr__(self) -> str:
        return (
            f"Cost(pt={self.pt:.1f}, depth={self.depth:.1f}, "
            f"time={self.time_min:.1f}m, bc={self.bc_count}, "
            f"tier={self.tier_weight:.1f}, scalar={self.scalar():.2f})"
        )


# =============================================================================
# Cost Tables
# =============================================================================

# Depth → 認知コスト (非線形: L3 は L2 の2倍)
DEPTH_COST = {
    Depth.L0: 0.0,
    Depth.L1: 1.0,
    Depth.L2: 2.0,
    Depth.L3: 4.0,
}

# Tier → 階層重み
TIER_WEIGHT = {
    Tier.OMEGA: 4.0,
    Tier.DELTA: 2.0,
    Tier.TAU: 1.0,
    Tier.MACRO: 0.0,  # Macro のコストは構成 WF の合計
    Tier.SPECIAL: 0.5,
}

# WF → 推定実行時間 (分) のデフォルト
DEFAULT_TIME_ESTIMATES = {
    # Ω layer
    "o": 15.0, "s": 15.0, "h": 10.0, "p": 10.0, "k": 10.0, "a": 10.0,
    "ax": 30.0, "x": 10.0,
    # Δ layer
    "noe": 20.0, "bou": 10.0, "zet": 10.0, "ene": 15.0, "dia": 10.0,
    # τ layer
    "boot": 5.0, "bye": 5.0, "now": 1.0, "dev": 10.0, "eat": 15.0,
    "vet": 10.0, "rom": 3.0, "mek": 10.0, "sop": 5.0, "dox": 3.0,
    "pis": 3.0, "pro": 3.0, "ore": 3.0, "epi": 5.0, "pra": 5.0,
    "met": 5.0, "sta": 5.0, "hod": 5.0, "tro": 5.0, "tek": 5.0,
    "kho": 5.0, "chr": 3.0, "tel": 3.0, "euk": 3.0, "pat": 5.0,
    "gno": 5.0,
    # Special
    "u": 2.0, "m": 0.0, "dendron": 3.0,
}

# Depth → BC 適用数の目安
DEPTH_BC_COUNT = {
    Depth.L0: 5,   # Always-On のみ
    Depth.L1: 8,   # + BC-3, BC-10, BC-14
    Depth.L2: 12,  # + BC-8, BC-9, BC-15
    Depth.L3: 18,  # 全 BC
}

# CCL 演算子 → pt コスト
OPERATOR_PT = {
    "_": 1,    # sequence
    "~": 3,    # oscillation
    "~*": 4,   # convergence
    "*": 2,    # fusion
    "+": 1,    # detail (depth up)
    "-": 0,    # reduction (depth down)
    ">>": 1,   # pipe
    "F:": 2,   # for loop (per iteration)
    "C:": 2,   # conditional
    "V:": 3,   # validation
    "I:": 2,   # if-then
    "E:": 2,   # else
    "R:": 3,   # repeat
}


# =============================================================================
# Calculator
# =============================================================================

class CostCalculator:
    """WF コスト計算器"""

    def __init__(
        self,
        time_estimates: Optional[Dict[str, float]] = None,
        operator_pt: Optional[Dict[str, int]] = None,
    ):
        self._time = time_estimates or DEFAULT_TIME_ESTIMATES
        self._pt = operator_pt or OPERATOR_PT

    def classify_tier(self, wf_name: str) -> Tier:
        """WF 名から階層を判定"""
        if wf_name.startswith("ccl-"):
            return Tier.MACRO
        if wf_name in ("u", "m"):
            return Tier.SPECIAL
        if len(wf_name) <= 2:
            return Tier.OMEGA
        if len(wf_name) == 3:
            return Tier.DELTA
        return Tier.TAU

    def classify_depth(self, wf_name: str) -> Depth:
        """WF 名から深度を判定 (派生なしの場合)"""
        tier = self.classify_tier(wf_name)
        if tier == Tier.OMEGA:
            return Depth.L3
        if tier == Tier.DELTA:
            return Depth.L2
        return Depth.L1

    def parse_depth_from_derivative(self, ccl: str) -> Depth:
        """CCL 派生記号から深度を判定"""
        clean = ccl.strip().lstrip("/")
        if clean.endswith("+"):
            return Depth.L3
        if clean.endswith("-"):
            return Depth.L1
        return Depth.L2

    def calculate(
        self,
        wf_name: str,
        depth: Optional[Depth] = None,
        ccl_expr: Optional[str] = None,
    ) -> CostVector:
        """WF の実行コストを計算

        Args:
            wf_name: WF 名 (例: "noe", "ccl-vet")
            depth: 深度 (省略時は WF 階層から自動判定)
            ccl_expr: CCL 式 (マクロの場合、pt を計算)
        """
        tier = self.classify_tier(wf_name)
        if depth is None:
            depth = self.classify_depth(wf_name)

        pt = 0.0
        if ccl_expr:
            pt = self.calculate_pt(ccl_expr)

        return CostVector(
            pt=pt,
            depth=DEPTH_COST[depth],
            time_min=self._time.get(wf_name, 5.0),
            bc_count=DEPTH_BC_COUNT[depth],
            tier_weight=TIER_WEIGHT[tier],
        )

    def calculate_pt(self, ccl_expr: str) -> float:
        """CCL 式の pt コストを計算"""
        total = 0.0
        for op, pt in self._pt.items():
            total += ccl_expr.count(op) * pt
        return total

    def calculate_macro(
        self,
        macro_name: str,
        ccl_expr: str,
        component_wfs: list[str],
    ) -> CostVector:
        """CCL マクロの合成コストを計算

        マクロのコスト = 構成 WF のコスト合計 + 演算子 pt
        """
        total = CostVector(pt=self.calculate_pt(ccl_expr))

        for wf in component_wfs:
            wf_cost = self.calculate(wf)
            total.time_min += wf_cost.time_min
            total.depth = max(total.depth, wf_cost.depth)
            total.bc_count = max(total.bc_count, wf_cost.bc_count)
            total.tier_weight = max(total.tier_weight, wf_cost.tier_weight)

        return total
