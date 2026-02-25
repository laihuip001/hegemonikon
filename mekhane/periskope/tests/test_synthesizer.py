# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI
"""
Tests for multi-model synthesizer.
"""

from __future__ import annotations

import pytest

from mekhane.periskope.models import (
    SearchResult,
    SearchSource,
    SynthModel,
    DivergenceReport,
    SynthesisResult,
    TaintLevel,
)
from mekhane.periskope.synthesizer import MultiModelSynthesizer


# ── Unit Tests (no API calls) ──

def test_format_results():
    """Results should be formatted with source tags and content."""
    synth = MultiModelSynthesizer()
    results = [
        SearchResult(
            source=SearchSource.SEARXNG,
            title="Test Paper 1",
            url="https://example.com/1",
            content="This is the content of paper 1.",
        ),
        SearchResult(
            source=SearchSource.GNOSIS,
            title="Test Paper 2",
            content="This is the content of paper 2.",
        ),
    ]
    formatted = synth._format_results(results)
    assert "[Source 1]" in formatted
    assert "[Source 2]" in formatted
    assert "[searxng]" in formatted
    assert "[gnosis]" in formatted
    assert "Test Paper 1" in formatted


def test_extract_citations():
    """Citations should be extracted from [Source N] references."""
    synth = MultiModelSynthesizer()
    text = """
    According to [Source 1], the FEP is important.
    This is confirmed by [Source 3] and [Source 1] again.
    """
    citations = synth._extract_citations(text)
    assert len(citations) == 2  # Source 1 and Source 3 (deduped)
    assert citations[0].taint_level == TaintLevel.UNCHECKED


def test_extract_confidence():
    """Confidence should be extracted from text."""
    synth = MultiModelSynthesizer()
    assert synth._extract_confidence("Confidence: 85%") == 0.85
    assert synth._extract_confidence("Confidence: 100%") == 1.0
    assert synth._extract_confidence("No confidence here") == 0.5


def test_divergence_single_model():
    """Single model should return agreement=1.0."""
    synth = MultiModelSynthesizer()
    results = [
        SynthesisResult(
            model=SynthModel.GEMINI_FLASH,
            content="Test",
            confidence=0.8,
        ),
    ]
    report = synth.detect_divergence(results)
    assert report.agreement_score == 1.0
    assert len(report.divergent_claims) == 0


def test_divergence_two_models():
    """Two models with different confidence should detect divergence."""
    synth = MultiModelSynthesizer()
    results = [
        SynthesisResult(model=SynthModel.GEMINI_FLASH, content="A", confidence=0.9),
        SynthesisResult(model=SynthModel.GEMINI_PRO, content="B", confidence=0.5),
    ]
    report = synth.detect_divergence(results)
    assert report.agreement_score < 1.0
    assert len(report.models_compared) == 2


# ── Integration Test (requires Cortex API) ──

@pytest.mark.asyncio
async def test_gemini_synthesis():
    """Gemini synthesis should produce a result via Cortex API."""
    synth = MultiModelSynthesizer(
        synth_models=[SynthModel.GEMINI_FLASH],
        max_tokens=1024,
    )
    search_results = [
        SearchResult(
            source=SearchSource.SEARXNG,
            title="Free Energy Principle Overview",
            content="The FEP states that biological systems minimize variational free energy.",
        ),
        SearchResult(
            source=SearchSource.GNOSIS,
            title="Active Inference Framework",
            content="Active inference extends the FEP to action selection via expected free energy.",
        ),
    ]

    results = await synth.synthesize(
        query="Free Energy Principle",
        search_results=search_results,
    )

    assert len(results) >= 1
    result = results[0]
    assert result.model == SynthModel.GEMINI_FLASH
    assert len(result.content) > 100  # Should have substantive output
    assert result.confidence > 0.0
