# PROOF: [L2/インフラ] <- hermeneus/src/ CCL AST 定義
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
    FUSE = auto()        # * 融合 (内積)
    OUTER = auto()       # % 外積 (テンソル展開)
    FUSE_OUTER = auto()  # *% 内積+外積
    OSC = auto()         # ~ 振動
    SEQ = auto()         # _ シーケンス
    COLIMIT = auto()     # \ Colimit (展開・発散)
    
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
    
    例: /noe+, /bou-, /s+a1:2, /noe.h, /bou.x
    """
    id: str                              # ワークフロー ID (e.g., "noe", "bou")
    operators: List[OpType] = field(default_factory=list)  # 適用された演算子
    modifiers: Dict[str, Any] = field(default_factory=dict)  # 修飾子 (e.g., {"a1": 2})
    mode: Optional[str] = None           # --mode 指定 (e.g., "nous")
    selector: Optional[str] = None       # [target] セレクタ
    relation: Optional[str] = None       # .d/.h/.x 関係サフィックス (v7.2)


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
    """融合: A * B, A % B (外積), A *% B (内積+外積)
    
    例: /noe * /dia, /noe % /dia, /noe+*%/dia+
    
    Markov圏対応:
        * = inner product (⟨−,−⟩)
        % = outer product (⊗ tensor expansion, copy morphism)
        *% = inner+outer product (収束+展開の同時操作)
    """
    left: Any
    right: Any
    meta_display: bool = False           # *^ のメタ表示フラグ
    outer_product: bool = False          # % の外積フラグ
    fuse_outer: bool = False             # *% の内積+外積フラグ


@dataclass
class Oscillation:
    """振動: A ~ B, A ~* B (収束), A ~! B (発散)
    
    例: /u+ ~ /noe!, /dia+~*/noe (収束振動)
    """
    left: Any
    right: Any
    convergent: bool = False              # ~* 収束振動
    divergent: bool = False               # ~! 発散振動
    max_iterations: int = 5               # 収束時の最大反復回数


@dataclass
class ColimitExpansion:
    """Colimit 展開: \\A
    
    例: \\pan+ (pan の全派生展開)
    圏論的意味: Colimit = 余極限 = 全射影の合併
    """
    body: Any                              # 展開対象の WF/Expression
    operators: List[OpType] = field(default_factory=list)  # 追加演算子


@dataclass
class Pipeline:
    """パイプライン: A |> B |> C
    
    例: /noe+ |> /dia+ (前段の出力を次段の入力に)
    """
    steps: List[Any] = field(default_factory=list)


@dataclass
class Parallel:
    """並列実行: A || B || C
    
    例: /noe+ || /dia+ (同時並行で実行)
    """
    branches: List[Any] = field(default_factory=list)


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


@dataclass
class TaggedBlock:
    """タグ付きブロック: V:{body}, C:{body}, R:{body}, M:{body}
    
    CPL v2.0 意味タグ。制御フローではなく意図を示す。
    
    Tags:
        V = Validate (検証)
        C = Cycle (反復サイクル)
        R = Repeat (反復)
        M = Memorize (記憶・永続化)
    
    例: V:{/dia+}, C:{/dia+_/ene+}, M:{/dox-}
    """
    tag: str      # "V", "C", "R", "M"
    body: Any     # 内部の CCL 式


# =============================================================================
# AST Node: Program (Root)
# =============================================================================

@dataclass
class Program:
    """CCL プログラム (ルートノード)"""
    expressions: List[Any] = field(default_factory=list)
    macros: Dict[str, Any] = field(default_factory=dict)  # let 定義


@dataclass
class LetBinding:
    """マクロ定義: let @name = CCL 式
    
    例: let @think = /noe+ _ /dia
    """
    name: str                            # マクロ名 (@ なし)
    body: Any                            # 束縛される CCL 式


# =============================================================================
# Type Aliases
# =============================================================================

ASTNode = Union[
    Workflow, Condition, MacroRef,
    ConvergenceLoop, Sequence, Fusion, Oscillation, ColimitExpansion,
    Pipeline, Parallel,
    ForLoop, IfCondition, WhileLoop, Lambda, TaggedBlock,
    LetBinding, Program
]
