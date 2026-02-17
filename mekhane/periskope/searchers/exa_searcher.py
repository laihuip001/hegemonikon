# PROOF: [L2/Mekhanē] <- mekhane/periskope/searchers/
"""
PROOF: [L2/Mekhanē] This file must exist.

P3 → Need for external research capabilities.
   → Interface to Exa semantic search engine.
   → exa_searcher.py implements this interface.

Q.E.D.
"""

"""
Exa search client for Periskopē.

Wraps the Exa MCP tool for semantic/neural web search.
Exa specializes in meaning-based search (not keyword-based),
making it complementary to SearXNG's traditional search.
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import json
from typing import Any

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)


class ExaSearcher:
    """Client for Exa semantic search via MCP.

    Exa provides neural/semantic search capabilities that find
    results based on meaning rather than keywords. This is
    particularly useful for conceptual queries and research topics.

    Note: Uses the Exa MCP server, which must be configured
    in the IDE's MCP settings.
    """

    def __init__(self) -> None:
        pass

    async def search(
        self,
        query: str,
        max_results: int = 10,
        category: str = "general",
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        search_type: str = "auto",
    ) -> list[SearchResult]:
        """Execute a semantic search via Exa.

        Since Exa is available as an MCP server, this searcher
        wraps the MCP tool interface. For Periskopē engine use,
        we call Exa's HTTP API directly if available, or fall back
        to subprocess-based invocation.

        Args:
            query: Search query (meaning-based).
            max_results: Maximum number of results.
            category: Result type (general, research paper, news, etc.).
            include_domains: Domains to include.
            exclude_domains: Domains to exclude.
            search_type: auto, neural, or keyword.

        Returns:
            List of SearchResult objects.
        """
        try:
            results = await self._search_via_api(
                query=query,
                max_results=max_results,
                category=category,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                search_type=search_type,
            )
            return results
        except Exception as e:
            logger.error("Exa search failed: %s", e)
            return []

    async def _search_via_api(
        self,
        query: str,
        max_results: int,
        category: str,
        include_domains: list[str] | None,
        exclude_domains: list[str] | None,
        search_type: str,
    ) -> list[SearchResult]:
        """Search using Exa's HTTP API (via environment key)."""
        import os

        api_key = os.environ.get("EXA_API_KEY")
        if not api_key:
            logger.warning("EXA_API_KEY not set, Exa search unavailable")
            return []

        import httpx

        payload: dict[str, Any] = {
            "query": query,
            "numResults": max_results,
            "type": search_type,
            "category": category,
            "contents": {
                "text": {"maxCharacters": 3000},
            },
        }
        if include_domains:
            payload["includeDomains"] = include_domains
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.exa.ai/search",
                json=payload,
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for i, item in enumerate(data.get("results", [])):
            result = SearchResult(
                source=SearchSource.EXA,
                title=item.get("title", ""),
                url=item.get("url"),
                content=item.get("text", ""),
                snippet=_truncate(item.get("text", ""), 200),
                relevance=item.get("score", 1.0 - (i / max(max_results, 1))),
                timestamp=item.get("publishedDate"),
                metadata={
                    "exa_id": item.get("id", ""),
                    "author": item.get("author", ""),
                },
            )
            results.append(result)

        logger.info("Exa: %d results for %r", len(results), query)
        return results

    async def search_academic(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search for research papers via Exa."""
        return await self.search(
            query=query,
            max_results=max_results,
            category="research paper",
            search_type="neural",
        )


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
