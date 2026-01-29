"""
O3 Zētēsis Inquirer — 探求・問い発見モジュール

Hegemonikón O-series (Ousia) 定理: O3 Zētēsis
FEP層での問いの発見と探索的思考を担当。

Architecture:
- O3 Zētēsis = 「何を問うべきか」の発見
- 派生: deep (深層探求), wide (広域探索), pivot (転換)

References:
- /zet ワークフロー
- FEP: 探求 = 能動推論による仮説生成
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ZetesisDerivative(Enum):
    """O3 Zētēsis の派生モード"""
    DEEP = "deep"     # 深層探求 (Five Whys)
    WIDE = "wide"     # 広域探索 (横展開)
    PIVOT = "pivot"   # 転換 (前提破壊)


class QuestionType(Enum):
    """問いの種類"""
    WHAT = "what"       # 何？
    WHY = "why"         # なぜ？
    HOW = "how"         # どうやって？
    WHEN = "when"       # いつ？
    WHO = "who"         # 誰？
    WHERE = "where"     # どこ？
    WHICH = "which"     # どれ？
    IF = "if"           # もし〜なら？


@dataclass
class ZetesisResult:
    """O3 Zētēsis 探求結果
    
    Attributes:
        topic: 探求対象
        derivative: 派生モード
        seed_question: 種となる問い
        generated_questions: 生成された問い
        depth: 探求深度
        insights: 発見した洞察
    """
    topic: str
    derivative: ZetesisDerivative
    seed_question: str
    generated_questions: List[str]
    depth: int
    insights: List[str] = field(default_factory=list)
    
    @property
    def question_count(self) -> int:
        """生成した問いの数"""
        return len(self.generated_questions)
    
    @property
    def has_insight(self) -> bool:
        """洞察があるか"""
        return len(self.insights) > 0


def _generate_five_whys(topic: str, seed: str) -> List[str]:
    """Five Whysパターンで問いを生成"""
    return [
        f"なぜ{seed}？",
        f"その原因は何か？",
        f"その原因の原因は？",
        f"根本的な要因は？",
        f"どうすれば根本解決できるか？",
    ]


def _generate_wide_questions(topic: str, seed: str) -> List[str]:
    """広域探索パターンで問いを生成"""
    return [
        f"{topic}の他の側面は？",
        f"類似の問題は？",
        f"反対の視点からは？",
        f"異なる分野での解決策は？",
        f"ステークホルダー全員の視点は？",
    ]


def _generate_pivot_questions(topic: str, seed: str) -> List[str]:
    """転換パターンで問いを生成"""
    return [
        f"前提が間違っているとしたら？",
        f"問題自体を消す方法は？",
        f"逆の結果が正解だとしたら？",
        f"10倍のリソースがあったら？",
        f"10分の1のリソースしかなかったら？",
    ]


def inquire(
    topic: str,
    seed_question: Optional[str] = None,
    derivative: Optional[ZetesisDerivative] = None,
    depth: int = 3,
) -> ZetesisResult:
    """O3 Zētēsis: 探求を実行
    
    Args:
        topic: 探求対象
        seed_question: 種となる問い (None で自動生成)
        derivative: 派生モード (None で自動推論)
        depth: 探求深度
        
    Returns:
        ZetesisResult
    """
    seed = seed_question or f"{topic}とは何か？"
    
    # 派生自動推論
    if derivative is None:
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ['なぜ', '原因', 'why', 'root']):
            derivative = ZetesisDerivative.DEEP
        elif any(w in topic_lower for w in ['他', '代替', 'alternative', 'other']):
            derivative = ZetesisDerivative.WIDE
        elif any(w in topic_lower for w in ['前提', '仮定', 'assumption', 'if']):
            derivative = ZetesisDerivative.PIVOT
        else:
            derivative = ZetesisDerivative.DEEP
    
    # 問い生成
    if derivative == ZetesisDerivative.DEEP:
        questions = _generate_five_whys(topic, seed)[:depth]
    elif derivative == ZetesisDerivative.WIDE:
        questions = _generate_wide_questions(topic, seed)[:depth]
    else:
        questions = _generate_pivot_questions(topic, seed)[:depth]
    
    # 洞察抽出 (簡略版)
    insights = []
    if len(questions) >= 3:
        insights.append(f"{topic}について{len(questions)}つの問いを発見")
    
    return ZetesisResult(
        topic=topic,
        derivative=derivative,
        seed_question=seed,
        generated_questions=questions,
        depth=depth,
        insights=insights,
    )


def format_zetesis_markdown(result: ZetesisResult) -> str:
    """O3 Zētēsis 結果をMarkdown形式でフォーマット"""
    lines = [
        "┌─[O3 Zētēsis 探求]──────────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 対象: {result.topic[:40]}",
        f"│ 種: {result.seed_question[:40]}",
        "│ 生成された問い:",
    ]
    for i, q in enumerate(result.generated_questions[:5], 1):
        lines.append(f"│   {i}. {q[:40]}")
    if result.insights:
        lines.append("│ 洞察:")
        for insight in result.insights[:3]:
            lines.append(f"│   • {insight[:40]}")
    lines.append("└──────────────────────────────────────────────────┘")
    return "\n".join(lines)


def encode_zetesis_observation(result: ZetesisResult) -> dict:
    """FEP観察空間へのエンコード"""
    # 深度 → confidence
    confidence = min(1.0, result.depth * 0.2)
    
    # 問いの数 → context_clarity
    context_clarity = min(1.0, result.question_count * 0.15)
    
    # 派生 → urgency
    urgency_map = {
        ZetesisDerivative.DEEP: 0.5,
        ZetesisDerivative.WIDE: 0.3,
        ZetesisDerivative.PIVOT: 0.7,
    }
    urgency = urgency_map[result.derivative]
    
    return {
        "context_clarity": context_clarity,
        "urgency": urgency,
        "confidence": confidence,
    }
