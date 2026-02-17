# PROOF: [L3/Test] <- mekhane/periskope/tests/
# PURPOSE: Tests for PeriskopeEngine.

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mekhane.periskope.engine import PeriskopeEngine
from mekhane.periskope.models import PeriskopeConfig, SearchResult, SearchSource, SynthesisResult


@pytest.fixture
def mock_searxng():
    with patch("mekhane.periskope.engine.SearXNGSearcher") as mock_cls:
        instance = mock_cls.return_value
        # Configure async methods
        instance.search = AsyncMock()
        instance.close = AsyncMock()
        instance.health_check = AsyncMock(return_value=True)
        yield instance


@pytest.mark.asyncio
async def test_engine_initialization(mock_searxng):
    """Test engine initialization with default config."""
    engine = PeriskopeEngine()
    assert engine.config is not None
    await engine.close()
    mock_searxng.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_delegation(mock_searxng):
    """Test that search is correctly delegated to configured searchers."""
    config = PeriskopeConfig(
        search_sources=[SearchSource.SEARXNG],
        max_results_per_source=5
    )
    engine = PeriskopeEngine(config)

    expected_result = SearchResult(
        source=SearchSource.SEARXNG,
        title="Test Result",
        relevance=0.9
    )
    mock_searxng.search.return_value = [expected_result]

    results = await engine.search("test query")

    assert len(results) == 1
    assert results[0].title == "Test Result"
    mock_searxng.search.assert_awaited_once_with("test query", max_results=5)

    await engine.close()


@pytest.mark.asyncio
async def test_search_no_sources(mock_searxng):
    """Test search with no sources configured."""
    config = PeriskopeConfig(search_sources=[])
    engine = PeriskopeEngine(config)
    results = await engine.search("test")
    assert results == []
    await engine.close()


@pytest.mark.asyncio
async def test_synthesize_stub(mock_searxng):
    """Test synthesize stub."""
    engine = PeriskopeEngine()
    results = [
        SearchResult(source=SearchSource.SEARXNG, title="Test", relevance=0.5)
    ]
    synth_results = await engine.synthesize("query", results)

    assert len(synth_results) == 1
    assert "not implemented" in synth_results[0].content
    await engine.close()


@pytest.mark.asyncio
async def test_run_flow(mock_searxng):
    """Test the full run flow."""
    mock_searxng.search.return_value = [
        SearchResult(source=SearchSource.SEARXNG, title="Test", relevance=1.0)
    ]

    engine = PeriskopeEngine()
    report = await engine.run(query="test flow")

    assert report.query == "test flow"
    assert len(report.search_results) == 1
    assert len(report.synthesis_results) == 1
    assert report.total_sources == 1

    await engine.close()


@pytest.mark.asyncio
async def test_run_missing_query(mock_searxng):
    """Test run raises ValueError if no query is provided."""
    config = PeriskopeConfig(query="")
    engine = PeriskopeEngine(config)
    with pytest.raises(ValueError, match="No query provided"):
        await engine.run(query=None)
    await engine.close()
