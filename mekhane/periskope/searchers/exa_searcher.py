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

    T3: Adaptive pruning — tracks hit rates per category and
    automatically disables underperforming categories.
    """

    def __init__(self, min_hit_rate: float = 0.1) -> None:
        # T3: Category hit-rate tracking {category: (hits, attempts)}
        self._hit_stats: dict[str, tuple[int, int]] = {}
        self._min_hit_rate = min_hit_rate

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

    async def search_multi_category(
        self,
        query: str,
        max_results: int = 10,
        weights: dict[str, float] | None = None,
    ) -> list[SearchResult]:
        """W2: Search across multiple Exa categories in parallel.

        Runs general, research paper, github, news, tweet, pdf,
        and personal site searches concurrently, then merges and
        deduplicates results.

        T3: Adaptive pruning — categories with hit rate below
        min_hit_rate are automatically skipped.

        Args:
            query: Search query.
            max_results: Total max results across all categories.
            weights: Category weights for result allocation.
                Keys: "general", "paper", "github", "news", "tweet",
                      "pdf", "personal_site".
                Default: general=0.3, paper=0.25, github=0.15,
                         news=0.15, tweet=0.05, pdf=0.05, personal_site=0.05

        Returns:
            Merged and deduplicated results.
        """
        # Default weights for 7 categories
        default_weights = {
            "general": 0.30,
            "paper": 0.25,
            "github": 0.15,
            "news": 0.15,
            "tweet": 0.05,
            "pdf": 0.05,
            "personal_site": 0.05,
        }
        w = default_weights.copy()
        if weights:
            w.update(weights)

        # Exa category name mapping (config key -> API value)
        category_map = {
            "general": "general",
            "paper": "research paper",
            "github": "github",
            "news": "news",
            "tweet": "tweet",
            "pdf": "pdf",
            "personal_site": "personal site",
        }

        # Build tasks for categories with weight > 0
        tasks = []
        category_names = []
        for key, exa_cat in category_map.items():
            weight = w.get(key, 0)
            if weight <= 0:
                continue

            # T3: Adaptive pruning — skip categories with low hit rate
            hits, attempts = self._hit_stats.get(key, (0, 0))
            if attempts >= 3:  # Need at least 3 attempts to judge
                hit_rate = hits / attempts
                if hit_rate < self._min_hit_rate:
                    logger.info(
                        "  Exa [%s]: PRUNED (hit_rate=%.2f < %.2f, %d/%d)",
                        key, hit_rate, self._min_hit_rate, hits, attempts,
                    )
                    continue

            n = max(2, int(max_results * weight))
            # Use neural for academic, auto for others
            stype = "neural" if key == "paper" else "auto"
            tasks.append(
                self.search(query, max_results=n, category=exa_cat, search_type=stype)
            )
            category_names.append(key)

        all_results: list[SearchResult] = []
        category_results = await asyncio.gather(*tasks, return_exceptions=True)

        for cat_name, result in zip(category_names, category_results):
            if isinstance(result, list):
                all_results.extend(result)
                # T3: Update hit stats
                hits, attempts = self._hit_stats.get(cat_name, (0, 0))
                self._hit_stats[cat_name] = (hits + len(result), attempts + 1)
                logger.info("  Exa [%s]: %d results", cat_name, len(result))
            elif isinstance(result, Exception):
                # T3: Count failures as attempts with 0 hits
                hits, attempts = self._hit_stats.get(cat_name, (0, 0))
                self._hit_stats[cat_name] = (hits, attempts + 1)
                logger.warning("  Exa [%s]: FAILED — %s", cat_name, result)

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

        deduped.sort(key=lambda r: r.relevance, reverse=True)
        result_list = deduped[:max_results]

        logger.info(
            "Exa multi-category: %d results (from %d raw, %d categories)",
            len(result_list), len(all_results), len(category_names),
        )
        return result_list

    def get_hit_rates(self) -> dict[str, float]:
        """T3: Return current hit rates per category.

        Returns:
            Dict of {category: hit_rate}. Empty categories not included.
        """
        rates = {}
        for cat, (hits, attempts) in self._hit_stats.items():
            if attempts > 0:
                rates[cat] = hits / attempts
        return rates


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
