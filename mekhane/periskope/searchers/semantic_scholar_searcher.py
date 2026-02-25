# PROOF: [L2/Mekhane] <- mekhane/periskope/searchers/ A0→Implementation→semantic_scholar_searcher
"""
Semantic Scholar API client for Periskopē.

Provides free, unlimited access to academic paper search.
No API key required (but recommended for higher rate limits).
Rate limits: 1 RPS with key, shared 5000/5min without.

API docs: https://api.semanticscholar.org/api-docs/
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)

_S2_API_URL = "https://api.semanticscholar.org/graph/v1"
_S2_SEARCH_URL = f"{_S2_API_URL}/paper/search"


# PURPOSE: Client for Semantic Scholar API
class SemanticScholarSearcher:
    """Client for Semantic Scholar API.

    Free academic paper search with:
    - Semantic (meaning-based) paper search
    - Citation data, abstracts, author info
    - No API key required (but recommended)
    - Rate limit: 1 RPS (with key) / shared pool (without)

    Optional: S2_API_KEY environment variable for higher limits.
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self._api_key = os.getenv("S2_API_KEY") or os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        self._timeout = timeout

    # PURPOSE: Always available (no key required, key is optional)
    @property
    def available(self) -> bool:
        """Always available (no key required, key is optional)."""
        return True

    # PURPOSE: Search academic papers via Semantic Scholar
    async def search(
        self,
        query: str,
        max_results: int = 10,
        year_range: str | None = None,
        fields_of_study: list[str] | None = None,
        open_access_only: bool = False,
    ) -> list[SearchResult]:
        """Search academic papers via Semantic Scholar.

        Args:
            query: Search query.
            max_results: Maximum results (1-100).
            year_range: Year filter (e.g., '2023-2026', '2024-').
            fields_of_study: Filter by field (e.g., ['Computer Science']).
            open_access_only: Only return open access papers.

        Returns:
            List of SearchResult from Semantic Scholar.
        """
        headers: dict[str, str] = {}
        if self._api_key:
            headers["x-api-key"] = self._api_key

        params: dict[str, Any] = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": "title,abstract,url,year,authors,citationCount,"
                      "externalIds,openAccessPdf,publicationDate,"
                      "journal,fieldsOfStudy",
        }
        if year_range:
            params["year"] = year_range
        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)
        if open_access_only:
            params["openAccessPdf"] = ""

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, headers=headers,
            ) as client:
                resp = await client.get(_S2_SEARCH_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error("S2 HTTP error: %s — %s", e.response.status_code, e)
            return []
        except Exception as e:
            logger.error("Semantic Scholar search failed: %s", e)
            return []

        results: list[SearchResult] = []
        papers = data.get("data", [])

        for i, paper in enumerate(papers[:max_results]):
            title = paper.get("title", "Untitled")
            abstract = paper.get("abstract", "")
            url = paper.get("url", "")

            # Build author string
            authors = paper.get("authors", [])
            author_str = ", ".join(
                a.get("name", "") for a in authors[:5]
            )
            if len(authors) > 5:
                author_str += f" et al. ({len(authors)} authors)"

            # Get external IDs
            ext_ids = paper.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI")
            arxiv_id = ext_ids.get("ArXiv")

            # Open access PDF
            oa_pdf = paper.get("openAccessPdf")
            pdf_url = oa_pdf.get("url") if oa_pdf else None

            # Relevance: S2 returns in relevance order
            citation_count = paper.get("citationCount", 0) or 0
            # Combine position with citation impact
            position_score = 1.0 - (i / max(len(papers), 1)) * 0.5
            citation_boost = min(citation_count / 1000, 0.3)
            relevance = position_score + citation_boost

            content = abstract or ""
            if author_str:
                content = f"Authors: {author_str}\n\n{content}"

            result = SearchResult(
                source=SearchSource.SEMANTIC_SCHOLAR,
                title=title,
                url=url or None,
                content=content[:1000],
                snippet=_truncate(abstract or title, 200),
                relevance=relevance,
                timestamp=paper.get("publicationDate"),
                metadata={
                    "authors": author_str,
                    "citations": citation_count,
                    "year": paper.get("year"),
                    "doi": doi,
                    "arxiv_id": arxiv_id,
                    "pdf_url": pdf_url,
                    "journal": (paper.get("journal") or {}).get("name", ""),
                    "fields_of_study": paper.get("fieldsOfStudy", []),
                },
            )
            results.append(result)

        logger.info(
            "Semantic Scholar: %d results for %r", len(results), query,
        )
        return results


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
