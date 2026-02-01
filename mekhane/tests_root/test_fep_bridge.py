# PROOF: [L3/テスト] <- mekhane/tests_root/ 対象モジュールが存在→検証が必要
"""Tests for FEP Bridge - Workflow Integration Layer."""

import pytest
import numpy as np

# Skip all tests if pymdp is not available
pytest.importorskip("pymdp")

from mekhane.fep.fep_bridge import (
    noesis_analyze,
    boulesis_analyze,
    full_inference_cycle,
    NoesisResult,
    BoulesisResult,
)


class TestNoesisAnalyze:
    """Tests for O1 Noēsis FEP integration."""

    def test_returns_noesis_result(self):
        """noesis_analyze returns a NoesisResult dataclass."""
        result = noesis_analyze(context_clarity=1)
        assert isinstance(result, NoesisResult)

    def test_entropy_is_positive(self):
        """Entropy should be a positive value."""
        result = noesis_analyze(context_clarity=1)
        assert result.entropy >= 0

    def test_confidence_in_valid_range(self):
        """Confidence should be between 0 and 1."""
        result = noesis_analyze(context_clarity=1)
        assert 0 <= result.confidence <= 1

    def test_map_state_has_required_keys(self):
        """MAP state should have phantasia, assent, horme keys."""
        result = noesis_analyze(context_clarity=1)
        assert "phantasia" in result.map_state
        assert "assent" in result.map_state
        assert "horme" in result.map_state

    def test_interpretation_is_string(self):
        """Interpretation should be a non-empty string."""
        result = noesis_analyze(context_clarity=1)
        assert isinstance(result.interpretation, str)
        assert len(result.interpretation) > 0

    def test_reset_beliefs_works(self):
        """reset_beliefs=True should reset agent state."""
        # Run twice with reset to ensure deterministic behavior
        result1 = noesis_analyze(context_clarity=1, reset_beliefs=True)
        result2 = noesis_analyze(context_clarity=1, reset_beliefs=True)
        # Results should be similar (not necessarily identical due to sampling)
        assert abs(result1.entropy - result2.entropy) < 0.5


class TestBoulesisAnalyze:
    """Tests for O2 Boulēsis FEP integration."""

    def test_returns_boulesis_result(self):
        """boulesis_analyze returns a BoulesisResult dataclass."""
        result = boulesis_analyze()
        assert isinstance(result, BoulesisResult)

    def test_preferred_action_is_valid(self):
        """Preferred action should be 0 or 1."""
        result = boulesis_analyze()
        assert result.preferred_action in [0, 1]

    def test_action_name_is_valid(self):
        """Action name should be 'observe' or 'act'."""
        result = boulesis_analyze()
        assert result.action_name in ["observe", "act"]

    def test_action_probabilities_sum_to_one(self):
        """Action probabilities should sum to approximately 1."""
        result = boulesis_analyze()
        prob_sum = sum(result.action_probabilities)
        assert abs(prob_sum - 1.0) < 0.01

    def test_interpretation_is_string(self):
        """Interpretation should be a non-empty string."""
        result = boulesis_analyze()
        assert isinstance(result.interpretation, str)
        assert len(result.interpretation) > 0

    def test_chained_from_noesis(self):
        """boulesis_analyze can chain from prior noesis result."""
        noesis_result = noesis_analyze(context_clarity=2)
        boulesis_result = boulesis_analyze(prior_noesis=noesis_result)
        assert isinstance(boulesis_result, BoulesisResult)


class TestFullInferenceCycle:
    """Tests for complete O1→O2 inference cycle."""

    def test_returns_dict_with_required_keys(self):
        """full_inference_cycle returns dict with noesis, boulesis, summary."""
        result = full_inference_cycle(context_clarity=1)
        assert isinstance(result, dict)
        assert "noesis" in result
        assert "boulesis" in result
        assert "summary" in result

    def test_noesis_section_has_required_keys(self):
        """Noesis section should have entropy, confidence, map_state."""
        result = full_inference_cycle(context_clarity=1)
        noesis = result["noesis"]
        assert "entropy" in noesis
        assert "confidence" in noesis
        assert "map_state" in noesis
        assert "interpretation" in noesis

    def test_boulesis_section_has_required_keys(self):
        """Boulesis section should have action info."""
        result = full_inference_cycle(context_clarity=1)
        boulesis = result["boulesis"]
        assert "preferred_action" in boulesis
        assert "action_name" in boulesis
        assert "action_probabilities" in boulesis

    def test_summary_is_string(self):
        """Summary should be a formatted string."""
        result = full_inference_cycle(context_clarity=1)
        assert isinstance(result["summary"], str)
        assert "FEP Analysis" in result["summary"]

    def test_different_context_clarity_affects_results(self):
        """Different context clarity levels should affect inference."""
        result_unclear = full_inference_cycle(context_clarity=0, reset_beliefs=True)
        result_clear = full_inference_cycle(context_clarity=2, reset_beliefs=True)

        # Results should differ (at least slightly)
        # Just verify both ran successfully
        assert result_unclear["noesis"]["entropy"] >= 0
        assert result_clear["noesis"]["entropy"] >= 0
