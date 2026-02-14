# PROOF: [L2/品質] <- mekhane/synteleia/dokimasia/ A0→品質保証→Cortex直接LLMバックエンド
# PURPOSE: Cortex (Gemini API 直接呼出) バックエンド — IDE/LS 非依存
"""
CortexBackend — Direct Gemini API Bridge for Synteleia

OchemaBackend が Antigravity Language Server に依存するのに対し、
CortexBackend は Gemini API を直接呼び出す。
CI/CD や IDE 外での監査実行に使用。

Usage:
    backend = CortexBackend()                       # gemini-2.5-flash (default)
    backend = CortexBackend(model="gemini-2.5-pro") # Pro model
    response = backend.query(prompt, context)
"""

import json
import os
from typing import Optional

from .semantic_agent import LLMBackend


# PURPOSE: Cortex (Gemini API 直接呼出) バックエンド
class CortexBackend(LLMBackend):
    """Gemini API 直接呼出バックエンド。

    IDE (Language Server) に依存せず、GEMINI_API_KEY で直接認証する。
    CI/CD パイプラインやスタンドアロン実行で利用可能。

    Available models:
        - gemini-2.5-flash (default, cost-optimal)
        - gemini-2.5-pro   (higher quality)
        - gemini-2.0-flash (fastest)
    """

    # PURPOSE: 初期化
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        timeout: float = 60.0,
        label: str = "",
    ):
        self.model = model
        self.timeout = timeout
        self.label = label or model
        self._available: Optional[bool] = None

    # PURPOSE: Gemini API にクエリを送信
    def query(self, prompt: str, context: str) -> str:
        """Gemini API 直接呼出でクエリを実行。"""
        import google.generativeai as genai

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return json.dumps({
                "issues": [],
                "summary": "GEMINI_API_KEY not set",
                "confidence": 0.0,
            })

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(self.model)

        combined = f"{prompt}\n\n---\n\n## 監査対象\n\n{context}"

        response = model.generate_content(
            combined,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000,
            ),
        )

        return response.text or "{}"

    # PURPOSE: バックエンドが利用可能か
    def is_available(self) -> bool:
        """GEMINI_API_KEY が設定されているかチェック。"""
        if self._available is None:
            self._available = bool(os.environ.get("GEMINI_API_KEY"))
        return self._available

    # PURPOSE: 文字列表現
    def __repr__(self) -> str:
        return f"CortexBackend(model={self.model!r}, label={self.label!r})"
