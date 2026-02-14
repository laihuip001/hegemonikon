# PROOF: [S2/Mekhanē] <- mekhane/ochema/__init__.py Package Init
# PURPOSE: Ochēma パッケージ — Antigravity LS クライアント
# REASON: Ochema パッケージの初期化と公開APIの定義
"""Ochēma (ὄχημα) — Antigravity Language Server Client Package."""

from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse

__all__ = ["AntigravityClient", "LLMResponse"]
