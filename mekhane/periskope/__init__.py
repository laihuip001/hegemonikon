# PROOF: [S1/Periskope] <- mekhane/periskope/PROOF.md S1 target
# PURPOSE: Periskopē - HGK Deep Research Engine.

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
