# PROOF: [L2/Mekhane] <- mekhane/periskope/searchers/tavily_searcher.py A0->Found->Fix
"""
Tavily Search API client for Periskopē.

Tavily is an AI-optimized search API that returns structured,
concise results. Free tier: 1,000 credits/month.

API docs: https://docs.tavily.com/
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)

_TAVILY_API_URL = "https://api.tavily.com/search"


class TavilySearcher:
    """Client for Tavily Search API.

    Tavily provides AI-optimized search with:
    - Structured, concise results (no HTML scraping needed)
    - Answer extraction (direct answers to queries)
    - 1,000 free credits/month (basic=1 credit, advanced=2)

    Requires TAVILY_API_KEY environment variable.
    """

    def __init__(self, timeout: float = 15.0) -> None:
        self._api_key = os.getenv("TAVILY_API_KEY", "")
        self._timeout = timeout

    @property
    def available(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)

    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = True,
        include_raw_content: bool = False,
        topic: str = "general",
    ) -> list[SearchResult]:
        """Search via Tavily API.

        Args:
            query: Search query.
            max_results: Maximum results (1-10 for basic, 1-5 for advanced).
            search_depth: 'basic' (1 credit) or 'advanced' (2 credits).
            include_answer: Whether to include AI-generated answer.
            include_raw_content: Include full page content (costly).
            topic: 'general' or 'news'.

        Returns:
            List of SearchResult from Tavily.
        """
        if not self.available:
            logger.warning("TAVILY_API_KEY not set — skipping Tavily search")
            return []

        payload = {
            "api_key": self._api_key,
            "query": query,
            "max_results": min(max_results, 10),
            "search_depth": search_depth,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "topic": topic,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(_TAVILY_API_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error("Tavily HTTP error: %s — %s", e.response.status_code, e)
            return []
        except Exception as e:
            logger.error("Tavily search failed: %s", e)
            return []

        results: list[SearchResult] = []
        raw_results = data.get("results", [])

        for i, item in enumerate(raw_results[:max_results]):
            url = item.get("url", "")
            title = item.get("title", "")
            content = item.get("content", "")
            raw_content = item.get("raw_content", "")

            # Use Tavily's relevance score if available
            relevance = item.get("score", 1.0 - (i / max(len(raw_results), 1)) * 0.5)

            result = SearchResult(
                source=SearchSource.TAVILY,
                title=title,
                url=url or None,
                content=raw_content[:1000] if raw_content else content,
                snippet=_truncate(content, 200),
                relevance=relevance,
                timestamp=item.get("published_date"),
                metadata={
                    "search_depth": search_depth,
                    "topic": topic,
                },
            )
            results.append(result)

        # If AI answer is included, add it as an extra result
        answer = data.get("answer")
        if answer and include_answer:
            results.insert(0, SearchResult(
                source=SearchSource.TAVILY,
                title=f"[Tavily Answer] {query[:50]}",
                url=None,
                content=answer,
                snippet=_truncate(answer, 200),
                relevance=1.0,
                metadata={"type": "ai_answer", "search_depth": search_depth},
            ))

        logger.info("Tavily: %d results for %r", len(results), query)
        return results


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
