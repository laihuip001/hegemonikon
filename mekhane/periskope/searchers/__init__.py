# PROOF: [S2/Mekhanē] <- mekhane/ A0->Implementation
# PURPOSE: [S2/Mekhanē] Implementation of __init__.py
"""
Periskopē searchers — pluggable search source adapters.

Each searcher implements the same async interface:
    # PURPOSE: [S2/Mekhanē] search
    async def search(query: str, max_results: int) -> list[SearchResult]
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
