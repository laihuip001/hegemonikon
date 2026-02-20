# PROOF: [L3/Periskope] <- mekhane/periskope/__init__.py Search Integration
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
