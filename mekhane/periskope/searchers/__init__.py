# PROOF: [L2/インフラ] <- mekhane/
"""
Periskopē searchers — pluggable search source adapters.

Each searcher implements the same async interface:
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
