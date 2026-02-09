#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/pks/
# PURPOSE: PKS 共通 LLM クライアント
"""
A0 (FEP) → 複数コンポーネントが同一の LLM 初期化パターンを持つ
→ DRY 原則により共通化
→ llm_client.py が担う

# PURPOSE: Gemini クライアントの共通初期化と提供
"""

from __future__ import annotations

import os
from typing import Optional


# PURPOSE: PKS 共通 LLM クライアントプロバイダー
class PKSLLMClient:
    """PKS 共通 LLM クライアントプロバイダー

    Narrator, MatrixView, SuggestedQuestionGenerator で重複していた
    Gemini クライアント初期化ロジックを共通化。

    Usage:
        client = PKSLLMClient()
        if client.available:
            response = client.generate("prompt text")
    """

    # PURPOSE: PKSLLMClient の初期化
    def __init__(self, model: str = "gemini-2.0-flash", enabled: bool = True):
        self._client = None
        self._model = model
        if enabled:
            self._init()

    def _init(self) -> None:
        """Gemini クライアントを初期化"""
        try:
            from google import genai

            api_key = (
                os.environ.get("GOOGLE_API_KEY")
                or os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GOOGLE_GENAI_API_KEY")
            )
            self._client = (
                genai.Client(api_key=api_key) if api_key else genai.Client()
            )
        except (ImportError, Exception):
            self._client = None

    # PURPOSE: LLM が利用可能か
    @property
    def available(self) -> bool:
        return self._client is not None

    # PURPOSE: LLM でテキスト生成
    def generate(self, prompt: str) -> Optional[str]:
        """プロンプトからテキストを生成

        Returns:
            生成テキスト。エラー時は None。
        """
        if not self.available:
            return None

        try:
            response = self._client.models.generate_content(
                model=self._model, contents=prompt
            )
            return response.text if response else None
        except Exception as e:
            print(f"[PKSLLMClient] Error: {e}")
            return None

    @property
    def model(self) -> str:
        return self._model
