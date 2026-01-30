"""
PROOF: このファイルは存在しなければならない

A0 → 認知には判定 (Krisis) がある
   → A2 で分析・統合・敵対的検証
   → krisis_judge が担う

Q.E.D.

---

A2 Krisis Judge — 判定・敵対的レビューモジュール

Hegemonikón A-series (Akribeia) 定理: A2 Krisis
FEP層での判定と敵対的検証を担当。

Architecture:
- A2 Krisis = 判定力 (anal/synt/advo)
- Devil's Advocate と Epochē (判断停止)

References:
- /dia, /epo ワークフロー
- FEP: 判定 = ベイズ的モデル比較
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class KrisisDerivative(Enum):
    """A2 Krisis の派生モード"""
    ANALYTIC = "anal"     # 分析的判定
    SYNTHETIC = "synt"    # 統合的判定
    ADVOCATE = "advo"     # 敵対的レビュー (Devil's Advocate)


class VerdictType(Enum):
    """判定タイプ"""
    APPROVE = "approve"     # 承認
    REJECT = "reject"       # 却下
    SUSPEND = "suspend"     # 保留 (Epochē)
    REVISE = "revise"       # 修正要求


@dataclass
class Objection:
    """異議オブジェクト
    
    Attributes:
        category: カテゴリ
        content: 内容
        severity: 深刻度 (0.0-1.0)
    """
    category: str
    content: str
    severity: float


@dataclass
class KrisisResult:
    """A2 Krisis 判定結果
    
    Attributes:
        subject: 判定対象
        derivative: 派生モード
        verdict: 判定
        confidence: 確信度
        objections: 異議リスト
        recommendation: 推奨事項
    """
    subject: str
    derivative: KrisisDerivative
    verdict: VerdictType
    confidence: float
    objections: List[Objection]
    recommendation: str
    
    @property
    def has_critical_objection(self) -> bool:
        """クリティカルな異議があるか"""
        return any(o.severity >= 0.8 for o in self.objections)
    
    @property
    def objection_count(self) -> int:
        """異議の数"""
        return len(self.objections)


def _generate_objections(subject: str) -> List[Objection]:
    """Devil's Advocate 異議を生成"""
    return [
        Objection("Feasibility", f"{subject}は本当に実現可能か？", 0.5),
        Objection("Necessity", f"{subject}は本当に必要か？", 0.4),
        Objection("Alternatives", f"より良い代替案はないか？", 0.3),
        Objection("Risks", "見落としているリスクは？", 0.6),
    ]


def judge(
    subject: str,
    derivative: Optional[KrisisDerivative] = None,
    evidence_for: Optional[List[str]] = None,
    evidence_against: Optional[List[str]] = None,
    devil_advocate: bool = False,
) -> KrisisResult:
    """A2 Krisis: 判定を実行
    
    Args:
        subject: 判定対象
        derivative: 派生モード
        evidence_for: 賛成根拠
        evidence_against: 反対根拠
        devil_advocate: 敵対的レビューを実行するか
        
    Returns:
        KrisisResult
    """
    ev_for = evidence_for or []
    ev_against = evidence_against or []
    
    # 派生決定
    if devil_advocate:
        derivative = KrisisDerivative.ADVOCATE
    elif derivative is None:
        if len(ev_for) > len(ev_against):
            derivative = KrisisDerivative.ANALYTIC
        else:
            derivative = KrisisDerivative.SYNTHETIC
    
    # 異議生成
    if derivative == KrisisDerivative.ADVOCATE:
        objections = _generate_objections(subject)
    else:
        objections = [Objection("General", o, 0.5) for o in ev_against[:3]]
    
    # 判定計算
    for_score = len(ev_for)
    against_score = len(ev_against) + sum(o.severity for o in objections)
    
    if against_score > for_score * 2:
        verdict = VerdictType.REJECT
        confidence = min(0.9, 0.5 + against_score * 0.1)
        recommendation = "却下 — 重大な問題あり"
    elif for_score > against_score * 2:
        verdict = VerdictType.APPROVE
        confidence = min(0.9, 0.5 + for_score * 0.1)
        recommendation = "承認 — 進行可能"
    elif any(o.severity >= 0.8 for o in objections):
        verdict = VerdictType.SUSPEND
        confidence = 0.5
        recommendation = "保留 (Epochē) — クリティカルな異議を解決してから再判定"
    else:
        verdict = VerdictType.REVISE
        confidence = 0.6
        recommendation = "修正要求 — 異議に対処してから再提出"
    
    return KrisisResult(
        subject=subject,
        derivative=derivative,
        verdict=verdict,
        confidence=confidence,
        objections=objections,
        recommendation=recommendation,
    )


def epochē(subject: str) -> KrisisResult:
    """A2 Krisis Epochē: 判断を停止
    
    過信を防ぐための明示的な判断保留。
    """
    return KrisisResult(
        subject=subject,
        derivative=KrisisDerivative.SYNTHETIC,
        verdict=VerdictType.SUSPEND,
        confidence=0.0,
        objections=[Objection("Epochē", "意図的な判断停止", 0.0)],
        recommendation="判断を保留し、追加情報を待つ",
    )


def format_krisis_markdown(result: KrisisResult) -> str:
    """A2 Krisis 結果をMarkdown形式でフォーマット"""
    verdict_emoji = {
        VerdictType.APPROVE: "✅",
        VerdictType.REJECT: "❌",
        VerdictType.SUSPEND: "⏸️",
        VerdictType.REVISE: "🔄",
    }
    lines = [
        "┌─[A2 Krisis 判定]──────────────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 対象: {result.subject[:40]}",
        f"│ 判定: {verdict_emoji[result.verdict]} {result.verdict.value.upper()}",
        f"│ 確信度: {result.confidence:.0%}",
        "│ 異議:",
    ]
    for o in result.objections[:3]:
        severity_emoji = "🔴" if o.severity >= 0.7 else ("🟡" if o.severity >= 0.4 else "🟢")
        lines.append(f"│   {severity_emoji} [{o.category}] {o.content[:30]}")
    lines.extend([
        f"│ 推奨: {result.recommendation}",
        "└──────────────────────────────────────────────────┘",
    ])
    return "\n".join(lines)


def encode_krisis_observation(result: KrisisResult) -> dict:
    """FEP観察空間へのエンコード"""
    # 判定 → confidence
    verdict_confidence = {
        VerdictType.APPROVE: 0.8,
        VerdictType.REJECT: 0.7,
        VerdictType.SUSPEND: 0.3,
        VerdictType.REVISE: 0.5,
    }
    confidence = verdict_confidence[result.verdict] * result.confidence
    
    # 異議の深刻度 → urgency
    if result.objections:
        urgency = max(o.severity for o in result.objections)
    else:
        urgency = 0.3
    
    # 異議の数 → context_clarity (多いほど低clarity)
    context_clarity = max(0.2, 1.0 - result.objection_count * 0.15)
    
    return {
        "context_clarity": context_clarity,
        "urgency": urgency,
        "confidence": confidence,
    }
