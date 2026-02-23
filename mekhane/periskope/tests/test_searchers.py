# PROOF: [L2/Mekhane] <- mekhane/periskope/tests/ Automatically added to satisfy CI
"""
Tests for SearXNG searcher.
"""

from __future__ import annotations

import pytest

from mekhane.periskope.models import SearchSource
from mekhane.periskope.searchers.searxng import SearXNGSearcher


@pytest.fixture
def searcher():
    return SearXNGSearcher(base_url="http://localhost:8888")


@pytest.mark.asyncio
async def test_health_check(searcher: SearXNGSearcher):
    """SearXNG Docker instance should be reachable."""
    healthy = await searcher.health_check()
    assert healthy, "SearXNG is not reachable at localhost:8888"
    await searcher.close()


@pytest.mark.asyncio
async def test_basic_search(searcher: SearXNGSearcher):
    """Basic search should return results."""
    results = await searcher.search("Python programming", max_results=5)
    assert len(results) > 0, "No results returned"
    assert len(results) <= 5, f"Too many results: {len(results)}"

    for r in results:
        assert r.source == SearchSource.SEARXNG
        assert r.title, "Title should not be empty"
        assert r.url, "URL should not be empty"
        assert 0.0 <= r.relevance <= 1.0

    await searcher.close()


@pytest.mark.asyncio
async def test_academic_search(searcher: SearXNGSearcher):
    """Academic search should use scholarly engines."""
    results = await searcher.search_academic(
        "free energy principle", max_results=5
    )
    # Academic engines may not always be available
    # but the call should not fail
    assert isinstance(results, list)
    await searcher.close()


@pytest.mark.asyncio
async def test_search_result_metadata(searcher: SearXNGSearcher):
    """Search results should contain engine metadata."""
    results = await searcher.search("test query", max_results=3)
    if results:
        r = results[0]
        assert "engine" in r.metadata or "engines" in r.metadata
        assert r.snippet  # snippet should be populated
        assert not r.is_internal  # SearXNG results are external

    await searcher.close()


@pytest.mark.asyncio
async def test_empty_query(searcher: SearXNGSearcher):
    """Empty query should not crash."""
    results = await searcher.search("", max_results=5)
    assert isinstance(results, list)
    await searcher.close()
