# PROOF: [L2/Periskope] <- mekhane/periskope/tests/test_internal_searchers.py A0→AutoFix
"""
Tests for internal searchers (Gnōsis, Sophia, Kairos).
"""

from __future__ import annotations

import pytest
from pathlib import Path

from mekhane.periskope.models import SearchSource
from mekhane.periskope.searchers.internal_searcher import (
    GnosisSearcher,
    SophiaSearcher,
    KairosSearcher,
)


# ── Gnōsis Tests ──

@pytest.mark.asyncio
async def test_gnosis_search():
    """Gnōsis should return results from the paper index."""
    searcher = GnosisSearcher()
    results = await searcher.search("free energy principle", max_results=5)
    # Index may or may not have papers; test should not crash
    assert isinstance(results, list)
    for r in results:
        assert r.source == SearchSource.GNOSIS
        assert r.title


@pytest.mark.asyncio
async def test_gnosis_search_with_filter():
    """Gnōsis search with source filter should not crash."""
    searcher = GnosisSearcher()
    results = await searcher.search(
        "attention mechanism", max_results=3, source_filter="arxiv"
    )
    assert isinstance(results, list)


# ── Sophia Tests ──

@pytest.mark.asyncio
async def test_sophia_search():
    """Sophia should search Knowledge Items."""
    searcher = SophiaSearcher()
    results = await searcher.search("hegemonikon", max_results=5)
    assert isinstance(results, list)
    for r in results:
        assert r.source == SearchSource.SOPHIA


@pytest.mark.asyncio
async def test_sophia_with_custom_dir(tmp_path: Path):
    """Sophia should work with custom KI directory."""
    # Create a temp KI file
    ki_file = tmp_path / "test_item.md"
    ki_file.write_text("# Test\nThis is about free energy principle and FEP.")

    searcher = SophiaSearcher(ki_dir=tmp_path)
    results = await searcher.search("free energy", max_results=5)
    assert len(results) >= 1
    assert "test_item" in results[0].title


# ── Kairos Tests ──

@pytest.mark.asyncio
async def test_kairos_search():
    """Kairos should search handoffs and ROMs."""
    searcher = KairosSearcher()
    results = await searcher.search("session", max_results=5)
    assert isinstance(results, list)
    for r in results:
        assert r.source == SearchSource.KAIROS


@pytest.mark.asyncio
async def test_kairos_with_empty_dir(tmp_path: Path):
    """Kairos should handle empty directories gracefully."""
    searcher = KairosSearcher(handoff_dir=tmp_path, rom_dir=tmp_path)
    results = await searcher.search("anything", max_results=5)
    assert results == []


# ── Integration ──

@pytest.mark.asyncio
async def test_all_internal_searchers():
    """All internal searchers should be importable and runnable."""
    searchers = [
        GnosisSearcher(),
        SophiaSearcher(),
        KairosSearcher(),
    ]
    for s in searchers:
        results = await s.search("test", max_results=3)
        assert isinstance(results, list)
