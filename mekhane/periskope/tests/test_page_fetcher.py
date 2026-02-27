# PROOF: [L2/Periskope] <- mekhane/periskope/ Periskope Search Test Page Fetcher
"""
Tests for PageFetcher (W7: selective full-page crawling).
"""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from mekhane.periskope.page_fetcher import (
    PageFetcher,
    INTERNAL_SOURCES,
    BLOCKED_DOMAINS,
)


# ── Text Extraction Tests ──

def test_extract_text_with_trafilatura():
    """trafilatura should extract clean text from HTML."""
    html = """
    <html>
    <head><title>Test</title></head>
    <body>
        <nav>Navigation</nav>
        <article>
            <h1>Main Title</h1>
            <p>This is the main content of the article with enough text
            to meet the minimum content length requirement for extraction.</p>
            <p>Second paragraph with additional information about the topic
            that provides more context and detail for the reader.</p>
        </article>
        <footer>Footer content</footer>
    </body>
    </html>
    """
    fetcher = PageFetcher()
    text = fetcher._extract_text(html, url="https://example.com/test")

    # Should extract something (trafilatura's exact output varies)
    assert text is not None
    assert len(text) > 50


def test_extract_text_fallback_without_trafilatura():
    """Should fall back to basic HTML stripping if trafilatura unavailable."""
    html = """
    <html><body>
        <script>var x = 1;</script>
        <style>.foo { color: red; }</style>
        <p>This is important content that should survive basic extraction
        and provide enough text to pass the minimum length check.</p>
        <p>Additional paragraph to ensure sufficient content length for testing.</p>
    </body></html>
    """
    # Simulate trafilatura ImportError by monkey-patching
    import trafilatura as _real_traf
    import sys

    saved = sys.modules.get("trafilatura")
    sys.modules["trafilatura"] = None  # type: ignore

    try:
        # Call the static method — it should hit ImportError and fallback
        text = PageFetcher._extract_text(html, url="https://example.com")
        assert text is not None
        assert "important content" in text
    finally:
        sys.modules["trafilatura"] = saved


# ── Blocked Domains ──

@pytest.mark.asyncio
async def test_blocked_domains_skipped():
    """URLs from blocked domains should be skipped."""
    fetcher = PageFetcher()

    for domain in ["linkedin.com", "facebook.com", "twitter.com"]:
        result = await fetcher.fetch_one(f"https://www.{domain}/some-page")
        assert result is None, f"{domain} should be blocked"


# ── fetch_many ──

@pytest.mark.asyncio
async def test_fetch_many_empty():
    """Empty URL list should return empty dict."""
    fetcher = PageFetcher()
    result = await fetcher.fetch_many([])
    assert result == {}


@pytest.mark.asyncio
async def test_fetch_many_with_mock():
    """fetch_many should process multiple URLs concurrently."""
    fetcher = PageFetcher()

    # Mock fetch_one to return predictable results
    call_count = 0

    async def mock_fetch(url):
        nonlocal call_count
        call_count += 1
        if "good" in url:
            return f"Content from {url} " * 100
        return None

    with patch.object(fetcher, "fetch_one", side_effect=mock_fetch):
        result = await fetcher.fetch_many([
            "https://good.example.com/page1",
            "https://bad.example.com/page2",
            "https://good.example.com/page3",
        ])

    assert call_count == 3
    assert len(result) == 2  # Only "good" URLs
    assert "https://good.example.com/page1" in result
    assert "https://good.example.com/page3" in result
    assert "https://bad.example.com/page2" not in result


@pytest.mark.asyncio
async def test_fetch_many_concurrency_limit():
    """Concurrency should be limited by semaphore."""
    fetcher = PageFetcher()
    max_concurrent = 0
    current_concurrent = 0

    async def mock_fetch(url):
        nonlocal max_concurrent, current_concurrent
        current_concurrent += 1
        max_concurrent = max(max_concurrent, current_concurrent)
        await asyncio.sleep(0.05)
        current_concurrent -= 1
        return "content " * 100

    with patch.object(fetcher, "fetch_one", side_effect=mock_fetch):
        urls = [f"https://example.com/page{i}" for i in range(10)]
        await fetcher.fetch_many(urls, concurrency=3)

    assert max_concurrent <= 3, f"Max concurrency was {max_concurrent}, expected <= 3"


# ── INTERNAL_SOURCES ──

def test_internal_sources_constant():
    """INTERNAL_SOURCES should contain expected sources."""
    assert "gnosis" in INTERNAL_SOURCES
    assert "sophia" in INTERNAL_SOURCES
    assert "kairos" in INTERNAL_SOURCES
    assert "searxng" not in INTERNAL_SOURCES


# ── PageFetcher init ──

def test_fetcher_defaults():
    """PageFetcher should initialize with sensible defaults."""
    fetcher = PageFetcher()
    assert fetcher.timeout == 10.0
    assert fetcher.max_content_length == 15_000
    assert fetcher.min_content_length == 500
    assert fetcher.playwright_fallback is True


def test_fetcher_custom_config():
    """PageFetcher should accept custom configuration."""
    fetcher = PageFetcher(
        timeout=5.0,
        max_content_length=10_000,
        min_content_length=200,
        playwright_fallback=False,
    )
    assert fetcher.timeout == 5.0
    assert fetcher.max_content_length == 10_000
    assert fetcher.min_content_length == 200
    assert fetcher.playwright_fallback is False


# ── Cache ──

@pytest.mark.asyncio
async def test_cache_prevents_refetch():
    """Second fetch of same URL should use cache, not re-fetch."""
    fetcher = PageFetcher()
    fetch_count = 0

    async def mock_fetch(url):
        nonlocal fetch_count
        fetch_count += 1
        return "Cached content " * 100

    with patch.object(fetcher, "_fetch_httpx", side_effect=mock_fetch):
        result1 = await fetcher.fetch_one("https://example.com/cached")
        result2 = await fetcher.fetch_one("https://example.com/cached")

    assert fetch_count == 1  # Only fetched once
    assert result1 == result2  # Same content returned


# ── Content length filtering ──

@pytest.mark.asyncio
async def test_fetch_one_rejects_short_content():
    """Content shorter than min_content_length should be rejected."""
    fetcher = PageFetcher(min_content_length=500)

    # Mock httpx to return short content
    async def mock_fetch_httpx(url):
        return "Too short"

    with patch.object(fetcher, "_fetch_httpx", side_effect=mock_fetch_httpx):
        with patch.object(fetcher, "_fetch_playwright", return_value=None):
            result = await fetcher.fetch_one("https://example.com/short")

    assert result is None


@pytest.mark.asyncio
async def test_fetch_one_truncates_long_content():
    """Content longer than max_content_length should be truncated."""
    fetcher = PageFetcher(max_content_length=100, min_content_length=10)
    long_content = "x" * 500

    async def mock_fetch_httpx(url):
        return long_content

    with patch.object(fetcher, "_fetch_httpx", side_effect=mock_fetch_httpx):
        result = await fetcher.fetch_one("https://example.com/long")

    assert result is not None
    assert len(result) == 100
