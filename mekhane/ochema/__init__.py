# PROOF: [L2/Ochema] <- mekhane/ochema/ Ochema
"""
Ochema - Antigravity AI Client Layer

LLM API (OpenAI/Anthropic/Google/Ollama) への統一アクセスを提供する。
"""
from .antigravity_client import AntigravityClient, LLMResponse

__all__ = ["AntigravityClient", "LLMResponse"]
