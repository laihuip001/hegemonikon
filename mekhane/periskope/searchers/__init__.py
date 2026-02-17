# PROOF: [L2/Mekhanē] <- mekhane/periskope/searchers/
"""
PROOF: [L2/Mekhanē] This file must exist.

P3 → Need for external research capabilities.
   → Package initialization for searchers module.
   → __init__.py exports the searcher classes.

Q.E.D.
"""

from .searxng import SearXNGSearcher
from .exa_searcher import ExaSearcher
from .internal_searcher import GnosisSearcher, SophiaSearcher, KairosSearcher

__all__ = [
    "SearXNGSearcher",
    "ExaSearcher",
    "GnosisSearcher",
    "SophiaSearcher",
    "KairosSearcher",
]
