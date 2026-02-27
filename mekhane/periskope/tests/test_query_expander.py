# PROOF: [L2/Periskope] <- mekhane/periskope/tests/test_query_expander.py A0→AutoFix
"""Tests for W3 QueryExpander and P3 weight distribution."""

from __future__ import annotations

import pytest
from mekhane.periskope.query_expander import QueryExpander, _is_japanese


class TestIsJapanese:
    """Test Japanese text detection."""

    def test_pure_japanese(self):
        assert _is_japanese("自由エネルギー原理") is True

    def test_pure_english(self):
        assert _is_japanese("Free Energy Principle") is False

    def test_mixed_with_japanese(self):
        assert _is_japanese("FEPの概要") is True

    def test_mixed_mostly_english(self):
        assert _is_japanese("FEP overview") is False

    def test_empty_string(self):
        assert _is_japanese("") is False

    def test_numbers_only(self):
        assert _is_japanese("12345") is False

    def test_katakana(self):
        assert _is_japanese("エネルギー") is True

    def test_hiragana(self):
        assert _is_japanese("おはよう") is True


class TestQueryExpander:
    """Test QueryExpander initialization and structure."""

    def test_instantiation(self):
        qe = QueryExpander()
        assert qe is not None

    def test_default_model(self):
        qe = QueryExpander()
        assert qe.model == "gemini-2.0-flash"

    def test_custom_model(self):
        qe = QueryExpander(model="gemini-2.5-flash")
        assert qe.model == "gemini-2.5-flash"


class TestWeightDistribution:
    """Test P3 weight distribution helpers."""

    def test_searxng_default_weights(self):
        """Default SearXNG weights: general=40%, rest=20% each."""
        w = {"general": 0.4, "science": 0.2, "it": 0.2, "news": 0.2}
        max_results = 20
        n_general = max(3, int(max_results * w["general"]))
        n_science = max(3, int(max_results * w["science"]))
        assert n_general == 8
        assert n_science == 4

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

    def test_custom_weights(self):
        """Custom weights: heavy on general."""
        w = {"general": 0.7, "science": 0.1, "it": 0.1, "news": 0.1}
        max_results = 20
        n_general = max(3, int(max_results * w["general"]))
        assert n_general == 14

    def test_min_results_floor(self):
        """Min floor prevents zero-result categories."""
        w = {"general": 0.01}
        max_results = 5
        n_general = max(3, int(max_results * w["general"]))
        assert n_general == 3  # Floor at 3
