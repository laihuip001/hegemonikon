"""
PROOF: このファイルは存在しなければならない

A0 → 認知には知恵 (Sophia) がある
   → K4 で深層調査と知恵収集
   → sophia_researcher が担う

Q.E.D.

---

K4 Sophia Researcher — 知恵・深層調査モジュール

Hegemonikón K-series (Kairos) 定理: K4 Sophia
FEP層での深層調査と知恵の収集を担当。

Architecture:
- K4 Sophia = 知恵の収集 (acad/tech/soci)
- Perplexity/外部リソースへの調査依頼生成

References:
- /sop ワークフロー
- FEP: 知恵 = 高次の一般化能力
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class SophiaDerivative(Enum):
    """K4 Sophia の派生モード"""
    ACADEMIC = "acad"   # 学術的調査
    TECHNICAL = "tech"  # 技術的調査
    SOCIAL = "soci"     # 社会的調査


class ResearchDepth(Enum):
    """調査深度"""
    SURFACE = "surface"     # 表層 (概要のみ)
    STANDARD = "standard"   # 標準 (詳細)
    DEEP = "deep"           # 深層 (専門家レベル)


@dataclass
class ResearchQuery:
    """調査クエリ
    
    Attributes:
        topic: 調査トピック
        questions: 具体的な問い
        sources: 推奨ソース
        constraints: 制約 (期間、言語など)
    """
    topic: str
    questions: List[str]
    sources: List[str] = field(default_factory=list)
    constraints: Dict[str, str] = field(default_factory=dict)


@dataclass
class SophiaResult:
    """K4 Sophia 調査結果
    
    Attributes:
        topic: 調査トピック
        derivative: 派生モード
        depth: 調査深度
        query: 生成された調査クエリ
        estimated_time_minutes: 推定調査時間
    """
    topic: str
    derivative: SophiaDerivative
    depth: ResearchDepth
    query: ResearchQuery
    estimated_time_minutes: int


def research(
    topic: str,
    derivative: Optional[SophiaDerivative] = None,
    depth: ResearchDepth = ResearchDepth.STANDARD,
    specific_questions: Optional[List[str]] = None,
) -> SophiaResult:
    """K4 Sophia: 調査クエリを生成
    
    Args:
        topic: 調査トピック
        derivative: 派生モード
        depth: 調査深度
        specific_questions: 具体的な問い
        
    Returns:
        SophiaResult
    """
    topic_lower = topic.lower()
    
    # 派生自動推論
    if derivative is None:
        if any(w in topic_lower for w in ['論文', '研究', 'paper', 'research', 'study']):
            derivative = SophiaDerivative.ACADEMIC
        elif any(w in topic_lower for w in ['実装', 'api', 'ライブラリ', 'framework']):
            derivative = SophiaDerivative.TECHNICAL
        else:
            derivative = SophiaDerivative.SOCIAL
    
    # ソース推奨
    sources_map = {
        SophiaDerivative.ACADEMIC: ["arXiv", "Google Scholar", "Semantic Scholar"],
        SophiaDerivative.TECHNICAL: ["GitHub", "Stack Overflow", "Official Docs"],
        SophiaDerivative.SOCIAL: ["X/Twitter", "Reddit", "HackerNews"],
    }
    
    # 問い生成
    if specific_questions:
        questions = specific_questions
    else:
        questions = [
            f"{topic}とは何か？",
            f"{topic}の最新動向は？",
            f"{topic}のベストプラクティスは？",
        ]
    
    # 推定時間
    time_map = {
        ResearchDepth.SURFACE: 15,
        ResearchDepth.STANDARD: 30,
        ResearchDepth.DEEP: 60,
    }
    
    query = ResearchQuery(
        topic=topic,
        questions=questions,
        sources=sources_map[derivative],
        constraints={"depth": depth.value},
    )
    
    return SophiaResult(
        topic=topic,
        derivative=derivative,
        depth=depth,
        query=query,
        estimated_time_minutes=time_map[depth],
    )


def format_sophia_markdown(result: SophiaResult) -> str:
    """K4 Sophia 結果をMarkdown形式でフォーマット"""
    lines = [
        "┌─[K4 Sophia 調査依頼]─────────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ トピック: {result.topic[:40]}",
        f"│ 深度: {result.depth.value}",
        "│ 問い:",
    ]
    for q in result.query.questions[:3]:
        lines.append(f"│   • {q[:40]}")
    lines.extend([
        f"│ ソース: {', '.join(result.query.sources[:3])}",
        f"│ 推定時間: {result.estimated_time_minutes}分",
        "└──────────────────────────────────────────────────┘",
    ])
    return "\n".join(lines)


def encode_sophia_observation(result: SophiaResult) -> dict:
    """FEP観察空間へのエンコード"""
    # 深度 → confidence
    depth_map = {
        ResearchDepth.SURFACE: 0.4,
        ResearchDepth.STANDARD: 0.6,
        ResearchDepth.DEEP: 0.8,
    }
    confidence = depth_map[result.depth]
    
    # 問いの数 → context_clarity
    context_clarity = min(1.0, len(result.query.questions) * 0.2)
    
    # 調査時間 → urgency (長い調査は低urgency)
    urgency = max(0.1, 1.0 - result.estimated_time_minutes * 0.01)
    
    return {
        "context_clarity": context_clarity,
        "urgency": urgency,
        "confidence": confidence,
    }
