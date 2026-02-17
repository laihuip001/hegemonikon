# PROOF: [L2/Mekhanē] <- mekhane/periskope/ A0(FEP) -> S5(DeepResearch) -> PackageInit
# PURPOSE: Periskopē パッケージ初期化
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
