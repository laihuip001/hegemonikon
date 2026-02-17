# PROOF: [L2/インフラ] <- mekhane/periskope/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

S5 → 検索機能の実装が必要
   → 各種検索モジュール (SearXNG, Exa, Internal) の集約が必要
   → searchers/__init__.py が担う

Q.E.D.

---

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
