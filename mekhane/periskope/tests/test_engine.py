# PROOF: [L2/Mekhane] <- mekhane/tests/ A0→Implementation required→test_engine.py provides functionality
"""
Tests for Periskopē Engine (orchestrator).
"""

from __future__ import annotations

import pytest
from mekhane.periskope.engine import PeriskopeEngine, ResearchReport
from mekhane.periskope.models import (
    SearchResult,
    SearchSource,
    SynthesisResult,
    SynthModel,
    Citation,
    TaintLevel,
    DivergenceReport,
)


# ── ResearchReport Tests ──

def test_report_markdown_empty():
    """Empty report should produce valid markdown."""
    report = ResearchReport(query="test", elapsed_seconds=1.5)
    md = report.markdown()
    assert "# Periskopē Research Report" in md
    assert "test" in md
    assert "1.5s" in md


def test_report_markdown_with_results():
    """Report with all phases should produce complete markdown."""
    report = ResearchReport(
        query="FEP",
        search_results=[
            SearchResult(source=SearchSource.GNOSIS, title="Paper A", content="..."),
            SearchResult(source=SearchSource.SEARXNG, title="Web B", content="..."),
        ],
        synthesis=[
            SynthesisResult(
                model=SynthModel.GEMINI_FLASH,
                content="The FEP is a fundamental principle.",
                confidence=0.85,
            ),
        ],
        citations=[
            Citation(
                claim="FEP is fundamental",
                source_url="https://a.com",
                taint_level=TaintLevel.SOURCE,
                similarity=0.92,
                verification_note="Verified: 92% match",
            ),
        ],
        divergence=DivergenceReport(
            models_compared=[SynthModel.GEMINI_FLASH],
            agreement_score=1.0,
            divergent_claims=[],
            consensus_claims=["Single model"],
        ),
        elapsed_seconds=3.2,
        source_counts={"gnosis": 1, "searxng": 1},
    )
    md = report.markdown()
    assert "## Sources" in md
    assert "## Synthesis" in md
    assert "## Citation Verification" in md
    assert "SOURCE" in md


# ── Engine Unit Tests ──

def test_engine_init():
    """Engine should initialize with default configuration."""
    engine = PeriskopeEngine()
    assert engine.max_results == 10
    assert engine.verify_citations is True


# ── Engine Integration Test (uses real APIs) ──

@pytest.mark.asyncio
async def test_engine_research_internal_only():
    """Research with internal sources only should work without Docker."""
    engine = PeriskopeEngine(verify_citations=False)
    report = await engine.research(
        query="free energy principle",
        sources=["gnosis", "sophia"],
    )
    assert isinstance(report, ResearchReport)
    assert report.query == "free energy principle"
    assert report.elapsed_seconds > 0
    # Should have some results from internal knowledge
    assert isinstance(report.search_results, list)


@pytest.mark.asyncio
async def test_engine_research_full():
    """Full research pipeline (all sources + synthesis + verification)."""
    engine = PeriskopeEngine(
        max_results_per_source=3,
        verify_citations=True,
    )
    report = await engine.research(
        query="active inference framework",
        sources=["gnosis", "sophia", "kairos"],
    )
    assert isinstance(report, ResearchReport)
    md = report.markdown()
    assert len(md) > 100  # Should produce substantive output
