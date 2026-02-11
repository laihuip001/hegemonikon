#!/usr/bin/env python3
# PROOF: [L3/テスト] <- convergence_tracker の3層収束証明テスト
"""
Tests for convergence_tracker.py

Covers:
- Binomial p-value computation
- Disagreement classification
- Convergence summary (3-layer criteria)
- Format display with p-value
"""

import json
import math
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from mekhane.fep.convergence_tracker import (
    _binomial_p_value,
    _log_comb,
    classify_disagreement,
    convergence_summary,
    format_convergence,
    record_agreement,
    ConvergenceScore,
)


# ============================================================
# Binomial Test
# ============================================================


# PURPOSE: Test suite validating binomial p value correctness
class TestBinomialPValue:
    """Test the pure-Python binomial test implementation."""

    # PURPOSE: Verify zero trials behaves correctly
    def test_zero_trials(self):
        """Verify zero trials behavior."""
        assert _binomial_p_value(0, 0) == 1.0

    # PURPOSE: Verify zero successes behaves correctly
    def test_zero_successes(self):
        """Verify zero successes behavior."""
        assert _binomial_p_value(0, 10) == 1.0

    # PURPOSE: Verify all successes behaves correctly
    def test_all_successes(self):
        """If all trials are successes, p should be very small."""
        p = _binomial_p_value(10, 10, chance=1 / 6)
        assert p < 0.001

    # PURPOSE: Verify chance level behaves correctly
    def test_chance_level(self):
        """At chance level (1/6 of trials), p should be ~0.5 or higher."""
        # 5 out of 30 = 16.7% = exactly chance
        p = _binomial_p_value(5, 30, chance=1 / 6)
        assert p > 0.3  # Not significant

    # PURPOSE: Verify above chance behaves correctly
    def test_above_chance(self):
        """Well above chance should give low p."""
        # 15 out of 30 = 50%, much higher than 1/6
        p = _binomial_p_value(15, 30, chance=1 / 6)
        assert p < 0.001

    # PURPOSE: Verify moderate above chance behaves correctly
    def test_moderate_above_chance(self):
        """Moderately above chance with enough data."""
        # 10 out of 30 = 33%, about 2x chance
        p = _binomial_p_value(10, 30, chance=1 / 6)
        assert p < 0.05


# PURPOSE: Test suite validating log comb correctness
class TestLogComb:
    """Test log-combination helper."""

    # PURPOSE: Verify basic combinations behaves correctly
    def test_basic_combinations(self):
        # C(5,2) = 10
        """Verify basic combinations behavior."""
        assert abs(math.exp(_log_comb(5, 2)) - 10.0) < 0.01

    # PURPOSE: Verify edge k zero behaves correctly
    def test_edge_k_zero(self):
        # C(n,0) = 1
        """Verify edge k zero behavior."""
        assert abs(math.exp(_log_comb(10, 0)) - 1.0) < 0.01

    # PURPOSE: Verify edge k equals n behaves correctly
    def test_edge_k_equals_n(self):
        # C(n,n) = 1
        """Verify edge k equals n behavior."""
        assert abs(math.exp(_log_comb(10, 10)) - 1.0) < 0.01

    # PURPOSE: Verify invalid k behaves correctly
    def test_invalid_k(self):
        """Verify invalid k behavior."""
        assert _log_comb(5, 6) == float("-inf")
        assert _log_comb(5, -1) == float("-inf")


# ============================================================
# Disagreement Classification
# ============================================================


# PURPOSE: Test suite validating classify disagreement correctness
class TestClassifyDisagreement:
    """Test disagreement categorization."""

    # PURPOSE: Verify agreement returns unknown behaves correctly
    def test_agreement_returns_unknown(self):
        """Verify agreement returns unknown behavior."""
        assert classify_disagreement("O", "O") == "unknown"

    # PURPOSE: Verify observe is explore behaves correctly
    def test_observe_is_explore(self):
        """Verify observe is explore behavior."""
        result = classify_disagreement(None, "O", agent_action="observe")
        assert result == "explore"

    # PURPOSE: Verify none agent is explore behaves correctly
    def test_none_agent_is_explore(self):
        """Verify none agent is explore behavior."""
        result = classify_disagreement(None, "S")
        assert result == "explore"

    # PURPOSE: Verify different series is exploit behaves correctly
    def test_different_series_is_exploit(self):
        """Verify different series is exploit behavior."""
        result = classify_disagreement("O", "S", agent_action="act_O")
        assert result == "exploit"

    # PURPOSE: Verify attractor none is error behaves correctly
    def test_attractor_none_is_error(self):
        """Verify attractor none is error behavior."""
        result = classify_disagreement("O", None, agent_action="act_O")
        assert result == "error"


# ============================================================
# Convergence Summary
# ============================================================


# PURPOSE: Test suite validating convergence summary correctness
class TestConvergenceSummary:
    """Test the convergence summary computation."""

    # PURPOSE: Verify empty records behaves correctly
    def test_empty_records(self):
        """Verify empty records behavior."""
        result = convergence_summary([])
        assert result["total"] == 0
        assert result["p_value"] == 1.0
        assert result["converged"] is False
        assert result["disagreement_breakdown"] == {}

    # PURPOSE: Verify all agree behaves correctly
    def test_all_agree(self):
        # Records with convergence_score (pushout format)
        """Verify all agree behavior."""
        records = [
            {
                "agreed": True,
                "convergence_score": ConvergenceScore(
                    agent_series="O", attractor_series="O",
                    agreement=True, value_alignment=0.5,
                ).to_dict(),
            }
            for _ in range(15)
        ]
        result = convergence_summary(records)
        assert result["rate"] == 1.0
        assert result["p_value"] < 0.001
        assert result["pushout_score"] > 0.3
        assert result["converged"] is True

    # PURPOSE: Verify all disagree behaves correctly
    def test_all_disagree(self):
        """Verify all disagree behavior."""
        records = [
            {"agreed": False, "disagreement_category": "exploit"}
            for _ in range(10)
        ]
        result = convergence_summary(records)
        assert result["rate"] == 0.0
        assert result["converged"] is False
        assert result["disagreement_breakdown"]["exploit"] == 10

    # PURPOSE: Verify not converged if degrading behaves correctly
    def test_not_converged_if_degrading(self):
        """Even with high rate, degrading trend should prevent convergence."""
        # First half: all agree (8/8)
        # Second half: all disagree (8/8)
        records = [{"agreed": True} for _ in range(8)] + [
            {"agreed": False, "disagreement_category": "error"} for _ in range(8)
        ]
        result = convergence_summary(records)
        assert result["trend"] == "degrading"
        assert result["converged"] is False

    # PURPOSE: Verify not converged if too few behaves correctly
    def test_not_converged_if_too_few(self):
        """Even with good p-value, need >= 10 records."""
        records = [{"agreed": True} for _ in range(5)]
        result = convergence_summary(records)
        assert result["converged"] is False  # total < 10

    # PURPOSE: Verify mixed disagreement breakdown behaves correctly
    def test_mixed_disagreement_breakdown(self):
        """Verify mixed disagreement breakdown behavior."""
        records = [
            {"agreed": False, "disagreement_category": "explore"},
            {"agreed": False, "disagreement_category": "explore"},
            {"agreed": False, "disagreement_category": "exploit"},
            {"agreed": True},
        ]
        result = convergence_summary(records)
        bd = result["disagreement_breakdown"]
        assert bd["explore"] == 2
        assert bd["exploit"] == 1


# ============================================================
# Format Display
# ============================================================


# PURPOSE: Test suite validating format convergence correctness
class TestFormatConvergence:
    """Test the display formatting."""

    # PURPOSE: Verify no data behaves correctly
    def test_no_data(self):
        """Verify no data behavior."""
        result = format_convergence({"total": 0})
        assert "No data" in result

    # PURPOSE: Verify converged with pushout behaves correctly
    def test_converged_with_pushout(self):
        """Verify converged with pushout behavior."""
        summary = {
            "total": 20,
            "agreements": 15,
            "rate": 0.75,
            "p_value": 0.001,
            "converged": True,
            "recent_rate": 0.8,
            "trend": "stable",
            "disagreement_breakdown": {"explore": 3, "exploit": 2},
            "pushout_score": 0.65,
            "recent_pushout": 0.7,
        }
        result = format_convergence(summary)
        assert "✅" in result
        assert "pushout=" in result
        assert "agree=75%" in result
        assert "disagree=" in result

    # PURPOSE: Verify not converged behaves correctly
    def test_not_converged(self):
        """Verify not converged behavior."""
        summary = {
            "total": 5,
            "agreements": 1,
            "rate": 0.2,
            "p_value": 0.5,
            "converged": False,
            "recent_rate": 0.2,
            "trend": "insufficient_data",
            "disagreement_breakdown": {},
            "pushout_score": 0.15,
            "recent_pushout": 0.15,
        }
        result = format_convergence(summary)
        assert "📊" in result
        assert "pushout=" in result


# ============================================================
# Record Agreement (integration)
# ============================================================


# PURPOSE: Test suite validating record agreement correctness
class TestRecordAgreement:
    """Integration test for record_agreement with temp file."""

    # PURPOSE: Verify record and summarize behaves correctly
    def test_record_and_summarize(self, tmp_path):
        """Verify record and summarize behavior."""
        test_path = tmp_path / "convergence.json"
        with mock.patch(
            "mekhane.fep.convergence_tracker.CONVERGENCE_PATH", test_path
        ):
            # Record 12 agreements
            for _ in range(12):
                result = record_agreement("O", "O", agent_action="act_O")

            assert result["total"] == 12
            assert result["agreements"] == 12
            assert result["p_value"] < 0.001
            assert result["converged"] is True

    # PURPOSE: Verify record disagreement category behaves correctly
    def test_record_disagreement_category(self, tmp_path):
        """Verify record disagreement category behavior."""
        test_path = tmp_path / "convergence.json"
        with mock.patch(
            "mekhane.fep.convergence_tracker.CONVERGENCE_PATH", test_path
        ):
            record_agreement(None, "O", agent_action="observe")

            # Check the saved record
            data = json.loads(test_path.read_text())
            rec = data["records"][0]
            assert rec["agreed"] is False
            assert rec["disagreement_category"] == "explore"
