# PROOF: [L2/Periskope] <- mekhane/periskope/searchers/__init__.py A0→AutoFix→CI_Failure_Mitigation
"""
Periskopē searchers — pluggable search source adapters.

Each searcher implements the same async interface:
    async def search(query: str, max_results: int) -> list[SearchResult]
"""

from .searxng import SearXNGSearcher
from .brave_searcher import BraveSearcher
from .tavily_searcher import TavilySearcher
from .semantic_scholar_searcher import SemanticScholarSearcher
from .internal_searcher import GnosisSearcher, SophiaSearcher, KairosSearcher

__all__ = [
    "SearXNGSearcher",
    "BraveSearcher",
    "TavilySearcher",
    "SemanticScholarSearcher",
    "GnosisSearcher",
    "SophiaSearcher",
    "KairosSearcher",
]
