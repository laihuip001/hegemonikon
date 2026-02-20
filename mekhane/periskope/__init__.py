# PROOF: [S2/Mekhanē] <- mekhane/periskope/ S2→Engine→Init
# PURPOSE: Periskope Init — Deep Research Engine エントリポイント
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
