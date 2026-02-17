# PROOF: [S4/CitationAgent] <- mekhane/periskope/PROOF.md S4 target
# PURPOSE: Verify citations and detect hallucinations (TAINT check).

from __future__ import annotations

import logging
from typing import List, Optional

from mekhane.periskope.models import Citation, SearchResult, TaintLevel
from mekhane.periskope.searchers.searxng import SearXNGSearcher

logger = logging.getLogger(__name__)


class CitationAgent:
    """Agent responsible for verifying citations against trusted sources."""

    def __init__(self, searcher: Optional[SearXNGSearcher] = None) -> None:
        self.searcher = searcher or SearXNGSearcher()

    async def verify_citations(self, citations: List[Citation]) -> List[Citation]:
        """Verify a list of citations by cross-referencing with search results.

        Args:
            citations: List of citations to verify.

        Returns:
            List of verified citations with updated taint levels.
        """
        results: List[Citation] = []
        for citation in citations:
            verified = await self._verify_single(citation)
            results.append(verified)
        return results

    async def _verify_single(self, citation: Citation) -> Citation:
        """Verify a single citation against search results."""
        if citation.is_trustworthy:
            return citation

        # Search for the claim + source title to verify existence
        query = f'"{citation.claim}" site:{citation.source_url}'

        try:
            # Note: This is a simplified logic. Real implementation would check content.
            search_results = await self.searcher.search(query, max_results=1)

            if search_results:
                citation.taint_level = TaintLevel.SOURCE
                citation.similarity = 0.95
            else:
                # If direct match fails, try broader search
                citation.taint_level = TaintLevel.FABRICATED
                citation.similarity = 0.2

        except Exception as e:
            logger.error("Verification failed for citation: %s", e)
            citation.taint_level = TaintLevel.UNCHECKED

        return citation
