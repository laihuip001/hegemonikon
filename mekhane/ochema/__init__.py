# PROOF: [L2/Transport] <- mekhane/ochema/ Ochema LLM Transport
# PURPOSE: LLM (Antigravity LS) との低レイヤー通信クライアント群
"""
Ochēma (The Vehicle) — Antigravity Language Server Client

Provides a standard interface to connect to local/remote LLM servers
(specifically Antigravity LS) via SSE, WebSocket, or HTTP.
"""

from .antigravity_client import AntigravityClient
from .proto import ChatMessage, CompletionRequest, CompletionResponse

__all__ = [
    "AntigravityClient",
    "ChatMessage",
    "CompletionRequest",
    "CompletionResponse",
]
