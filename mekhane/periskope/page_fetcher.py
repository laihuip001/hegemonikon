# PROOF: [L2/Mekhane] <- mekhane/periskope/page_fetcher.py Auto-generated proof
"""
Page Fetcher — 選択的全文クロール for Periskopē.

サマリ→本文パターン: 合成が「深読みすべき」と判断した URL のみ全文取得。
httpx でフェッチ → trafilatura で本文抽出。
JS 必須ページは PlaywrightSearcher にフォールバック。
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Internal sources — already have full content, no crawling needed
INTERNAL_SOURCES = {"gnosis", "sophia", "kairos"}

# Domains that block bots or are unreliable
BLOCKED_DOMAINS = {
    "linkedin.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
}


class PageFetcher:
    """Fetch and extract full text from web pages.

    Strategy:
      1. httpx GET → trafilatura extract (fast, lightweight)
      2. If httpx fails or JS required → PlaywrightSearcher fallback
    """

    def __init__(
        self,
        timeout: float = 10.0,
        max_content_length: int = 15_000,
        min_content_length: int = 500,
        playwright_fallback: bool = True,
    ) -> None:
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.min_content_length = min_content_length
        self.playwright_fallback = playwright_fallback
        self._playwright = None  # Lazy-init
        self._cache: dict[str, str | None] = {}  # URL → content cache

    async def fetch_one(self, url: str) -> str | None:
        """Fetch a single URL and extract text content.

        Returns:
            Extracted text content, or None on failure.
        """
        # Cache check — avoid re-fetching same URL in multi-pass
        if url in self._cache:
            logger.debug("Cache hit for %s", url[:60])
            return self._cache[url]

        # Skip blocked domains
        for domain in BLOCKED_DOMAINS:
            if domain in url:
                logger.debug("Skipping blocked domain: %s", url[:60])
                self._cache[url] = None
                return None

        # Try httpx + trafilatura first (fast path)
        text = await self._fetch_httpx(url)
        if text and len(text) >= self.min_content_length:
            result = text[:self.max_content_length]
            self._cache[url] = result
            return result

        # Fallback to Playwright for JS-rendered pages
        if self.playwright_fallback:
            text = await self._fetch_playwright(url)
            if text and len(text) >= self.min_content_length:
                result = text[:self.max_content_length]
                self._cache[url] = result
                return result

        self._cache[url] = None
        return None

    async def fetch_many(
        self,
        urls: list[str],
        concurrency: int = 5,
    ) -> dict[str, str]:
        """Fetch multiple URLs in parallel with concurrency limit.

        Args:
            urls: URLs to fetch.
            concurrency: Maximum concurrent fetches.

        Returns:
            Mapping of URL → extracted text (only successful fetches).
        """
        sem = asyncio.Semaphore(concurrency)

        async def _limited_fetch(url: str) -> tuple[str, str | None]:
            async with sem:
                text = await self.fetch_one(url)
                return url, text

        tasks = [_limited_fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        fetched: dict[str, str] = {}
        for result in results:
            if isinstance(result, tuple):
                url, text = result
                if text:
                    fetched[url] = text
            elif isinstance(result, Exception):
                logger.debug("Fetch exception: %s", result)

        logger.info(
            "PageFetcher: %d/%d URLs fetched successfully",
            len(fetched), len(urls),
        )
        return fetched

    async def _fetch_httpx(self, url: str) -> str | None:
        """Fast path: httpx GET + content-type routing.

        Supports HTML (trafilatura) and PDF (pymupdf) extraction.
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                    ),
                },
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")

                # PDF extraction
                if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                    text = self._extract_pdf(response.content)
                    if text:
                        logger.debug(
                            "httpx+pymupdf: %d chars from %s",
                            len(text), url[:60],
                        )
                    return text

                # HTML extraction
                if "text/html" not in content_type and "text/plain" not in content_type:
                    logger.debug("Unsupported content type: %s for %s", content_type, url[:60])
                    return None

                html = response.text

            # Extract main text with trafilatura
            text = self._extract_text(html, url)
            if text:
                logger.debug(
                    "httpx+trafilatura: %d chars from %s",
                    len(text), url[:60],
                )
            return text

        except httpx.HTTPStatusError as e:
            logger.debug("HTTP %d for %s", e.response.status_code, url[:60])
            return None
        except Exception as e:
            logger.debug("httpx fetch failed for %s: %s", url[:60], e)
            return None

    @staticmethod
    def _extract_pdf(pdf_bytes: bytes) -> str | None:
        """Extract text from PDF bytes using pymupdf.

        Returns None if pymupdf is not installed or extraction fails.
        """
        try:
            import pymupdf
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            pages = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    pages.append(text.strip())
            doc.close()
            if pages:
                return "\n\n".join(pages)
            return None
        except ImportError:
            logger.debug("pymupdf not installed — PDF extraction unavailable")
            return None
        except Exception as e:
            logger.debug("PDF extraction failed: %s", e)
            return None

    @staticmethod
    def _extract_text(html: str, url: str = "") -> str | None:
        """Extract main text from HTML using trafilatura.

        Falls back to basic tag stripping if trafilatura is unavailable.
        """
        try:
            import trafilatura
            text = trafilatura.extract(
                html,
                url=url,
                include_comments=False,
                include_tables=True,
                include_formatting=True,  # Preserve heading structure (Markdown)
                favor_recall=True,
            )
            return text
        except ImportError:
            logger.warning(
                "trafilatura not installed — falling back to basic extraction. "
                "Install with: pip install trafilatura"
            )
            # Basic fallback: strip HTML tags
            import re
            text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text if len(text) > 100 else None
        except Exception as e:
            logger.debug("trafilatura extraction failed: %s", e)
            return None

    async def _fetch_playwright(self, url: str) -> str | None:
        """Fallback: use Playwright for JS-rendered pages."""
        try:
            if self._playwright is None:
                from mekhane.periskope.searchers.playwright_searcher import PlaywrightSearcher
                self._playwright = PlaywrightSearcher(timeout=self.timeout)

            text = await self._playwright.fetch_page(url)
            if text:
                logger.debug(
                    "Playwright fallback: %d chars from %s",
                    len(text), url[:60],
                )
            return text
        except Exception as e:
            logger.debug("Playwright fallback failed for %s: %s", url[:60], e)
            return None
