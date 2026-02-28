"""
Tests for Citation Agent.
"""

from __future__ import annotations

import pytest
from mekhane.periskope.models import Citation, TaintLevel, SearchResult, SearchSource
from mekhane.periskope.citation_agent import CitationAgent


# ── Unit Tests ──

def test_compute_similarity_exact():
    """Exact substring should return 1.0."""
    agent = CitationAgent()
    result = agent._compute_similarity(
        "the cat sat on the mat",
        "Once upon a time, the cat sat on the mat and slept.",
    )
    assert result == 1.0


def test_compute_similarity_partial():
    """Partial match should return intermediate score."""
    agent = CitationAgent()
    result = agent._compute_similarity(
        "the FEP minimizes free energy",
        "The Free Energy Principle states organisms minimize variational free energy.",
    )
    assert 0.0 < result < 1.0


def test_compute_similarity_none():
    """No match should return low score."""
    agent = CitationAgent()
    result = agent._compute_similarity(
        "quantum gravity unification theory",
        "This paper discusses baking techniques for sourdough bread.",
    )
    assert result < 0.3


def test_extract_claims():
    """Should extract claims with [Source N] references."""
    agent = CitationAgent()
    text = (
        "According to [Source 1], the FEP is a fundamental principle. "
        "This is supported by [Source 2] which confirms active inference. "
        "Some unrelated text without sources."
    )
    results = [
        SearchResult(source=SearchSource.SEARXNG, title="A", url="https://a.com", content=""),
        SearchResult(source=SearchSource.GNOSIS, title="B", url="https://b.com", content=""),
    ]
    citations = agent.extract_claims_from_synthesis(text, results)
    assert len(citations) >= 2
    # Should map to correct URLs
    urls = [c.source_url for c in citations]
    assert "https://a.com" in urls
    assert "https://b.com" in urls


def test_extract_claims_no_refs():
    """Text without [Source N] should produce no citations."""
    agent = CitationAgent()
    text = "This is plain text without any citations or references."
    citations = agent.extract_claims_from_synthesis(text)
    assert citations == []


@pytest.mark.asyncio
async def test_verify_with_content():
    """Verification with pre-fetched content should classify correctly."""
    agent = CitationAgent()
    citations = [
        Citation(
            claim="the FEP minimizes free energy",
            source_url="https://example.com/fep",
            taint_level=TaintLevel.UNCHECKED,
        ),
    ]
    source_contents = {
        "https://example.com/fep": (
            "The Free Energy Principle (FEP) states that biological "
            "systems minimize free energy to maintain homeostasis."
        ),
    }
    verified = await agent.verify_citations(citations, source_contents)
    assert len(verified) == 1
    assert verified[0].taint_level in (TaintLevel.SOURCE, TaintLevel.TAINT)
    assert verified[0].similarity is not None
    assert verified[0].similarity > 0.3


@pytest.mark.asyncio
async def test_verify_no_url():
    """Citation without URL should be TAINT."""
    agent = CitationAgent()
    citations = [
        Citation(claim="some claim", source_url="", taint_level=TaintLevel.UNCHECKED),
    ]
    verified = await agent.verify_citations(citations)
    assert verified[0].taint_level == TaintLevel.TAINT
    assert "No source URL" in verified[0].verification_note


@pytest.mark.asyncio
async def test_verify_no_claim():
    """Citation without claim should be UNCHECKED."""
    agent = CitationAgent()
    citations = [
        Citation(claim="", source_url="https://a.com", taint_level=TaintLevel.UNCHECKED),
    ]
    verified = await agent.verify_citations(citations)
    assert verified[0].taint_level == TaintLevel.UNCHECKED


@pytest.mark.asyncio
async def test_verify_fabricated():
    """Completely unrelated claim should be FABRICATED."""
    agent = CitationAgent()
    citations = [
        Citation(
            claim="quantum gravity unifies all forces in the universe",
            source_url="https://example.com/bread",
            taint_level=TaintLevel.UNCHECKED,
        ),
    ]
    source_contents = {
        "https://example.com/bread": (
            "This recipe uses sourdough starter, flour, water, and salt "
            "to create a delicious artisan bread with a crispy crust."
        ),
    }
    verified = await agent.verify_citations(citations, source_contents)
    assert verified[0].taint_level == TaintLevel.FABRICATED
