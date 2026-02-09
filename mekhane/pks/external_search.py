# PROOF: [L2/PKS] <- mekhane/pks/
#!/usr/bin/env python3
# PURPOSE: 外部知識検索 (Perplexity API 統合)
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → Gnōsis 内部知識だけでは自由エネルギーの最小化に限界
→ 外部知識ソースとの統合が能動的推論を完成させる
→ external_search.py が担う

# PURPOSE: Perplexity API 経由の外部知識検索
"""

from __future__ import annotations

import os
from typing import Optional

from mekhane.pks.pks_engine import KnowledgeNugget


# PURPOSE: Perplexity API 経由の外部知識検索
class PerplexitySearch:
    """Perplexity Sonar API で外部知識を検索

    Gnōsis 内部インデックスを補完する外部知識ソース。
    OpenAI-compatible API を使用。

    Env:
        PERPLEXITY_API_KEY: Perplexity API キー

    Usage:
        search = PerplexitySearch()
        if search.available:
            nuggets = search.search("FEP Active Inference latest research")
    """

    DEFAULT_MODEL = "sonar"
    API_BASE = "https://api.perplexity.ai"

    # PURPOSE: PerplexitySearch の初期化
    def __init__(self, model: str = DEFAULT_MODEL):
        self._model = model
        self._api_key = os.environ.get("PERPLEXITY_API_KEY", "")
        self._client = None
        if self._api_key:
            self._init_client()

    def _init_client(self) -> None:
        """OpenAI-compatible クライアントを初期化"""
        try:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self._api_key,
                base_url=self.API_BASE,
            )
        except ImportError:
            self._client = None

    # PURPOSE: API が利用可能か
    @property
    def available(self) -> bool:
        return self._client is not None

    # PURPOSE: 外部知識を検索して KnowledgeNugget リストに変換
    def search(
        self, query: str, max_results: int = 5
    ) -> list[KnowledgeNugget]:
        """Perplexity で検索して KnowledgeNugget リストを返す

        Args:
            query: 検索クエリ
            max_results: 最大結果数

        Returns:
            KnowledgeNugget リスト (外部ソース)
        """
        if not self.available:
            return []

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a research assistant. "
                            "Find relevant academic knowledge. "
                            "Respond in Japanese. "
                            "Structure your response as numbered items, each with: "
                            "[TITLE] title\n[ABSTRACT] summary\n[SOURCE] url or reference"
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                max_tokens=1024,
            )

            text = response.choices[0].message.content if response.choices else ""
            if text:
                return self._parse_results(text, max_results)
        except Exception as e:
            print(f"[PerplexitySearch] Error: {e}")

        return []

    # PURPOSE: Perplexity レスポンスをパース
    def _parse_results(
        self, text: str, max_results: int
    ) -> list[KnowledgeNugget]:
        """テキストレスポンスを KnowledgeNugget にパース"""
        nuggets = []
        current_title = ""
        current_abstract = ""
        current_source = ""

        for line in text.strip().split("\n"):
            line = line.strip()
            if line.startswith("[TITLE]"):
                # 前のエントリを保存
                if current_title:
                    nuggets.append(self._make_nugget(
                        current_title, current_abstract, current_source
                    ))
                current_title = line.replace("[TITLE]", "").strip()
                current_abstract = ""
                current_source = ""
            elif line.startswith("[ABSTRACT]"):
                current_abstract = line.replace("[ABSTRACT]", "").strip()
            elif line.startswith("[SOURCE]"):
                current_source = line.replace("[SOURCE]", "").strip()

        # 最後のエントリ
        if current_title:
            nuggets.append(self._make_nugget(
                current_title, current_abstract, current_source
            ))

        return nuggets[:max_results]

    # PURPOSE: KnowledgeNugget を生成
    def _make_nugget(
        self, title: str, abstract: str, source: str
    ) -> KnowledgeNugget:
        return KnowledgeNugget(
            title=title,
            source=source or "perplexity",
            relevance_score=0.7,  # 外部ソースはデフォルト 0.7
            abstract=abstract,
            push_reason="外部知識 (Perplexity)",
        )

    # PURPOSE: Gnōsis 結果と外部結果をマージ
    @staticmethod
    def merge_results(
        internal: list[KnowledgeNugget],
        external: list[KnowledgeNugget],
        max_external: int = 3,
    ) -> list[KnowledgeNugget]:
        """Gnōsis 内部結果と Perplexity 外部結果をマージ

        内部結果を優先し、末尾に外部結果を追加。
        """
        # 重複タイトルを除外
        internal_titles = {n.title.lower() for n in internal}
        unique_external = [
            n for n in external
            if n.title.lower() not in internal_titles
        ]
        return internal + unique_external[:max_external]
