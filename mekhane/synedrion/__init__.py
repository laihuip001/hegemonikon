# PROOF: [L2/インフラ] <- mekhane/synedrion/ A2→評議会システム統合パッケージ
# Synedrion — Hegemonikón 多視点レビュー & 静的解析システム
"""
Synedrion — 統合評議会パッケージ

3層構成:
  1. PerspectiveMatrix: 480次元直交視点 (perspectives.yaml)
  2. AIAuditor: 22軸 AST ベース静的解析 (ai_auditor.py)
  3. Gateway: API ゲートウェイ (gateway/)
"""

from .prompt_generator import PerspectiveMatrix, Perspective  # noqa: F401

__all__ = ["PerspectiveMatrix", "Perspective", "AIAuditor"]
