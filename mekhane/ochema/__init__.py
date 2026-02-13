# PROOF: [L2/インフラ] <- mekhane/ochema/ A0→外部LLM接続→パッケージ定義
# PURPOSE: Ochēma パッケージ — Antigravity LS クライアント
# REASON: Antigravity LS への接続機能を提供し、UltraプランのLLMを活用可能にするため
"""Ochēma (ὄχημα) — Antigravity Language Server Client Package."""

from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse

__all__ = ["AntigravityClient", "LLMResponse"]
