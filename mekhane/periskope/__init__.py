# PROOF: [L2/Mekhanē] <- mekhane/periskope/
"""
PROOF: [L2/Mekhanē] This file must exist.

P3 → Need for external research capabilities.
   → Package initialization for Periskopē module.
   → __init__.py defines the public API.

Q.E.D.
"""

"""
Periskopē — HGK Deep Research Engine

Multi-source parallel search + multi-model synthesis + TAINT verification.
"""

from .models import SearchResult, SynthesisResult, Citation, PeriskopeConfig, PeriskopeReport

__all__ = [
    "SearchResult",
    "SynthesisResult",
    "Citation",
    "PeriskopeConfig",
    "PeriskopeReport",
]
