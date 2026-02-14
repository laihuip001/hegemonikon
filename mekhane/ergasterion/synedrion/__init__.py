# PROOF: [L2/インフラ] <- mekhane/ergasterion/synedrion/ 後方互換 re-export ラッパー
"""
Backward compatibility shim — DEPRECATED.

Canonical location: mekhane.synedrion
This module re-exports PerspectiveMatrix for existing imports.
Migrate to: from mekhane.synedrion import PerspectiveMatrix
"""

import warnings

warnings.warn(
    "mekhane.ergasterion.synedrion is deprecated. "
    "Use mekhane.synedrion instead.",
    DeprecationWarning,
    stacklevel=2,
)

from mekhane.synedrion.prompt_generator import PerspectiveMatrix, Perspective  # noqa: F401

__all__ = ["PerspectiveMatrix", "Perspective"]
