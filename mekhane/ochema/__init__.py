#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- ochema/ A0→Implementation→__init__
# PROOF: [L2/インフラ] <- mekhane/ochema/ A0→外部LLM接続
# PURPOSE: Ochēma パッケージ初期化 — lazy import で proto 依存を回避
"""
Ochēma package — Unified LLM Access Layer.

Exports:
    OchemaService     - Unified LLM service (always available)
    AntigravityClient - LS bridge (requires proto)
    CortexClient      - Cortex API direct (requires LLMResponse from antigravity_client)
    LLMResponse       - Response data class
"""

from __future__ import annotations


def __getattr__(name: str):
    """Lazy import for all public symbols.

    This avoids triggering the proto dependency chain at package import time,
    which is essential for test environments and MCP servers.
    """
    if name == "OchemaService":
        from mekhane.ochema.service import OchemaService
        return OchemaService
    if name == "CortexClient":
        from mekhane.ochema.cortex_client import CortexClient
        return CortexClient
    if name == "AntigravityClient":
        from mekhane.ochema.antigravity_client import AntigravityClient
        return AntigravityClient
    if name == "LLMResponse":
        from mekhane.ochema.types import LLMResponse
        return LLMResponse
    raise AttributeError(f"module 'mekhane.ochema' has no attribute {name!r}")


__all__ = ["AntigravityClient", "CortexClient", "LLMResponse", "OchemaService"]
