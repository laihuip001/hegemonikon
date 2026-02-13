# PROOF: [L2/クライアント] <- mekhane/ochema/ A0→パッケージインターフェース定義
# PURPOSE: Ochēma パッケージ — Antigravity LS クライアント
# REASON: 外部LLM接続とセッション管理を提供するAntigravity LSのクライアントパッケージ
"""Ochēma (ὄχημα) — Antigravity Language Server Client Package."""

from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse

__all__ = ["AntigravityClient", "LLMResponse"]
