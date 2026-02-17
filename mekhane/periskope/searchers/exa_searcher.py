# PROOF: [L2/Periskopē] <- mekhane/periskope/searchers/ Exa Client
"""
Exa (formerly Metaphor) search client.
"""

from typing import List

from mekhane.periskope.models import SearchResult, SearchSource

class ExaSearcher:
    """Client for Exa search engine."""

    async def search(self, query: str, max_results: int = 20) -> List[SearchResult]:
        # Implementation placeholder
        return []
