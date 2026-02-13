# PROOF: [L2/Antigravity] <- mekhane/ochema/ Antigravity Client Package
# PURPOSE: Antigravity LS との連携クライアントパッケージ
"""
Mekhane Ochema — Antigravity Language Server Client.

AI-driven development platform 'Antigravity' (Codeium) の
Language Server に対して非公式に接続し、LLM 推論能力を活用する
ためのクライアントライブラリ。

Modules:
    - antigravity_client: メインクライアント実装
    - proto: プロトコル定数とヘルパー
    - cli: コマンドラインインターフェース

Disclaimer: Experimental.
"""

from .antigravity_client import AntigravityClient, LLMResponse
from .proto import (
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    RPC_START_CASCADE,
    RPC_SEND_MESSAGE,
)

__all__ = [
    "AntigravityClient",
    "LLMResponse",
    "DEFAULT_MODEL",
    "DEFAULT_TIMEOUT",
    "RPC_START_CASCADE",
    "RPC_SEND_MESSAGE",
]
