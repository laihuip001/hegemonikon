# PROOF: [L2/Mekhane] <- mekhane/periskope/searchers/playwright_searcher.py Axiom->Reason->Module
"""
Playwright-based searcher for Periskopē.

W5: Renders dynamic/SPA pages via Playwright to extract text content
when traditional HTTP fetching fails (e.g., JavaScript-rendered pages).
Primarily used as a fallback for citation chain verification.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)


class PlaywrightSearcher:
    """Search by rendering dynamic pages via Playwright.

    Unlike SearXNG/Exa which perform query-based search,
    this searcher extracts content from specific URLs.
    Used as a fallback when httpx fails to fetch JS-rendered pages.
    """

    def __init__(
        self,
        timeout: float = 30.0,
        headless: bool = True,
    ) -> None:
        self.timeout = timeout
        self.headless = headless

    async def fetch_page(self, url: str) -> str | None:
        """Render a page and extract text content.

        Args:
            url: URL to render.

        Returns:
            Extracted text content, or None on failure.
        """
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle", timeout=int(self.timeout * 1000))

                # Extract main text content
                content = await page.evaluate("""
                    () => {
                        // Remove script/style/nav elements
                        const removeSelectors = ['script', 'style', 'nav', 'footer', 'header'];
                        removeSelectors.forEach(sel => {
                            document.querySelectorAll(sel).forEach(el => el.remove());
                        });
                        return document.body.innerText || '';
                    }
                """)

                await browser.close()

                if content and len(content.strip()) > 50:
                    logger.info("Playwright: extracted %d chars from %s", len(content), url[:60])
                    return content.strip()
                return None

        except ImportError:
            logger.warning("Playwright not installed, fetch_page unavailable")
            return None
        except Exception as e:
            logger.warning("Playwright fetch failed for %s: %s", url[:60], e)
            return None

    async def search(
        self,
        query: str,
        urls: list[str],
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Render target URLs and extract text content.

        Unlike query-based searchers, this takes explicit URLs
        and extracts their text via Playwright rendering.

        Args:
            query: Original query (for metadata).
            urls: List of URLs to render.
            max_results: Maximum results to return.

        Returns:
            List of SearchResult from rendered pages.
        """
        results: list[SearchResult] = []
        tasks = [self.fetch_page(url) for url in urls[:max_results]]

        fetched = await asyncio.gather(*tasks, return_exceptions=True)

        for url, content in zip(urls, fetched):
            if isinstance(content, str) and content:
                result = SearchResult(
                    source=SearchSource.PLAYWRIGHT,
                    title=f"[Rendered] {url[:80]}",
                    url=url,
                    content=content[:5000],
                    snippet=content[:200],
                    relevance=0.5,  # Neutral — reranker will adjust
                    metadata={"renderer": "playwright"},
                )
                results.append(result)
            elif isinstance(content, Exception):
                logger.debug("Playwright failed for %s: %s", url[:60], content)

        logger.info(
            "Playwright: %d/%d URLs rendered successfully",
            len(results), len(urls),
        )
        return results
