# PROOF: [L1/定理]
"""
PROOF: [L1/定理] このファイルは存在しなければならない

A0 → 認知には精度評価 (Akribeia) が必要
   → A1 感情, A3 原則, A4 知識を評価
   → akribeia_evaluator が担う

Q.E.D.

---

A-series Akribeia Evaluator — 精度評価モジュール

Hegemonikón A-series (Akribeia) 定理: A1 Pathos, A3 Gnōmē, A4 Epistēmē
FEP層での感情・原則・知識の評価を担当。
(A2 Krisis は ergasterion/synedrion として判定層で分離済み)

Architecture:
- A1 Pathos = メタ感情評価 (emot/cogn/soma)
- A3 Gnōmē = 格言・原則抽出 (univ/doma/prag)
- A4 Epistēmē = 知識確立評価 (just/true/beli)

References:
- /pat, /gno, /epi ワークフロー
- FEP: 精度 = 信念の解像度と確からしさ
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# =============================================================================
# A1 Pathos (メタ感情)
# =============================================================================

class PathosDerivative(Enum):
    """A1 Pathos の派生モード"""
    EMOTIONAL = "emot"    # 情動的 (感情そのもの)
    COGNITIVE = "cogn"    # 認知的 (感情についての思考)
    SOMATIC = "soma"      # 身体的 (感情の身体反応)


@dataclass
class PathosResult:
    """A1 Pathos 評価結果
    
    Attributes:
        experience: 経験・状況
        derivative: 派生モード
        primary_emotion: 一次感情
        meta_emotion: 二次感情 (一次への反応)
        intensity: 強度 (0.0-1.0)
        regulation_need: 調整必要度 (0.0-1.0)
    """
    experience: str
    derivative: PathosDerivative
    primary_emotion: str
    meta_emotion: str
    intensity: float
    regulation_need: float
    
    @property
    def needs_regulation(self) -> bool:
        """調整が必要か"""
        return self.regulation_need >= 0.6


def evaluate_pathos(
    experience: str,
    primary_emotion: Optional[str] = None,
    meta_emotion: Optional[str] = None,
) -> PathosResult:
    """A1 Pathos: メタ感情を評価
    
    Args:
        experience: 経験・状況
        primary_emotion: 一次感情
        meta_emotion: 二次感情
        
    Returns:
        PathosResult
    """
    exp_lower = experience.lower()
    
    # キーワードベースの派生推論
    if any(w in exp_lower for w in ['体', '身体', '緊張', '心拍', 'body', 'tension']):
        derivative = PathosDerivative.SOMATIC
    elif any(w in exp_lower for w in ['考え', '思考', '分析', 'think', 'analyze']):
        derivative = PathosDerivative.COGNITIVE
    else:
        derivative = PathosDerivative.EMOTIONAL
    
    # 感情推論
    primary = primary_emotion or "不明"
    meta = meta_emotion or f"{primary}に対する自覚"
    
    # 強度と調整必要度
    negative_keywords = ['不安', '怒り', '悲しみ', '恐れ', 'anxiety', 'anger', 'fear']
    if any(w in exp_lower for w in negative_keywords):
        intensity = 0.7
        regulation_need = 0.6
    else:
        intensity = 0.4
        regulation_need = 0.2
    
    return PathosResult(
        experience=experience,
        derivative=derivative,
        primary_emotion=primary,
        meta_emotion=meta,
        intensity=intensity,
        regulation_need=regulation_need,
    )


# =============================================================================
# A3 Gnōmē (格言・原則)
# =============================================================================

class GnomeDerivative(Enum):
    """A3 Gnōmē の派生モード"""
    UNIVERSAL = "univ"    # 普遍的原則
    DOMAIN = "doma"       # 領域固有原則
    PRAGMATIC = "prag"    # 実用的原則


@dataclass
class GnomeResult:
    """A3 Gnōmē 評価結果
    
    Attributes:
        source: 原則の出所・文脈
        derivative: 派生モード
        principle: 抽出された原則
        applicability: 適用可能性 (0.0-1.0)
        generalizability: 一般化可能性 (0.0-1.0)
        examples: 適用例
    """
    source: str
    derivative: GnomeDerivative
    principle: str
    applicability: float
    generalizability: float
    examples: List[str] = field(default_factory=list)
    
    @property
    def is_actionable(self) -> bool:
        """行動可能な原則か"""
        return self.applicability >= 0.6


def extract_gnome(
    source: str,
    context: Optional[str] = None,
) -> GnomeResult:
    """A3 Gnōmē: 原則を抽出
    
    Args:
        source: 原則の出所・経験
        context: 文脈
        
    Returns:
        GnomeResult
    """
    src_lower = source.lower()
    ctx_lower = (context or "").lower()
    combined = src_lower + " " + ctx_lower
    
    # 派生推論
    if any(w in combined for w in ['常に', '普遍', 'never', 'always', '必ず']):
        derivative = GnomeDerivative.UNIVERSAL
        generalizability = 0.9
    elif any(w in combined for w in ['この場合', '特定の', 'specifically', 'in this case']):
        derivative = GnomeDerivative.DOMAIN
        generalizability = 0.5
    else:
        derivative = GnomeDerivative.PRAGMATIC
        generalizability = 0.7
    
    # 原則生成 (簡略版)
    principle = f"{source[:50]}から導かれる教訓"
    
    return GnomeResult(
        source=source,
        derivative=derivative,
        principle=principle,
        applicability=0.7,
        generalizability=generalizability,
        examples=[],
    )


# =============================================================================
# A4 Epistēmē (知識確立)
# =============================================================================

class EpistemeDerivative(Enum):
    """A4 Epistēmē の派生モード (JTB条件)"""
    JUSTIFIED = "just"    # 正当化された
    TRUE = "true"         # 真である
    BELIEVED = "beli"     # 信じられている


@dataclass
class EpistemeResult:
    """A4 Epistēmē 評価結果
    
    Attributes:
        proposition: 命題
        derivative: 評価の焦点
        is_justified: 正当化されているか
        is_true: 真であるか (検証可能な範囲で)
        is_believed: 信じられているか
        jtb_score: JTB総合スコア (0.0-1.0)
        status: 知識ステータス
    """
    proposition: str
    derivative: EpistemeDerivative
    is_justified: bool
    is_true: Optional[bool]  # None = 検証不能
    is_believed: bool
    jtb_score: float
    status: str
    
    @property
    def is_knowledge(self) -> bool:
        """知識として成立するか (JTB条件)"""
        return self.is_justified and (self.is_true is True) and self.is_believed


def evaluate_episteme(
    proposition: str,
    justification: Optional[str] = None,
    evidence: Optional[List[str]] = None,
    believed: bool = True,
) -> EpistemeResult:
    """A4 Epistēmē: 知識を評価
    
    Args:
        proposition: 命題
        justification: 正当化根拠
        evidence: 証拠リスト
        believed: 信じられているか
        
    Returns:
        EpistemeResult
    """
    ev = evidence or []
    
    # 正当化評価
    is_justified = justification is not None or len(ev) > 0
    
    # 真理評価 (証拠ベース)
    if len(ev) >= 3:
        is_true = True
        derivative = EpistemeDerivative.TRUE
    elif len(ev) >= 1:
        is_true = None  # 検証中
        derivative = EpistemeDerivative.JUSTIFIED
    else:
        is_true = None
        derivative = EpistemeDerivative.BELIEVED
    
    # JTBスコア計算
    j_score = 1.0 if is_justified else 0.0
    t_score = 1.0 if is_true else (0.5 if is_true is None else 0.0)
    b_score = 1.0 if believed else 0.0
    jtb_score = (j_score + t_score + b_score) / 3
    
    # ステータス
    if is_justified and is_true and believed:
        status = "✅ 知識として確立"
    elif is_justified and believed:
        status = "🔄 正当化された信念（真理検証中）"
    elif believed:
        status = "⚠️ 単なる信念（正当化不足）"
    else:
        status = "❌ 疑念あり"
    
    return EpistemeResult(
        proposition=proposition,
        derivative=derivative,
        is_justified=is_justified,
        is_true=is_true,
        is_believed=believed,
        jtb_score=jtb_score,
        status=status,
    )


# =============================================================================
# Formatting
# =============================================================================

def format_pathos_markdown(result: PathosResult) -> str:
    """A1 Pathos 結果をMarkdown形式でフォーマット"""
    reg_emoji = "⚠️" if result.needs_regulation else "✅"
    lines = [
        "┌─[A1 Pathos メタ感情評価]────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 経験: {result.experience[:40]}",
        f"│ 一次感情: {result.primary_emotion}",
        f"│ 二次感情: {result.meta_emotion}",
        f"│ 強度: {result.intensity:.0%}",
        f"│ 調整: {reg_emoji} {result.regulation_need:.0%}",
        "└──────────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)


def format_gnome_markdown(result: GnomeResult) -> str:
    """A3 Gnōmē 結果をMarkdown形式でフォーマット"""
    lines = [
        "┌─[A3 Gnōmē 原則抽出]─────────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 出所: {result.source[:40]}",
        f"│ 原則: {result.principle[:40]}",
        f"│ 適用可能性: {result.applicability:.0%}",
        f"│ 一般化: {result.generalizability:.0%}",
        "└──────────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)


def format_episteme_markdown(result: EpistemeResult) -> str:
    """A4 Epistēmē 結果をMarkdown形式でフォーマット"""
    j_emoji = "✅" if result.is_justified else "❌"
    t_emoji = "✅" if result.is_true else ("🔄" if result.is_true is None else "❌")
    b_emoji = "✅" if result.is_believed else "❌"
    
    lines = [
        "┌─[A4 Epistēmē 知識評価]───────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 命題: {result.proposition[:40]}",
        f"│ J(正当化): {j_emoji} / T(真理): {t_emoji} / B(信念): {b_emoji}",
        f"│ JTBスコア: {result.jtb_score:.0%}",
        f"│ 状態: {result.status}",
        "└──────────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)


# =============================================================================
# FEP Integration
# =============================================================================

def encode_akribeia_observation(
    pathos: Optional[PathosResult] = None,
    gnome: Optional[GnomeResult] = None,
    episteme: Optional[EpistemeResult] = None,
) -> dict:
    """FEP観察空間へのエンコード
    
    A-series の精度評価を FEP agent の観察形式に変換。
    
    Returns:
        dict with context_clarity, urgency, confidence
    """
    context_clarity = 0.5
    urgency = 0.3
    confidence = 0.5
    
    # Pathos: メタ感情 → urgency (調整必要度と連動)
    if pathos:
        urgency = pathos.regulation_need
    
    # Gnōmē: 原則 → context_clarity (一般化可能性)
    if gnome:
        context_clarity = gnome.generalizability
    
    # Epistēmē: 知識 → confidence (JTBスコア)
    if episteme:
        confidence = episteme.jtb_score
    
    return {
        "context_clarity": context_clarity,
        "urgency": urgency,
        "confidence": confidence,
    }
