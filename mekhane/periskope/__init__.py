# PROOF: [L2/Periskope] <- mekhane/periskope/ A0->Need->Search
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
