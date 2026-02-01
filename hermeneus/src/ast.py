# PROOF: [L2/インフラ] CCL AST 定義
"""
Hermēneus AST (Abstract Syntax Tree) Nodes

CCL 式を表現する抽象構文木のノード定義。
lmql_translator.py PoC から正式版へリファクタ。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Dict, Any, Union


# =============================================================================
# Operator Types
# =============================================================================

class OpType(Enum):
    """CCL 演算子タイプ (v6.50)"""
    # Tier 1: 単項演算子 (強度・次元)
    DEEPEN = auto()      # + 深化
    CONDENSE = auto()    # - 縮約
    ASCEND = auto()      # ^ 上昇 (メタ化)
    DESCEND = auto()     # √ 下降 (アクション)
    QUERY = auto()       # ? 質問
    INVERT = auto()      # \ 位相反転
    DIFF = auto()        # ' 微分 (変化率)
    EXPAND = auto()      # ! 全展開
    
    # Tier 2: 二項演算子 (合成)
    FUSE = auto()        # * 融合
    OSC = auto()         # ~ 振動
    SEQ = auto()         # _ シーケンス
    
    # Tier 3: 制御演算子
    CONVERGE = auto()    # >> or lim 収束
    PIPE = auto()        # |> パイプライン
    PARALLEL = auto()    # || 並列


# =============================================================================
# AST Nodes: Basic
# =============================================================================

@dataclass
class Workflow:
    """ワークフローノード
    
    例: /noe+, /bou-, /s+a1:2
    """
    id: str                              # ワークフロー ID (e.g., "noe", "bou")
    operators: List[OpType] = field(default_factory=list)  # 適用された演算子
    modifiers: Dict[str, Any] = field(default_factory=dict)  # 修飾子 (e.g., {"a1": 2})
    mode: Optional[str] = None           # --mode 指定 (e.g., "nous")
    selector: Optional[str] = None       # [target] セレクタ


@dataclass
class Condition:
    """条件ノード
    
    例: V[] < 0.3, E[] > 0.5
    """
    var: str      # 変数名 (e.g., "V[]", "E[]")
    op: str       # 比較演算子 (e.g., "<", ">", "=", "<=", ">=")
    value: float  # 閾値


@dataclass
class MacroRef:
    """マクロ参照ノード
    
    例: @think, @tak, @dig
    """
    name: str                            # マクロ名
    args: List[Any] = field(default_factory=list)  # 引数


# =============================================================================
# AST Nodes: Compound
# =============================================================================

@dataclass
class ConvergenceLoop:
    """収束ループ: A >> cond または lim[cond]{A}
    
    例: /noe+ >> V[] < 0.3
    """
    body: Any                            # Workflow or Expression
    condition: Condition                 # 収束条件
    max_iterations: int = 5              # 最大反復回数


@dataclass
class Sequence:
    """シーケンス: A _ B _ C
    
    例: /boot _/bou _/ene
    """
    steps: List[Any] = field(default_factory=list)


@dataclass
class Fusion:
    """融合: A * B
    
    例: /noe * /dia
    """
    left: Any
    right: Any
    meta_display: bool = False           # *^ のメタ表示フラグ


@dataclass
class Oscillation:
    """振動: A ~ B
    
    例: /u+ ~ /noe!
    """
    left: Any
    right: Any


# =============================================================================
# AST Nodes: CPL v2.0 Control Structures
# =============================================================================

@dataclass
class ForLoop:
    """FOR ループ: F:[×N]{body} または F:[A,B,C]{body}
    
    例: F:[×3]{/dia}
    """
    iterations: Union[int, List[Any]]    # 反復回数 or 対象リスト
    body: Any


@dataclass
class IfCondition:
    """IF 条件分岐: I:[cond]{then} E:{else}
    
    例: I:[V[] > 0.5]{/noe+} E:{/noe-}
    """
    condition: Condition
    then_branch: Any
    else_branch: Optional[Any] = None


@dataclass
class WhileLoop:
    """WHILE ループ: W:[cond]{body}
    
    例: W:[E[] > 0.3]{/dia}
    """
    condition: Condition
    body: Any


@dataclass
class Lambda:
    """Lambda 関数: L:[x]{body}
    
    例: L:[wf]{wf+}
    """
    params: List[str]
    body: Any


# =============================================================================
# AST Node: Program (Root)
# =============================================================================

@dataclass
class Program:
    """CCL プログラム (ルートノード)"""
    expressions: List[Any] = field(default_factory=list)
    macros: Dict[str, Any] = field(default_factory=dict)  # let 定義


# =============================================================================
# Type Aliases
# =============================================================================

ASTNode = Union[
    Workflow, Condition, MacroRef,
    ConvergenceLoop, Sequence, Fusion, Oscillation,
    ForLoop, IfCondition, WhileLoop, Lambda,
    Program
]
