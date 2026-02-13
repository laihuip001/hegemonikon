# PROOF: [L2/Nous] <- mekhane/synteleia/dokimasia/ Ochema Backend
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
        # クライアントは遅延初期化
        client = self._get_client()
        if not client:
            return "Error: AntigravityClient unavailable"

        combined = f"{prompt}\n\n---\n\n## 監査対象\n\n{context}"

        try:
            # AntigravityClient 経由で質問
            # Note: 実際の実装に合わせてメソッド呼び出しを調整
            response = client.ask(
                message=combined,
                model=self.model,
                timeout=self.timeout,
            )

            # レスポンス形式に応じてテキスト抽出
            if hasattr(response, "text"):
                return response.text
            elif isinstance(response, str):
                return response
            elif isinstance(response, dict) and "text" in response:
                return response["text"]
            else:
                return str(response)

        except Exception as e:
            return f"Error querying OchemaBackend: {e}"

    # PURPOSE: バックエンドが利用可能か
    def is_available(self) -> bool:
        """AntigravityClient が接続可能かチェック。"""
        if self._available is None:
            try:
                client = self._get_client()
                # 簡易接続チェック (get_status は RPC コールを含む)
                if client:
                    client.get_status()
                    self._available = True
                else:
                    self._available = False
            except Exception:
                self._available = False
        return self._available

    # PURPOSE: AntigravityClient のシングルトン取得
    def _get_client(self):
        """AntigravityClient をシングルトンで取得。synteleia-sandbox WS に接続。"""
        if self._client is None:
            try:
                from mekhane.ochema.antigravity_client import AntigravityClient
                self._client = AntigravityClient(workspace="synteleia-sandbox")
            except ImportError:
                return None
        return self._client

    def __repr__(self) -> str:
        return f"OchemaBackend(model={self.model!r}, label={self.label!r})"
