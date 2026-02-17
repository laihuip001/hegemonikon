# PROOF: [S4/CitationAgentTest] <- mekhane/periskope/citation_agent.py
# PURPOSE: Test CitationAgent logic.

import pytest
from unittest.mock import AsyncMock, MagicMock

from mekhane.periskope.citation_agent import CitationAgent
from mekhane.periskope.models import Citation, SearchResult, TaintLevel, SearchSource

@pytest.fixture
def mock_searcher():
    searcher = AsyncMock()
    return searcher

@pytest.mark.asyncio
async def test_citation_verification_success(mock_searcher):
    """Citation verified successfully."""
    agent = CitationAgent(searcher=mock_searcher)

    citation = Citation(claim="Earth is round", source_url="https://nasa.gov")

    # Mock search result
    result = SearchResult(
        source=SearchSource.SEARXNG,
        title="Earth Fact Sheet",
        url="https://nasa.gov/earth",
        content="The Earth is round.",
        snippet="The Earth is round.",
        relevance=1.0,
        metadata={}
    )
    mock_searcher.search.return_value = [result]

    verified_list = await agent.verify_citations([citation])
    verified = verified_list[0]

    assert verified.taint_level == TaintLevel.SOURCE
    assert verified.similarity > 0.8
    mock_searcher.search.assert_called_once()

@pytest.mark.asyncio
async def test_citation_verification_failure(mock_searcher):
    """Citation verification fails (no results)."""
    agent = CitationAgent(searcher=mock_searcher)

    citation = Citation(claim="Fake claim", source_url="https://fake.com")
    mock_searcher.search.return_value = []

    verified_list = await agent.verify_citations([citation])
    verified = verified_list[0]

    assert verified.taint_level == TaintLevel.FABRICATED
    assert verified.similarity < 0.5
    mock_searcher.search.assert_called_once()
