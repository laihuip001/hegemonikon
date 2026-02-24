# PROOF: [L2/Mekhane] <- mekhane/periskope/searchers/ A0→Implementation→searxng
"""
SearXNG search client for Periskopē.

Connects to a self-hosted SearXNG instance to aggregate results
from 70+ search engines (Google, Bing, DuckDuckGo, Brave, etc.).
"""

from __future__ import annotations

import asyncio
import logging
import re
from urllib.parse import urlencode, urlparse

import httpx

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)

# Default SearXNG categories
CATEGORY_GENERAL = "general"
CATEGORY_SCIENCE = "science"
CATEGORY_NEWS = "news"
CATEGORY_IT = "it"

# Domain blacklist — known noise sources irrelevant to research
DOMAIN_BLACKLIST: set[str] = {
    "hotstar.com",
    "www.hotstar.com",
    "tiktok.com",
    "www.tiktok.com",
    "instagram.com",
    "www.instagram.com",
    "facebook.com",
    "www.facebook.com",
    "pinterest.com",
    "www.pinterest.com",
}


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
        min_score: float = 0.0,
        domain_blacklist: set[str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_lang = default_lang
        self.min_score = min_score
        self.domain_blacklist = domain_blacklist or DOMAIN_BLACKLIST
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
        # Preprocess query
        processed_query = self._preprocess_query(query)

        params: dict[str, str] = {
            "q": processed_query,
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

        for i, item in enumerate(raw_results[:max_results * 2]):  # over-fetch for filtering
            url_str = item.get("url", "")

            # Filter blacklisted domains
            if self._is_blacklisted(url_str):
                logger.debug("Filtered blacklisted URL: %s", url_str)
                continue

            relevance = _calculate_relevance(i, len(raw_results))

            # Filter low-score results
            if relevance < self.min_score:
                continue

            result = SearchResult(
                source=SearchSource.SEARXNG,
                title=item.get("title", ""),
                url=url_str or None,
                content=item.get("content", ""),
                snippet=_truncate(item.get("content", ""), 200),
                relevance=relevance,
                timestamp=item.get("publishedDate"),
                metadata={
                    "engine": item.get("engine", ""),
                    "engines": item.get("engines", []),
                    "category": item.get("category", ""),
                    "score": item.get("score", 0.0),
                },
            )
            results.append(result)

            if len(results) >= max_results:
                break

        logger.info(
            "SearXNG: %d results for %r (from %d total, %d filtered)",
            len(results),
            query,
            data.get("number_of_results", 0),
            len(raw_results) - len(results),
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

    async def search_multi_category(
        self,
        query: str,
        max_results: int = 20,
        weights: dict[str, float] | None = None,
    ) -> list[SearchResult]:
        """W1: Search across 4 categories in parallel.

        Runs general, science, it, and news searches concurrently,
        then merges and deduplicates results.

        Args:
            query: Search query.
            max_results: Total max results across all categories.
            weights: Category weights for result allocation.
                Keys: "general", "science", "it", "news". Values sum to 1.0.
                Default: {"general": 0.4, "science": 0.2, "it": 0.2, "news": 0.2}

        Returns:
            Merged and deduplicated results.
        """
        w = weights or {"general": 0.4, "science": 0.2, "it": 0.2, "news": 0.2}
        n_general = max(3, int(max_results * w.get("general", 0.4)))
        n_science = max(3, int(max_results * w.get("science", 0.2)))
        n_it = max(3, int(max_results * w.get("it", 0.2)))
        n_news = max(3, int(max_results * w.get("news", 0.2)))

        tasks = [
            self.search(query, categories=["general"], max_results=n_general),
            self.search_academic(query, max_results=n_science),
            self.search(query, categories=["it"], max_results=n_it),
            self.search_news(query, max_results=n_news, time_range="month"),
        ]

        all_results: list[SearchResult] = []
        category_results = await asyncio.gather(*tasks, return_exceptions=True)

        category_names = ["general", "science", "it", "news"]
        for cat_name, result in zip(category_names, category_results):
            if isinstance(result, list):
                all_results.extend(result)
                logger.info("  SearXNG [%s]: %d results", cat_name, len(result))
            elif isinstance(result, Exception):
                logger.warning("  SearXNG [%s]: FAILED — %s", cat_name, result)

        # Deduplicate by URL
        seen: set[str] = set()
        deduped: list[SearchResult] = []
        for r in all_results:
            key = (r.url or "").lower().rstrip("/")
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            deduped.append(r)

        # Sort by relevance and trim
        deduped.sort(key=lambda r: r.relevance, reverse=True)
        result_list = deduped[:max_results]

        logger.info(
            "SearXNG multi-category: %d results (from %d raw, %d deduped)",
            len(result_list), len(all_results), len(all_results) - len(deduped),
        )
        return result_list

    def _preprocess_query(self, query: str) -> str:
        """Preprocess search query for better results.

        - Strips excessive whitespace
        - Removes common noise words for academic queries
        """
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        return query

    def _is_blacklisted(self, url: str) -> bool:
        """Check if URL domain is in the blacklist."""
        if not url:
            return False
        try:
            domain = urlparse(url).hostname or ""
            return domain in self.domain_blacklist
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

