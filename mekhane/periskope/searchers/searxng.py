# PROOF: [L2/Mekhanē] <- mekhane/periskope/PROOF.md S2->Periskopē->searchers->searxng
# PURPOSE: SearXNG search client implementation.

"""
SearXNG search client for Periskopē.

Connects to a self-hosted SearXNG instance to aggregate results
from 70+ search engines (Google, Bing, DuckDuckGo, Brave, etc.).
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlencode

import httpx

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)

# Default SearXNG categories
CATEGORY_GENERAL = "general"
CATEGORY_SCIENCE = "science"
CATEGORY_NEWS = "news"
CATEGORY_IT = "it"


class SearXNGSearcher:
    """Client for SearXNG meta-search engine.

    SearXNG aggregates 70+ search engines into a single API.
    Results are returned in JSON format with relevance scoring.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8888",
        timeout: float = 30.0,
        default_lang: str = "ja-JP",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_lang = default_lang
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def search(
        self,
        query: str,
        categories: list[str] | None = None,
        max_results: int = 20,
        language: str | None = None,
        time_range: str | None = None,
        engines: list[str] | None = None,
    ) -> list[SearchResult]:
        """Execute a search against SearXNG.

        Args:
            query: Search query string.
            categories: SearXNG categories (general, science, news, it).
            max_results: Maximum number of results to return.
            language: Language code (default: ja-JP).
            time_range: Time filter (day, week, month, year).
            engines: Specific engines to use (google, bing, etc.).

        Returns:
            List of SearchResult objects.
        """
        params: dict[str, str] = {
            "q": query,
            "format": "json",
            "language": language or self.default_lang,
        }

        if categories:
            params["categories"] = ",".join(categories)
        if time_range:
            params["time_range"] = time_range
        if engines:
            params["engines"] = ",".join(engines)

        url = f"{self.base_url}/search?{urlencode(params)}"

        try:
            client = await self._get_client()
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.error("SearXNG search failed: %s", e)
            return []
        except Exception as e:
            logger.error("Unexpected error during SearXNG search: %s", e)
            return []

        results = []
        raw_results = data.get("results", [])

        for i, item in enumerate(raw_results[:max_results]):
            result = SearchResult(
                source=SearchSource.SEARXNG,
                title=item.get("title", ""),
                url=item.get("url"),
                content=item.get("content", ""),
                snippet=_truncate(item.get("content", ""), 200),
                relevance=_calculate_relevance(i, len(raw_results)),
                timestamp=item.get("publishedDate"),
                metadata={
                    "engine": item.get("engine", ""),
                    "engines": item.get("engines", []),
                    "category": item.get("category", ""),
                    "score": item.get("score", 0.0),
                },
            )
            results.append(result)

        logger.info(
            "SearXNG: %d results for %r (from %d total)",
            len(results),
            query,
            data.get("number_of_results", 0),
        )

        return results

    async def search_academic(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search academic sources (Google Scholar, Semantic Scholar, arXiv)."""
        return await self.search(
            query=query,
            categories=[CATEGORY_SCIENCE],
            max_results=max_results,
            engines=["google scholar", "semantic scholar", "arxiv"],
        )

    async def search_news(
        self,
        query: str,
        max_results: int = 10,
        time_range: str = "week",
    ) -> list[SearchResult]:
        """Search news sources."""
        return await self.search(
            query=query,
            categories=[CATEGORY_NEWS],
            max_results=max_results,
            time_range=time_range,
        )

    async def health_check(self) -> bool:
        """Check if SearXNG is reachable."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/search?q=ping&format=json")
            return response.status_code == 200
        except Exception:
            return False


def _calculate_relevance(index: int, total: int) -> float:
    """Calculate relevance score based on position (0-indexed)."""
    if total == 0:
        return 0.0
    return max(0.0, 1.0 - (index / max(total, 1)))


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len characters."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
