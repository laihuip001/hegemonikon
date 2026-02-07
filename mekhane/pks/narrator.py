# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/pks/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 知識の能動的表面化には多視点の対話的解説が必要
→ NotebookLM Audio Overview のテキスト版
→ narrator.py が担う

# PURPOSE: 知識を Advocate vs Critic の対話形式で表面化する
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mekhane.pks.pks_engine import KnowledgeNugget


@dataclass
class NarrativeSegment:
    """対話の一セグメント"""

    speaker: str  # "Advocate" or "Critic"
    content: str


@dataclass
class Narrative:
    """Advocate vs Critic の対話形式サマリー"""

    title: str
    segments: list[NarrativeSegment]
    source_nugget: Optional[KnowledgeNugget] = None

    def to_markdown(self) -> str:
        """Markdown 対話形式に出力"""
        lines = [
            f"## 🎙️ PKS Narrative: {self.title}",
            "",
        ]

        if self.source_nugget and self.source_nugget.url:
            lines.append(f"*Source: [{self.source_nugget.source}]({self.source_nugget.url})*")
            lines.append("")

        for seg in self.segments:
            icon = "🟢" if seg.speaker == "Advocate" else "🔴"
            lines.append(f"**{icon} {seg.speaker}**: {seg.content}")
            lines.append("")

        return "\n".join(lines)


class PKSNarrator:
    """NotebookLM Audio Overview 相当の「知識が語りかける」機構

    テキスト Markdown ベースの対話形式サマリーを生成する。
    2 視点: Advocate (ベネフィット主張) vs Critic (限界指摘)。

    Note:
        LLM 統合は Phase 2 で実装。
        現時点ではテンプレートベースの簡易生成。
    """

    def narrate(self, nugget: KnowledgeNugget) -> Narrative:
        """KnowledgeNugget を対話形式に変換

        Phase 1: テンプレートベースの簡易生成
        Phase 2: LLM 経由の高品質対話生成
        """
        segments = []

        # Advocate: ベネフィットを主張
        advocate_text = self._generate_advocate(nugget)
        segments.append(NarrativeSegment(speaker="Advocate", content=advocate_text))

        # Critic: 限界と注意点を指摘
        critic_text = self._generate_critic(nugget)
        segments.append(NarrativeSegment(speaker="Critic", content=critic_text))

        # Advocate: 応答
        response_text = self._generate_response(nugget)
        segments.append(NarrativeSegment(speaker="Advocate", content=response_text))

        return Narrative(
            title=nugget.title,
            segments=segments,
            source_nugget=nugget,
        )

    def narrate_batch(self, nuggets: list[KnowledgeNugget]) -> list[Narrative]:
        """複数 nugget をバッチで対話化"""
        return [self.narrate(n) for n in nuggets]

    def format_report(self, narratives: list[Narrative]) -> str:
        """ナラティブ群を一つのレポートに整形"""
        if not narratives:
            return "📭 ナラティブ対象なし"

        lines = [
            "# 🎙️ PKS Narrative Report",
            "",
            f"_生成数: {len(narratives)} 件_",
            "",
            "---",
        ]

        for narrative in narratives:
            lines.append("")
            lines.append(narrative.to_markdown())
            lines.append("---")

        return "\n".join(lines)

    # --- Phase 1: テンプレートベース生成 ---

    def _generate_advocate(self, nugget: KnowledgeNugget) -> str:
        """Advocate の発言を生成"""
        abstract = nugget.abstract[:200] if nugget.abstract else "（要約なし）"

        parts = [f"この研究は注目に値します。"]

        if nugget.push_reason:
            parts.append(f"{nugget.push_reason}。")

        parts.append(f"概要: {abstract}")

        return " ".join(parts)

    def _generate_critic(self, nugget: KnowledgeNugget) -> str:
        """Critic の発言を生成"""
        parts = ["ただし注意が必要です。"]

        if nugget.relevance_score < 0.8:
            parts.append(
                f"関連度スコアは {nugget.relevance_score:.2f} で、"
                "確定的な関連性とは言えません。"
            )

        parts.append("実際のコンテキストとの適合性は人間の判断が必要です。")

        if nugget.source in ("arxiv", "semantic_scholar"):
            parts.append("プレプリントの場合、査読状況も確認すべきです。")

        return " ".join(parts)

    def _generate_response(self, nugget: KnowledgeNugget) -> str:
        """Advocate の応答を生成"""
        return (
            "確かにその通りです。"
            "この知識は参考として提示しているものであり、"
            "最終的な判断は Creator に委ねます。"
            f"関連度 {nugget.relevance_score:.2f} は、"
            "少なくとも一読の価値があることを示しています。"
        )
