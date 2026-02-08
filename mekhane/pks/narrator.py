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
import os
import re

from mekhane.pks.pks_engine import KnowledgeNugget


@dataclass
# PURPOSE: 対話の一セグメント
class NarrativeSegment:
    """対話の一セグメント"""

    speaker: str  # "Advocate" or "Critic"
    content: str


@dataclass
# PURPOSE: Advocate vs Critic の対話形式サマリー
class Narrative:
    """Advocate vs Critic の対話形式サマリー"""

    title: str
    segments: list[NarrativeSegment]
    source_nugget: Optional[KnowledgeNugget] = None

    # PURPOSE: Markdown 対話形式に出力
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

# PURPOSE: NotebookLM Audio Overview 相当の「知識が語りかける」機構

class PKSNarrator:
    """NotebookLM Audio Overview 相当の「知識が語りかける」機構

    2 視点: Advocate (ベネフィット主張) vs Critic (限界指摘)。

    Phase 1: テンプレートベースの簡易生成
    Phase 2: Gemini 経由の高品質対話生成 (フォールバック付き)
    """

    _LLM_PROMPT = (
        "以下の知識について、Advocate（推薦者）と Critic（批判者）の対話を生成してください。\n\n"
        "タイトル: {title}\n"
        "要約: {abstract}\n"
        "ソース: {source}\n"
        "関連度: {score}\n\n"
        "出力形式 (厳密に守ってください):\n"
        "ADVOCATE: (この知識の価値と応用可能性を具体的に主張)\n"
        "CRITIC: (限界、注意点、前提条件を指摘)\n"
        "ADVOCATE: (批判に応答し、最終的な推薦を述べる)\n\n"
        "各発言は1-2文で簡潔に。日本語で。"
    )

    # PURPOSE: PKSNarrator の初期化
    def __init__(self, use_llm: bool = True, model: str = "gemini-2.0-flash"):
        self._client = None
        self._model = model
        if use_llm:
            self._init_client()

    def _init_client(self) -> None:
        """Gemini クライアントを初期化"""
        try:
            from google import genai
            api_key = (
                os.environ.get("GOOGLE_API_KEY")
                or os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GOOGLE_GENAI_API_KEY")
            )
            self._client = genai.Client(api_key=api_key) if api_key else genai.Client()
        except (ImportError, Exception):
            self._client = None

    # PURPOSE: llm_available の処理
    @property
    def llm_available(self) -> bool:
        return self._client is not None

    # PURPOSE: KnowledgeNugget を対話形式に変換
    def narrate(self, nugget: KnowledgeNugget) -> Narrative:
        """KnowledgeNugget を対話形式に変換

        LLM 可用時: Gemini で動的生成
        LLM 不可時: テンプレートフォールバック
        """
        if self.llm_available:
            narrative = self._narrate_llm(nugget)
            if narrative:
                return narrative

        return self._narrate_template(nugget)

    # PURPOSE: LLM 経由の対話生成
    def _narrate_llm(self, nugget: KnowledgeNugget) -> Optional[Narrative]:
        """Gemini で Advocate/Critic 対話を生成"""
        prompt = self._LLM_PROMPT.format(
            title=nugget.title,
            abstract=nugget.abstract[:500] if nugget.abstract else "(なし)",
            source=nugget.source,
            score=f"{nugget.relevance_score:.2f}",
        )

        try:
            response = self._client.models.generate_content(
                model=self._model, contents=prompt
            )
            text = response.text if response else ""
            if text:
                return self._parse_llm_response(text, nugget)
        except Exception as e:
            print(f"[Narrator] LLM error: {e}")

        return None

    # PURPOSE: LLM 応答をパース
    def _parse_llm_response(
        self, text: str, nugget: KnowledgeNugget
    ) -> Optional[Narrative]:
        """「ADVOCATE: ...」CRITIC: ...」形式をパース"""
        segments = []
        pattern = re.compile(
            r"(ADVOCATE|CRITIC):\s*(.+?)(?=(?:ADVOCATE|CRITIC):|$)",
            re.DOTALL,
        )
        matches = pattern.findall(text)

        for speaker_raw, content in matches:
            speaker = "Advocate" if speaker_raw == "ADVOCATE" else "Critic"
            content = content.strip()
            if content:
                segments.append(NarrativeSegment(speaker=speaker, content=content))

        if len(segments) >= 2:
            return Narrative(
                title=nugget.title,
                segments=segments,
                source_nugget=nugget,
            )

        return None  # パース失敗 → テンプレートフォールバック

    # PURPOSE: テンプレートベース生成 (Phase 1 フォールバック)
    def _narrate_template(self, nugget: KnowledgeNugget) -> Narrative:
        """テンプレートベースの対話生成 (Phase 1)"""
        segments = []
        segments.append(NarrativeSegment(speaker="Advocate", content=self._generate_advocate(nugget)))
        segments.append(NarrativeSegment(speaker="Critic", content=self._generate_critic(nugget)))
        segments.append(NarrativeSegment(speaker="Advocate", content=self._generate_response(nugget)))

        return Narrative(
            title=nugget.title,
            segments=segments,
            source_nugget=nugget,
        )

    # PURPOSE: 複数 nugget をバッチで対話化
    def narrate_batch(self, nuggets: list[KnowledgeNugget]) -> list[Narrative]:
        """複数 nugget をバッチで対話化"""
        return [self.narrate(n) for n in nuggets]

    # PURPOSE: ナラティブ群を一つのレポートに整形
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

    # PURPOSE: Advocate の発言を生成
    def _generate_advocate(self, nugget: KnowledgeNugget) -> str:
        """Advocate の発言を生成"""
        abstract = nugget.abstract[:200] if nugget.abstract else "（要約なし）"

        parts = [f"この研究は注目に値します。"]

        if nugget.push_reason:
            parts.append(f"{nugget.push_reason}。")

        parts.append(f"概要: {abstract}")

        return " ".join(parts)

    # PURPOSE: Critic の発言を生成
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

    # PURPOSE: Advocate の応答を生成
    def _generate_response(self, nugget: KnowledgeNugget) -> str:
        """Advocate の応答を生成"""
        return (
            "確かにその通りです。"
            "この知識は参考として提示しているものであり、"
            "最終的な判断は Creator に委ねます。"
            f"関連度 {nugget.relevance_score:.2f} は、"
            "少なくとも一読の価値があることを示しています。"
        )
