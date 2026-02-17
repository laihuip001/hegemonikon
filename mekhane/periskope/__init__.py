# PROOF: [L2/Mekhanē] <- mekhane/periskope/ A0→Search→Search Results→Deep Research Engine
# PURPOSE: Periskopē パッケージ定義 (Deep Research Engine)
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
