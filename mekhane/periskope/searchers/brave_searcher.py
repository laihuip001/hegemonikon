# PROOF: [L2/Mekhane] <- mekhane/periskope/searchers/ A0→AutoFix→brave_searcher
"""
Brave Search API client for Periskopē.

Brave Search provides high-quality web search with a generous
free tier of 2,000 queries per month. No tracking, independent
index — complements SearXNG's meta-search approach.

API docs: https://api.search.brave.com/app/documentation/web-search
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)

# Brave Web Search API endpoint
_BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"


class BraveSearcher:
    """Client for Brave Search API.

    Provides high-quality web search results with:
    - Independent search index (not Google/Bing reliant)
    - Privacy-focused (no tracking)
    - 2,000 free queries/month

    Requires BRAVE_API_KEY environment variable.
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self._api_key = os.getenv("BRAVE_API_KEY", "")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def available(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self._api_key,
                },
            )
        return self._client

    async def search(
        self,
        query: str,
        max_results: int = 10,
        country: str = "",
        search_lang: str = "",
        freshness: str = "",
    ) -> list[SearchResult]:
        """Search via Brave Search API.

        Args:
            query: Search query string.
            max_results: Maximum results (1-20, Brave API limit).
            country: Country code for results (e.g., 'JP', 'US').
            search_lang: Language code (e.g., 'ja', 'en').
            freshness: Time filter ('pd'=past day, 'pw'=past week,
                       'pm'=past month, 'py'=past year, or date range).

        Returns:
            List of SearchResult from Brave.
        """
        if not self.available:
            logger.warning("BRAVE_API_KEY not set — skipping Brave search")
            return []

        params: dict[str, Any] = {
            "q": query,
            "count": min(max_results, 20),  # Brave max is 20 per request
        }
        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        if freshness:
            params["freshness"] = freshness

        try:
            client = await self._get_client()
            resp = await client.get(_BRAVE_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error("Brave search HTTP error: %s — %s", e.response.status_code, e)
            return []
        except Exception as e:
            logger.error("Brave search failed: %s", e)
            return []

        # Extract web results
        web_results = data.get("web", {}).get("results", [])
        results: list[SearchResult] = []

        for i, item in enumerate(web_results[:max_results]):
            url = item.get("url", "")
            title = item.get("title", "")
            description = item.get("description", "")
            # Extra content from deep results if available
            extra = ""
            if "extra_snippets" in item:
                extra = " ".join(item["extra_snippets"][:2])

            content = description
            if extra:
                content = f"{description}\n\n{extra}"

            # Relevance: position-based scoring (1.0 → 0.5)
            relevance = 1.0 - (i / max(len(web_results), 1)) * 0.5

            result = SearchResult(
                source=SearchSource.BRAVE,
                title=title,
                url=url or None,
                content=content,
                snippet=_truncate(description, 200),
                relevance=relevance,
                timestamp=item.get("page_age"),
                metadata={
                    "language": item.get("language", ""),
                    "family_friendly": item.get("family_friendly", True),
                    "has_extra_snippets": bool(extra),
                },
            )
            results.append(result)

        logger.info("Brave: %d results for %r", len(results), query)
        return results

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
