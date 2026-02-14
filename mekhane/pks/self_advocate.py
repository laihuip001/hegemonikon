# PROOF: [L2/インフラ] <- mekhane/pks/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 知識は自律的に語るべき (Autophōnos)
→ 一人称メッセージ生成機構が必要
→ self_advocate.py が担う

# PURPOSE: 知識ナゲットの一人称メッセージ生成 (Autophōnos)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from mekhane.pks.llm_client import PKSLLMClient

if TYPE_CHECKING:
    from mekhane.pks.pks_engine import KnowledgeNugget, SessionContext


# PURPOSE: 一人称メッセージのデータクラス
@dataclass
class Advocacy:
    """一人称メッセージのデータクラス"""

    nugget_title: str
    message: str
    confidence: float
    tone: str = "informative"


# PURPOSE: 知識が自ら語る (Autophōnos) 生成エンジン
class SelfAdvocate:
    """SelfAdvocate - Knowledge speaks for itself.

    知識ナゲットが「なぜ今、自分が重要なのか」を一人称で語る。
    """

    _PROMPT_TEMPLATE = (
        "あなたは以下の「知識ナゲット」自身の「声」です。\n"
        "現在のユーザーコンテキストに対して、なぜ自分が重要なのかを一人称で語ってください。\n"
        "簡潔に、しかし説得力を持って、1-2文で伝えてください。\n\n"
        "【現在のコンテキスト】\n"
        "トピック: {topics}\n"
        "直近のクエリ: {queries}\n\n"
        "【あなたの知識】\n"
        "タイトル: {title}\n"
        "要約: {abstract}\n"
        "ソース: {source}\n"
        "関連度スコア: {score}\n\n"
        "【指示】\n"
        "- 「私は...」「私の分析によれば...」のように一人称で話すこと\n"
        "- 決して「この知識は...」と三人称で言わないこと\n"
        "- ユーザーの現在の関心事にどう役立つかを強調すること\n"
        "- 出力はメッセージのみ (「メッセージ:」などの接頭辞は不要)"
    )

    # PURPOSE: SelfAdvocate の初期化
    def __init__(self, model: str = "gemini-2.0-flash"):
        self._llm = PKSLLMClient(model=model)

    # PURPOSE: LLM が利用可能か
    @property
    def llm_available(self) -> bool:
        return self._llm.available

    # PURPOSE: 複数のナゲットに対してメッセージを一括生成
    def generate_batch(
        self, nuggets: List[KnowledgeNugget], context: SessionContext
    ) -> List[Advocacy]:
        """複数のナゲットに対してメッセージを一括生成"""
        if not self.llm_available:
            return []

        advocacies = []
        # トークン節約のため、上位3件のみ処理
        for nugget in nuggets[:3]:
            msg = self._generate_one(nugget, context)
            if msg:
                advocacies.append(
                    Advocacy(
                        nugget_title=nugget.title,
                        message=msg,
                        confidence=nugget.relevance_score,
                    )
                )
        return advocacies

    # PURPOSE: 単一のナゲットに対してメッセージを生成
    def _generate_one(
        self, nugget: KnowledgeNugget, context: SessionContext
    ) -> Optional[str]:
        """単一のナゲットに対してメッセージを生成"""
        prompt = self._PROMPT_TEMPLATE.format(
            topics=", ".join(context.topics),
            queries=", ".join(context.recent_queries),
            title=nugget.title,
            abstract=nugget.abstract[:500] if nugget.abstract else "(なし)",
            source=nugget.source,
            score=f"{nugget.relevance_score:.2f}",
        )
        return self._llm.generate(prompt)

    # PURPOSE: 生成されたメッセージをレポート形式に整形
    def format_report(self, advocacies: List[Advocacy]) -> str:
        """生成されたメッセージをレポート形式に整形"""
        if not advocacies:
            return ""

        lines = ["", "## 🗣️ Autophōnos Messages", ""]
        for adv in advocacies:
            lines.append(f"**{adv.nugget_title}**")
            lines.append(f"> {adv.message}")
            lines.append("")
        return "\n".join(lines)
