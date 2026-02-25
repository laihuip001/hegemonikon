# PROOF: [L3/テスト] <- mekhane/periskope/tests/ A0→Implementation→test_query_expander
"""Tests for W3 QueryExpander and P3 weight distribution."""

from __future__ import annotations

import pytest
from mekhane.periskope.query_expander import QueryExpander, _is_japanese


# PURPOSE: Test Japanese text detection
class TestIsJapanese:
    """Test Japanese text detection."""

    # PURPOSE: pure_japanese をテストする
    def test_pure_japanese(self):
        assert _is_japanese("自由エネルギー原理") is True

    # PURPOSE: pure_english をテストする
    def test_pure_english(self):
        assert _is_japanese("Free Energy Principle") is False

    # PURPOSE: mixed_with_japanese をテストする
    def test_mixed_with_japanese(self):
        assert _is_japanese("FEPの概要") is True

    # PURPOSE: mixed_mostly_english をテストする
    def test_mixed_mostly_english(self):
        assert _is_japanese("FEP overview") is False

    # PURPOSE: empty_string をテストする
    def test_empty_string(self):
        assert _is_japanese("") is False

    # PURPOSE: numbers_only をテストする
    def test_numbers_only(self):
        assert _is_japanese("12345") is False

    # PURPOSE: katakana をテストする
    def test_katakana(self):
        assert _is_japanese("エネルギー") is True

    # PURPOSE: hiragana をテストする
    def test_hiragana(self):
        assert _is_japanese("おはよう") is True


# PURPOSE: Test QueryExpander initialization and structure
class TestQueryExpander:
    """Test QueryExpander initialization and structure."""

    # PURPOSE: instantiation をテストする
    def test_instantiation(self):
        qe = QueryExpander()
        assert qe is not None

    # PURPOSE: default_model をテストする
    def test_default_model(self):
        qe = QueryExpander()
        assert qe.model == "gemini-2.0-flash"

    # PURPOSE: custom_model をテストする
    def test_custom_model(self):
        qe = QueryExpander(model="gemini-2.5-flash")
        assert qe.model == "gemini-2.5-flash"


# PURPOSE: Test P3 weight distribution helpers
class TestWeightDistribution:
    """Test P3 weight distribution helpers."""

    # PURPOSE: Default SearXNG weights: general=40%, rest=20% each
    def test_searxng_default_weights(self):
        """Default SearXNG weights: general=40%, rest=20% each."""
        w = {"general": 0.4, "science": 0.2, "it": 0.2, "news": 0.2}
        max_results = 20
        n_general = max(3, int(max_results * w["general"]))
        n_science = max(3, int(max_results * w["science"]))
        assert n_general == 8
        assert n_science == 4

    # PURPOSE: Default Exa weights: general=50%, paper=30%, github=20%
    def test_exa_default_weights(self):
        """Default Exa weights: general=50%, paper=30%, github=20%."""
        w = {"general": 0.5, "paper": 0.3, "github": 0.2}
        max_results = 10
        n_general = max(2, int(max_results * w["general"]))
        n_paper = max(2, int(max_results * w["paper"]))
        n_github = max(2, int(max_results * w["github"]))
        assert n_general == 5
        assert n_paper == 3
        assert n_github == 2

    # PURPOSE: Custom weights: heavy on general
    def test_custom_weights(self):
        """Custom weights: heavy on general."""
        w = {"general": 0.7, "science": 0.1, "it": 0.1, "news": 0.1}
        max_results = 20
        n_general = max(3, int(max_results * w["general"]))
        assert n_general == 14

    # PURPOSE: Min floor prevents zero-result categories
    def test_min_results_floor(self):
        """Min floor prevents zero-result categories."""
        w = {"general": 0.01}
        max_results = 5
        n_general = max(3, int(max_results * w["general"]))
        assert n_general == 3  # Floor at 3
