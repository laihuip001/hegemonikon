# PROOF: [L2/Mekhanē] <- mekhane/periskope/tests/test_engine.py S2->test
# PURPOSE: Test Periskopē Engine implementation.

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mekhane.periskope.engine import PeriskopeEngine
from mekhane.periskope.models import PeriskopeConfig, SearchResult, SearchSource


@pytest.mark.asyncio
async def test_engine_initialization():
    with patch("mekhane.periskope.engine.SearXNGSearcher") as MockSearXNG, \
         patch("mekhane.periskope.engine.ExaSearcher"), \
         patch("mekhane.periskope.engine.GnosisSearcher"), \
         patch("mekhane.periskope.engine.SophiaSearcher"), \
         patch("mekhane.periskope.engine.KairosSearcher"):

        # Configure SearXNG mock to have async close
        mock_searxng = MockSearXNG.return_value
        mock_searxng.close = AsyncMock()

        engine = PeriskopeEngine()
        assert engine.searxng is not None
        assert engine.exa is not None
        await engine.close()


@pytest.mark.asyncio
async def test_engine_run_search():
    # Mock searchers
    with patch("mekhane.periskope.engine.SearXNGSearcher") as MockSearXNG, \
         patch("mekhane.periskope.engine.ExaSearcher") as MockExa, \
         patch("mekhane.periskope.engine.GnosisSearcher"), \
         patch("mekhane.periskope.engine.SophiaSearcher"), \
         patch("mekhane.periskope.engine.KairosSearcher"):

        # Setup mocks
        mock_searxng = MockSearXNG.return_value
        mock_searxng.search = AsyncMock()
        mock_searxng.search.return_value = [
            SearchResult(source=SearchSource.SEARXNG, title="R1", relevance=0.9, url="http://r1")
        ]
        mock_searxng.close = AsyncMock()

        mock_exa = MockExa.return_value
        mock_exa.search = AsyncMock()
        mock_exa.search.return_value = [
            SearchResult(source=SearchSource.EXA, title="R2", relevance=0.8, url="http://r2")
        ]

        engine = PeriskopeEngine()

        config = PeriskopeConfig(
            query="test",
            search_sources=[SearchSource.SEARXNG, SearchSource.EXA]
        )

        report = await engine.run(config)

        assert report.query == "test"
        assert len(report.search_results) == 2

        # Verify calls
        mock_searxng.search.assert_called_once()
        mock_exa.search.assert_called_once()

        await engine.close()
