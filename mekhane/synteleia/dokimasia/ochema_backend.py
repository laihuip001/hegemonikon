# PURPOSE: Ochēma (AntigravityClient) 経由の LLM バックエンド
"""
OchemaBackend — Antigravity Language Server Bridge for Synteleia

AntigravityClient を使い、Ultra プランの LLM を Synteleia 監査に利用する。
Strategy Pattern: LLMBackend の具象実装。

Usage:
    backend = OchemaBackend(model="MODEL_PLACEHOLDER_M8")  # Gemini 3 Pro
    response = backend.query(prompt, context)
"""

import json
from typing import Optional

from .semantic_agent import LLMBackend


# PURPOSE: Ochēma (AntigravityClient) 経由の LLM バックエンド
class OchemaBackend(LLMBackend):
    """Ochēma (AntigravityClient) 経由の LLM バックエンド。

    Antigravity IDE の Language Server に接続し、
    Ultra プランで利用可能な LLM にクエリを送信する。

    Available models:
        - MODEL_PLACEHOLDER_M8: Gemini 3 Pro (100%)
        - MODEL_PLACEHOLDER_M26: Claude Opus 4.6 Thinking (40%)
        - MODEL_OPENAI_GPT_OSS_120B_MEDIUM: GPT-OSS 120B (40%)
        - MODEL_CLAUDE_4_5_SONNET: Claude Sonnet 4.5 (40%)
        - MODEL_PLACEHOLDER_M18: Gemini 3 Flash (100%)
    """

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(
        self,
        model: str = "MODEL_PLACEHOLDER_M8",  # Gemini 3 Pro
        timeout: float = 60.0,
        label: str = "",
    ):
        self.model = model
        self.timeout = timeout
        self.label = label or model
        self._client = None
        self._available: Optional[bool] = None

    # PURPOSE: LLM にクエリを送信
    def query(self, prompt: str, context: str) -> str:
        """Ochēma 経由で LLM にクエリを送信し、テキスト応答を返す。"""
        client = self._get_client()
        combined = f"{prompt}\n\n---\n\n## 監査対象\n\n{context}"

        response = client.ask(
            message=combined,
            model=self.model,
            timeout=self.timeout,
        )

        return response.text

    # PURPOSE: バックエンドが利用可能か
    def is_available(self) -> bool:
        """AntigravityClient が接続可能かチェック。"""
        if self._available is None:
            try:
                client = self._get_client()
                client.get_status()
                self._available = True
            except Exception:
                self._available = False
        return self._available

    # PURPOSE: AntigravityClient のシングルトン取得
    def _get_client(self):
        """AntigravityClient をシングルトンで取得。synteleia-sandbox WS に接続。"""
        if self._client is None:
            from mekhane.ochema.antigravity_client import AntigravityClient
            self._client = AntigravityClient(workspace="synteleia-sandbox")
        return self._client

    # PURPOSE: [L2-auto] 文字列表現: repr__
    def __repr__(self) -> str:
        return f"OchemaBackend(model={self.model!r}, label={self.label!r})"
