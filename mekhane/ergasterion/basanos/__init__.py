# PROOF: [L2/インフラ] <- mekhane/ergasterion/basanos/ 後方互換 re-export ラッパー
# PURPOSE: Backward compatibility shim — DEPRECATED.
"""
Backward compatibility shim — DEPRECATED.

Canonical location: mekhane.basanos
This module re-exports PerspectiveMatrix for existing imports.
Migrate to: from mekhane.basanos import PerspectiveMatrix
"""

import warnings

warnings.warn(
    "mekhane.ergasterion.basanos is deprecated. "
    "Use mekhane.basanos instead.",
    DeprecationWarning,
    stacklevel=2,
)

from mekhane.basanos.prompt_generator import PerspectiveMatrix, Perspective  # noqa: F401

__all__ = ["PerspectiveMatrix", "Perspective"]
