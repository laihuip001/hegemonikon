# Synedrion v2: Orthogonal Perspective Review System
"""
Jules Synedrion v2 - 直交視点レビューシステム

20 Domains × 6 Axes = 120 structurally orthogonal review perspectives.
"""

from .prompt_generator import PerspectiveMatrix, Perspective

__all__ = ["PerspectiveMatrix", "Perspective"]
