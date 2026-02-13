# PROOF: [L2/Hodos] <- mekhane/synteleia/dokimasia/ochema_backend.py
# PURPOSE: Dokimasia 用の Ochēma バックエンドアダプタ
"""
Ochēma Backend for Dokimasia

Dokimasia の検証プロセスが Antigravity LS (Ochēma) を利用するためのアダプタ。
"""

from typing import Any, Dict

from mekhane.ochema.antigravity_client import AntigravityClient


# PURPOSE: [L2-auto] Ochēma バックエンド
class OchemaBackend:
    """Ochēma バックエンド"""

    def __init__(self):
        self.client = AntigravityClient()

    # PURPOSE: [L2-auto] 生成リクエストを処理する
    def generate(self, prompt: str, **kwargs) -> str:
        """生成リクエストを処理する"""
        response = self.client.ask(prompt)
        return response.text
