# PROOF: [L1/定理] <- mekhane/fep/
"""
PROOF: [L1/定理] このファイルは存在しなければならない

A0 → 認知には環境定義 (Perigraphē) がある
   → P1-P3 で場・経路・軌道を定義
   → perigraphe_engine が担う

Q.E.D.

---

P-series Perigraphē Engine — 環境定義モジュール

Hegemonikón P-series (Perigraphē) 定理: P1 Khōra, P2 Hodos, P3 Trokhia
FEP層での環境・スコープ・経路・軌道の定義を担当。
(P4 Tekhnē は tekhne_registry.py として Phase A で分離済み)

Architecture:
- P1 Khōra = スコープ定義 (phys/conc/rela)
- P2 Hodos = 経路定義 (direct/iterate/parallel)
- P3 Trokhia = 軌道定義 (cycle/spiral/branch)

References:
- /kho, /hod, /tro ワークフロー
- FEP: 状態空間の境界と遷移経路
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

# =============================================================================
# P1 Khōra (場・スコープ)
# =============================================================================


# PURPOSE: P1 Khōra の派生モード (Lefebvre の空間三分法)
class KhoraDerivative(Enum):
    """P1 Khōra の派生モード (Lefebvre の空間三分法)"""

    PHYSICAL = "phys"  # 物理的空間 (Perceived space)
    CONCEPTUAL = "conc"  # 概念的空間 (Conceived space)
    RELATIONAL = "rela"  # 関係的空間 (Lived space)


# PURPOSE: スコープのスケール
class ScopeScale(Enum):
    """スコープのスケール"""

    MICRO = "micro"  # 局所的
    MACRO = "macro"  # 広域的


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: P1 Khōra 評価結果
class KhoraResult:
    """P1 Khōra 評価結果

    Attributes:
        target: 対象
        derivative: 派生モード
        x_scale: X軸方向スケール
        y_scale: Y軸方向スケール
        boundaries: 境界定義
        included: スコープ内に含まれるもの
        excluded: スコープ外に除外されるもの
    """

    target: str
    derivative: KhoraDerivative
    x_scale: ScopeScale
    y_scale: ScopeScale
    boundaries: List[str]
    included: List[str] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)

    # PURPOSE: perigraphe_engine の scope label 処理を実行する
    @property
    # PURPOSE: スコープラベル (Micro×Micro 等)
    def scope_label(self) -> str:
        """スコープラベル (Micro×Micro 等)"""
        return f"{self.x_scale.value.capitalize()}×{self.y_scale.value.capitalize()}"

# PURPOSE: P1 Khōra: スコープを定義

def define_scope(
    target: str,
    derivative: Optional[KhoraDerivative] = None,
    x_scale: ScopeScale = ScopeScale.MICRO,
    y_scale: ScopeScale = ScopeScale.MICRO,
    included: Optional[List[str]] = None,
    excluded: Optional[List[str]] = None,
) -> KhoraResult:
    """P1 Khōra: スコープを定義

    Args:
        target: 対象
        derivative: 派生モード (None で自動推論)
        x_scale: X軸スケール
        y_scale: Y軸スケール
        included: 含めるもの
        excluded: 除外するもの

    Returns:
        KhoraResult
    """
    # 派生自動推論 (キーワードベース)
    if derivative is None:
        target_lower = target.lower()
        if any(
            w in target_lower
            for w in ["チーム", "ネットワーク", "関係", "コミュニティ"]
        ):
            derivative = KhoraDerivative.RELATIONAL
        elif any(
            w in target_lower for w in ["設計", "モデル", "スキーマ", "アーキテクチャ"]
        ):
            derivative = KhoraDerivative.CONCEPTUAL
        else:
            derivative = KhoraDerivative.PHYSICAL

    # 境界生成
    boundaries = []
    if x_scale == ScopeScale.MICRO and y_scale == ScopeScale.MICRO:
        boundaries.append("局所的・詳細レベル")
    elif x_scale == ScopeScale.MACRO and y_scale == ScopeScale.MACRO:
        boundaries.append("広域的・全体レベル")
    else:
        boundaries.append("混合スケール")

    return KhoraResult(
        target=target,
        derivative=derivative,
        x_scale=x_scale,
        y_scale=y_scale,
        boundaries=boundaries,
        included=included or [],
        excluded=excluded or [],
    )


# =============================================================================
# P2 Hodos (道・経路)
# =============================================================================

# PURPOSE: P2 Hodos の派生モード

class HodosDerivative(Enum):
    """P2 Hodos の派生モード"""

    DIRECT = "direct"  # 直接経路 (A→B)
    ITERATE = "iterate"  # 反復経路 (A→B→A→B)
    PARALLEL = "parallel"  # 並列経路 (A→B, A→C)


# PURPOSE: P2 Hodos 評価結果
@dataclass
class HodosResult:
    """P2 Hodos 評価結果

    Attributes:
        path_name: 経路名
        derivative: 派生モード
        start: 開始点
        end: 終了点
        waypoints: 経由点
        estimated_steps: 予想ステップ数
    """

    path_name: str
    derivative: HodosDerivative
    start: str
    end: str
    waypoints: List[str] = field(default_factory=list)
    estimated_steps: int = 1

    # PURPOSE: perigraphe_engine の total nodes 処理を実行する
    @property
    # PURPOSE: 総ノード数
    def total_nodes(self) -> int:
        """総ノード数"""
        return 2 + len(self.waypoints)
# PURPOSE: P2 Hodos: 経路を定義


def define_path(
    path_name: str,
    start: str,
    end: str,
    derivative: Optional[HodosDerivative] = None,
    waypoints: Optional[List[str]] = None,
) -> HodosResult:
    """P2 Hodos: 経路を定義

    Args:
        path_name: 経路名
        start: 開始点
        end: 終了点
        derivative: 派生モード (None で自動推論)
        waypoints: 経由点

    Returns:
        HodosResult
    """
    wp = waypoints or []

    # 派生自動推論
    if derivative is None:
        if start == end:
            derivative = HodosDerivative.ITERATE
        elif len(wp) > 0 and any(wp.count(w) > 1 for w in wp):
            derivative = HodosDerivative.ITERATE
        else:
            derivative = HodosDerivative.DIRECT

    # ステップ数計算
    if derivative == HodosDerivative.ITERATE:
        estimated_steps = (len(wp) + 1) * 2  # 往復
    elif derivative == HodosDerivative.PARALLEL:
        estimated_steps = len(wp) + 1  # 同時
    else:
        estimated_steps = len(wp) + 1

    return HodosResult(
        path_name=path_name,
        derivative=derivative,
        start=start,
        end=end,
        waypoints=wp,
        estimated_steps=estimated_steps,
    )


# =============================================================================
# P3 Trokhia (軌道・サイクル)
# =============================================================================
# PURPOSE: P3 Trokhia の派生モード


class TrokhiaDerivative(Enum):
    """P3 Trokhia の派生モード"""

    CYCLE = "cycle"  # 循環 (A→B→C→A)
    SPIRAL = "spiral"  # 螺旋 (A→B→C→A' elevated)
    BRANCH = "branch"  # 分岐 (A→B or A→C)

# PURPOSE: P3 Trokhia 評価結果

@dataclass
class TrokhiaResult:
    """P3 Trokhia 評価結果

    Attributes:
        trajectory_name: 軌道名
        derivative: 派生モード
        phases: フェーズリスト
        current_phase: 現在フェーズ (0-indexed)
        iteration: 現在イテレーション
        max_iterations: 最大イテレーション (None で無限)
    """

    trajectory_name: str
    derivative: TrokhiaDerivative
    phases: List[str]
    current_phase: int = 0
    iteration: int = 1
    max_iterations: Optional[int] = None

    # PURPOSE: perigraphe_engine の current phase name 処理を実行する
    @property
    # PURPOSE: 現在フェーズ名
    def current_phase_name(self) -> str:
        """現在フェーズ名"""
        if 0 <= self.current_phase < len(self.phases):
            return self.phases[self.current_phase]
        return "unknown"

    # PURPOSE: perigraphe_engine の is complete 処理を実行する
    @property
    # PURPOSE: 軌道完了か
    def is_complete(self) -> bool:
        """軌道完了か"""
        if self.max_iterations is None:
# PURPOSE: P3 Trokhia: 軌道を定義
            return False
        return self.iteration > self.max_iterations


# PURPOSE: perigraphe_engine の define trajectory 処理を実行する
def define_trajectory(
    trajectory_name: str,
    phases: List[str],
    derivative: Optional[TrokhiaDerivative] = None,
    max_iterations: Optional[int] = None,
) -> TrokhiaResult:
    """P3 Trokhia: 軌道を定義

    Args:
        trajectory_name: 軌道名
        phases: フェーズリスト
        derivative: 派生モード
        max_iterations: 最大イテレーション

    Returns:
        TrokhiaResult
    """
    if derivative is None:
        if max_iterations is None:
            derivative = TrokhiaDerivative.CYCLE
        else:
            derivative = TrokhiaDerivative.SPIRAL

    return TrokhiaResult(
        trajectory_name=trajectory_name,
        derivative=derivative,
        phases=phases,
        max_iterations=max_iterations,
    )


# =============================================================================
# PURPOSE: P1 Khōra 結果をMarkdown形式でフォーマット
# Formatting
# =============================================================================


def format_khora_markdown(result: KhoraResult) -> str:
    """P1 Khōra 結果をMarkdown形式でフォーマット"""
    lines = [
        "┌─[P1 Khōra 条件空間定義]───────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 対象: {result.target[:40]}",
        f"│ スコープ: {result.scope_label}",
        f"│ 境界: {', '.join(result.boundaries)}",
    ]
    if result.included:
        lines.append(f"│ 含む: {', '.join(result.included[:3])}")
    if result.excluded:
        lines.append(f"│ 除外: {', '.join(result.excluded[:3])}")
# PURPOSE: P2 Hodos 結果をMarkdown形式でフォーマット
    lines.append("└──────────────────────────────────────────────────┘")
    return "\n".join(lines)


# PURPOSE: hodos markdown を整形する
def format_hodos_markdown(result: HodosResult) -> str:
    """P2 Hodos 結果をMarkdown形式でフォーマット"""
    path_str = f"{result.start}"
    for wp in result.waypoints:
        path_str += f" → {wp}"
    path_str += f" → {result.end}"

    lines = [
        "┌─[P2 Hodos 経路定義]───────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 経路: {result.path_name}",
        f"│ {path_str}",
        f"│ ステップ: {result.estimated_steps}",
        "└──────────────────────────────────────────────────┘",
# PURPOSE: P3 Trokhia 結果をMarkdown形式でフォーマット
    ]
    return "\n".join(lines)


# PURPOSE: trokhia markdown を整形する
def format_trokhia_markdown(result: TrokhiaResult) -> str:
    """P3 Trokhia 結果をMarkdown形式でフォーマット"""
    phase_str = " → ".join(result.phases)
    iter_str = (
        f"{result.iteration}"
        if result.max_iterations is None
        else f"{result.iteration}/{result.max_iterations}"
    )

    lines = [
        "┌─[P3 Trokhia 軌道定義]──────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 軌道: {result.trajectory_name}",
        f"│ {phase_str}",
        f"│ 現在: {result.current_phase_name} (iter {iter_str})",
        "└──────────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)


# =============================================================================
# PURPOSE: FEP観察空間へのエンコード
# FEP Integration
# =============================================================================


def encode_perigraphe_observation(
    khora: Optional[KhoraResult] = None,
    hodos: Optional[HodosResult] = None,
    trokhia: Optional[TrokhiaResult] = None,
) -> dict:
    """FEP観察空間へのエンコード

    P-series の環境定義を FEP agent の観察形式に変換。

    Returns:
        dict with context_clarity, urgency, confidence
    """
    context_clarity = 0.5
    urgency = 0.3
    confidence = 0.5

    # Khōra: スコープ定義 → context_clarity
    if khora:
        scale_factor = {
            (ScopeScale.MICRO, ScopeScale.MICRO): 0.9,
            (ScopeScale.MICRO, ScopeScale.MACRO): 0.7,
            (ScopeScale.MACRO, ScopeScale.MICRO): 0.7,
            (ScopeScale.MACRO, ScopeScale.MACRO): 0.5,
        }
        context_clarity = scale_factor.get((khora.x_scale, khora.y_scale), 0.6)

    # Hodos: 経路定義 → urgency
    if hodos:
        # 長い経路 → 低urgency (余裕がある)
        urgency = max(0.1, 1.0 - (hodos.estimated_steps * 0.1))

    # Trokhia: 軌道定義 → confidence
    if trokhia:
        if trokhia.is_complete:
            confidence = 0.9
        elif trokhia.max_iterations:
            progress = trokhia.iteration / trokhia.max_iterations
            confidence = 0.4 + (progress * 0.5)
        else:
            confidence = 0.5

    return {
        "context_clarity": context_clarity,
        "urgency": urgency,
        "confidence": confidence,
    }
