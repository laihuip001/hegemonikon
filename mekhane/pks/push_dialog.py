#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/pks/
# PURPOSE: Push された知識への対話インターフェース
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 能動的推論 = 受身のプッシュではなく対話的探求
→ Creator が「なぜ？」「もっと」「関連は？」と問える
→ push_dialog.py が担う

# PURPOSE: PushDialog — 推薦知識への対話的アクセス
"""

from __future__ import annotations

from typing import Callable, Optional

from mekhane.pks.llm_client import PKSLLMClient
from mekhane.pks.pks_engine import KnowledgeNugget


# PURPOSE: Push された知識への対話インターフェース
class PushDialog:
    """Push された知識への対話インターフェース

    Creator が push された nugget に対して:
    - why():     なぜ推薦されたか
    - deeper():  追加質問 (LLM 生成)
    - related(): 関連知識の検索

    Usage:
        dialog = PushDialog()
        print(dialog.why(nugget))
        print(dialog.deeper(nugget, "実装の困難さは？"))
    """

    _WHY_PROMPT = (
        "以下の知識が推薦された理由を簡潔に説明してください。\n\n"
        "タイトル: {title}\n"
        "要約: {abstract}\n"
        "ソース: {source}\n"
        "関連度スコア: {score}\n"
        "推薦理由(システム): {push_reason}\n\n"
        "ユーザーにとってなぜ有用かを2-3文で説明。日本語で。"
    )

    _DEEPER_PROMPT = (
        "以下の知識について質問に回答してください。\n\n"
        "タイトル: {title}\n"
        "要約: {abstract}\n"
        "ソース: {source}\n\n"
        "質問: {question}\n\n"
        "簡潔に回答。不確実な場合は明示。日本語で。"
    )

    # PURPOSE: PushDialog の初期化
    def __init__(
        self,
        use_llm: bool = True,
        model: str = "gemini-2.0-flash",
        on_feedback: Optional[Callable[[str, str, str], None]] = None,
    ):
        self._llm = PKSLLMClient(model=model, enabled=use_llm)
        self._on_feedback = on_feedback

    # PURPOSE: なぜこの知識が push されたか説明
    def why(self, nugget: KnowledgeNugget) -> str:
        """なぜこの知識が push されたか説明

        LLM 可用時: Gemini で自然言語説明を生成
        LLM 不可時: メタデータベースの定型説明
        """
        if self._llm.available:
            prompt = self._WHY_PROMPT.format(
                title=nugget.title,
                abstract=nugget.abstract[:500] if nugget.abstract else "(なし)",
                source=nugget.source,
                score=f"{nugget.relevance_score:.2f}",
                push_reason=nugget.push_reason or "(自動推薦)",
            )
            result = self._llm.generate(prompt)
            if result:
                return result

        # テンプレートフォールバック
        return self._why_template(nugget)

    # PURPOSE: テンプレートベースの推薦理由
    def _why_template(self, nugget: KnowledgeNugget) -> str:
        """テンプレートベースの推薦理由"""
        lines = [
            f"📌 **{nugget.title}** が推薦された理由:",
            "",
            f"- 関連度スコア: **{nugget.relevance_score:.2f}**",
            f"- ソース: {nugget.source}",
        ]
        if nugget.push_reason:
            lines.append(f"- 推薦理由: {nugget.push_reason}")
        if nugget.abstract:
            lines.append(f"- 要約: {nugget.abstract[:200]}")
        return "\n".join(lines)

    # PURPOSE: nugget について追加質問 (LLM 経由)
    def deeper(self, nugget: KnowledgeNugget, question: str) -> str:
        """nugget について追加質問

        LLM 可用時: Gemini で回答生成
        LLM 不可時: 定型メッセージ
        """
        if self._llm.available:
            prompt = self._DEEPER_PROMPT.format(
                title=nugget.title,
                abstract=nugget.abstract[:500] if nugget.abstract else "(なし)",
                source=nugget.source,
                question=question,
            )
            result = self._llm.generate(prompt)
            if result:
                if self._on_feedback:
                    self._on_feedback(nugget.title, "deepened", nugget.source[:1].upper())
                return result

        return (
            f"💡 「{question}」への回答には LLM が必要です。\n"
            f"GOOGLE_API_KEY を設定してください。\n\n"
            f"参考: {nugget.source}"
        )

    # PURPOSE: この nugget に関連する知識を検索
    def related(self, nugget: KnowledgeNugget, k: int = 5) -> list[KnowledgeNugget]:
        """この nugget に関連する知識を GnosisIndex で検索"""
        try:
            from mekhane.anamnesis.index import GnosisIndex

            index = GnosisIndex()
            query = f"{nugget.title} {nugget.abstract[:100] if nugget.abstract else ''}"
            results = index.search(query, k=k + 1)

            # 自分自身を除外
            nuggets = []
            for r in results:
                title = r.get("title", "")
                if title != nugget.title:
                    nuggets.append(
                        KnowledgeNugget(
                            title=title,
                            source=r.get("source", "unknown"),
                            relevance_score=1.0 - r.get("_distance", 0.5),
                            abstract=r.get("abstract", ""),
                            push_reason="関連知識",
                        )
                    )
            if nuggets and self._on_feedback:
                self._on_feedback(nugget.title, "engaged", nugget.source[:1].upper())
            return nuggets[:k]
        except Exception as e:
            print(f"[PushDialog] Related search error: {e}")
            return []
