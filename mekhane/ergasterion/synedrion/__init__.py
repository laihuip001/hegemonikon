# PROOF: [L2/インフラ] <- mekhane/ergasterion/synedrion/ 後方互換 re-export ラッパー
"""
Backward compatibility shim.

Canonical location: mekhane.synedrion
This module re-exports PerspectiveMatrix for existing imports.
"""

from mekhane.synedrion.prompt_generator import PerspectiveMatrix, Perspective  # noqa: F401

__all__ = ["PerspectiveMatrix", "Perspective"]
