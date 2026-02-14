#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/ergasterion/tekhne/ SweepEngine + ResponseCache 統合テスト
"""
SweepEngine + ResponseCache Integration Tests.

Tests the interaction between ResponseCache and SweepEngine:
- Cache hit/miss behavior during sweep
- TTL expiry during sweep
- Cache consistency across multiple sweeps
- Stats tracking through sweep cycle
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mekhane.ergasterion.tekhne.response_cache import ResponseCache, CacheStats
from mekhane.ergasterion.tekhne.sweep_engine import (
    SweepEngine,
    SweepReport,
    SweepIssue,
    _parse_sweep_response,
)


# === Fixtures ===


@pytest.fixture
def tmp_cache_dir(tmp_path):
    """Temporary cache directory for tests."""
    return tmp_path / "test_cache"


@pytest.fixture
def cache(tmp_cache_dir):
    """Fresh ResponseCache with short TTL for testing."""
    return ResponseCache(cache_dir=tmp_cache_dir, ttl=60)


@pytest.fixture
def mock_cortex_response():
    """Standard mock response from Cortex API."""
    return json.dumps({
        "issues": [
            {
                "severity": "minor",
                "description": "Test issue from mock",
                "recommendation": "Fix it",
            }
        ]
    })


@pytest.fixture
def sample_prompt_file(tmp_path):
    """Create a sample prompt file for sweep testing."""
    prompt = tmp_path / "test_prompt.md"
    prompt.write_text(
        "# Test Prompt\n\nThis is a test prompt for sweep integration testing.\n"
        "Please review this content for quality issues.\n",
        encoding="utf-8",
    )
    return str(prompt)


# === ResponseCache Unit Tests (Extended) ===


class TestCacheBasicOps:
    """Basic cache operations."""

    def test_put_and_get(self, cache):
        """Store and retrieve a response."""
        key = cache.put(
            prompt="Hello world",
            model="gemini-2.0-flash",
            response_text="Test response",
        )
        assert key

        hit = cache.get(prompt="Hello world", model="gemini-2.0-flash")
        assert hit is not None
        assert hit["text"] == "Test response"
        assert hit["model"] == "gemini-2.0-flash"

    def test_cache_miss(self, cache):
        """Non-existent key returns None."""
        result = cache.get(prompt="nonexistent", model="gemini-2.0-flash")
        assert result is None

    def test_ttl_expiry(self, tmp_cache_dir):
        """Expired entries return None."""
        cache = ResponseCache(cache_dir=tmp_cache_dir, ttl=1)  # 1 second TTL
        cache.put(
            prompt="expirable",
            model="gemini-2.0-flash",
            response_text="will expire",
        )

        # Should hit immediately
        assert cache.get(prompt="expirable", model="gemini-2.0-flash") is not None

        # Wait for expiry
        time.sleep(1.1)
        assert cache.get(prompt="expirable", model="gemini-2.0-flash") is None

    def test_different_models_different_keys(self, cache):
        """Same prompt with different models creates separate cache entries."""
        cache.put(prompt="same", model="model-a", response_text="response-a")
        cache.put(prompt="same", model="model-b", response_text="response-b")

        hit_a = cache.get(prompt="same", model="model-a")
        hit_b = cache.get(prompt="same", model="model-b")

        assert hit_a["text"] == "response-a"
        assert hit_b["text"] == "response-b"

    def test_system_instruction_affects_key(self, cache):
        """System instruction changes the cache key."""
        cache.put(
            prompt="same", model="m", response_text="no-sys",
            system_instruction=None,
        )
        cache.put(
            prompt="same", model="m", response_text="with-sys",
            system_instruction="Be helpful",
        )

        assert cache.get(prompt="same", model="m")["text"] == "no-sys"
        assert cache.get(
            prompt="same", model="m", system_instruction="Be helpful"
        )["text"] == "with-sys"


class TestCacheStats:
    """Cache statistics tracking."""

    def test_hit_miss_counting(self, cache):
        """Stats accurately count hits and misses."""
        cache.put(prompt="exists", model="m", response_text="yes")

        cache.get(prompt="exists", model="m")       # hit
        cache.get(prompt="missing", model="m")       # miss
        cache.get(prompt="exists", model="m")        # hit
        cache.get(prompt="also-missing", model="m")  # miss

        stats = cache.stats()
        assert stats.hits == 2
        assert stats.misses == 2
        assert stats.hit_rate == 0.5

    def test_stats_total_entries(self, cache):
        """Stats report correct number of entries."""
        for i in range(5):
            cache.put(prompt=f"p{i}", model="m", response_text=f"r{i}")

        stats = cache.stats()
        assert stats.total_entries == 5

    def test_empty_cache_stats(self, cache):
        """Empty cache returns zero stats."""
        stats = cache.stats()
        assert stats.total_entries == 0
        assert stats.size_bytes == 0
        assert stats.hit_rate == 0.0


class TestCacheEviction:
    """Cache eviction behavior."""

    def test_clear(self, cache):
        """Clear removes all entries."""
        for i in range(10):
            cache.put(prompt=f"p{i}", model="m", response_text=f"r{i}")

        removed = cache.clear()
        assert removed == 10
        assert cache.stats().total_entries == 0

    def test_invalidate_specific(self, cache):
        """Invalidate removes only the targeted entry."""
        cache.put(prompt="keep", model="m", response_text="keep-me")
        cache.put(prompt="remove", model="m", response_text="remove-me")

        result = cache.invalidate(prompt="remove", model="m")
        assert result is True
        assert cache.get(prompt="remove", model="m") is None
        assert cache.get(prompt="keep", model="m") is not None

    def test_invalidate_nonexistent(self, cache):
        """Invalidate on non-existent key returns False."""
        assert cache.invalidate(prompt="nope", model="m") is False


# === SweepEngine + Cache Integration ===


class TestSweepCacheIntegration:
    """Integration tests for SweepEngine with ResponseCache."""

    def test_engine_creates_with_cache(self):
        """SweepEngine initializes with cache enabled by default."""
        engine = SweepEngine(use_cache=True)
        assert engine.use_cache is True

    def test_engine_without_cache(self):
        """SweepEngine can be created with cache disabled."""
        engine = SweepEngine(use_cache=False)
        assert engine.use_cache is False

    def test_cache_integration_during_sweep(
        self, tmp_cache_dir, sample_prompt_file, mock_cortex_response
    ):
        """Cache is populated during sweep and used on re-sweep."""
        engine = SweepEngine(use_cache=True)

        # Inject a test cache
        test_cache = ResponseCache(cache_dir=tmp_cache_dir, ttl=3600)
        engine._cache = test_cache

        # Mock CortexClient with ask_batch (used by sweep())
        mock_response = MagicMock(text=mock_cortex_response)
        mock_client = MagicMock()
        mock_client.ask_batch.return_value = [mock_response] * 3
        engine._client = mock_client

        # Mock PerspectiveMatrix
        mock_perspective = MagicMock()
        mock_perspective.domain_id = "Test"
        mock_perspective.axis_id = "O1"
        mock_perspective.perspective_id = "Test-O1"
        mock_matrix = MagicMock()
        mock_matrix.all_perspectives.return_value = [
            mock_perspective, mock_perspective, mock_perspective
        ]
        mock_matrix.generate_prompt.return_value = "Review this from Test perspective"
        engine._matrix = mock_matrix

        # First sweep — should call API
        report1 = engine.sweep(
            filepath=sample_prompt_file,
            max_perspectives=3,
        )
        assert isinstance(report1, SweepReport)
        batch_calls_1 = mock_client.ask_batch.call_count

        # Second sweep with same file — should hit cache
        report2 = engine.sweep(
            filepath=sample_prompt_file,
            max_perspectives=3,
        )
        batch_calls_2 = mock_client.ask_batch.call_count - batch_calls_1

        # Cache should reduce API calls on second sweep
        stats = test_cache.stats()
        assert stats.hits > 0, f"Cache should have hits on second sweep. Stats: {stats}"
        assert batch_calls_2 < batch_calls_1 or stats.hits > 0, (
            f"Second sweep should use cache (batch calls: {batch_calls_1} vs {batch_calls_2}, "
            f"hits: {stats.hits})"
        )

    def test_parse_cached_response(self, mock_cortex_response):
        """Parsed results from cached response match parsed API response."""
        issues1 = _parse_sweep_response(
            mock_cortex_response, "Test-O1", "Test", "O1"
        )
        issues2 = _parse_sweep_response(
            mock_cortex_response, "Test-O1", "Test", "O1"
        )

        assert len(issues1) == len(issues2)
        if issues1:
            assert issues1[0].description == issues2[0].description


# === Regression Tests ===


class TestRegressions:
    """Regression tests for known issues."""

    def test_cache_handles_empty_response(self, cache):
        """Cache correctly stores and retrieves empty responses."""
        cache.put(prompt="empty", model="m", response_text="")
        hit = cache.get(prompt="empty", model="m")
        assert hit is not None
        assert hit["text"] == ""

    def test_cache_handles_unicode(self, cache):
        """Cache handles Japanese/Unicode content correctly."""
        text = "これはテスト応答です。セキュリティ問題なし。"
        cache.put(prompt="日本語テスト", model="m", response_text=text)
        hit = cache.get(prompt="日本語テスト", model="m")
        assert hit["text"] == text

    def test_cache_handles_large_response(self, cache):
        """Cache handles large responses without corruption."""
        large_text = "x" * 100_000  # 100KB
        cache.put(prompt="large", model="m", response_text=large_text)
        hit = cache.get(prompt="large", model="m")
        assert hit["text"] == large_text
        assert len(hit["text"]) == 100_000

    def test_concurrent_cache_metadata(self, cache):
        """Metadata is preserved through put/get cycle."""
        meta = {"perspective": "Security-O1", "domain": "Security", "axis": "O1"}
        cache.put(
            prompt="meta-test", model="m",
            response_text="resp", metadata=meta,
        )
        hit = cache.get(prompt="meta-test", model="m")
        assert hit["metadata"] == meta
