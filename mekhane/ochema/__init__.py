# PROOF: [L2/Hodos] <- mekhane/ochema/
# PURPOSE: Ochēma Package Initialization
"""Ochēma (ὄχημα, 乗り物) — Antigravity Language Server Client.

Antigravity LS との接続・通信を管理し、LLM とのインタラクションを提供する。
"""

from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse

__all__ = ["AntigravityClient", "LLMResponse"]
