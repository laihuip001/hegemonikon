# PROOF: [L3/テスト] <- mekhane/fep/tests/ 対象モジュールが存在→検証が必要
"""
Tests for workflow_runner with X-series integration.

Verifies:
- Derivative selection for all 24 theorems
- X-series recommendations generation
- Output formatting
"""

import pytest
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from mekhane.workflow_runner import (
    run_workflow,
    format_derivative_selection,
    get_workflow_for_theorem,
    WorkflowResult,
    XSeriesRecommendation,
    THEOREM_TO_WORKFLOW,
)

# =============================================================================
# Theorem Coverage Tests
# =============================================================================


class TestTheoremCoverage:
    """Test that all 24 theorems work with workflow_runner."""

    ALL_THEOREMS = [
        "O1",
        "O2",
        "O3",
        "O4",
        "S1",
        "S2",
        "S3",
        "S4",
        "H1",
        "H2",
        "H3",
        "H4",
        "P1",
        "P2",
        "P3",
        "P4",
        "K1",
        "K2",
        "K3",
        "K4",
        "A1",
        "A2",
        "A3",
        "A4",
    ]

    @pytest.mark.parametrize("theorem", ALL_THEOREMS)
    def test_run_workflow_all_theorems(self, theorem):
        """All theorems should return valid WorkflowResult."""
        result = run_workflow(theorem, "テスト入力")

        assert isinstance(result, WorkflowResult)
        assert result.theorem == theorem
        assert isinstance(result.derivative, str)
        assert 0 <= result.confidence <= 1
        assert isinstance(result.x_series_recommendations, list)

    @pytest.mark.parametrize("theorem", ALL_THEOREMS)
    def test_theorem_to_workflow_mapping(self, theorem):
        """All theorems should have workflow mapping."""
        workflow = get_workflow_for_theorem(theorem)
        assert workflow is not None
        assert workflow.startswith("/")


# =============================================================================
# X-Series Recommendation Tests
# =============================================================================


class TestXSeriesRecommendations:
    """Test X-series next step recommendations."""

    def test_o_series_recommendations(self):
        """O-series should get recommendations to other series."""
        result = run_workflow("O1", "本質分析")

        assert len(result.x_series_recommendations) >= 2

        # Should not recommend same series
        for rec in result.x_series_recommendations:
            assert rec.target != "O"

    def test_high_confidence_prioritizes_action(self):
        """High confidence should prioritize S, P series."""
        result = run_workflow("O1", "やって実行proceed")  # High confidence keywords

        # S or P should be in top recommendations
        targets = [rec.target for rec in result.x_series_recommendations]
        assert "S" in targets or "P" in targets

    def test_x_series_recommendation_format(self):
        """XSeriesRecommendation should have all fields."""
        result = run_workflow("A2", "判定テスト")

        if result.x_series_recommendations:
            rec = result.x_series_recommendations[0]
            assert isinstance(rec.x_id, str)
            assert rec.x_id.startswith("X-")
            assert isinstance(rec.target, str)
            assert isinstance(rec.workflow, str)
            assert isinstance(rec.reason, str)


# =============================================================================
# Format Output Tests
# =============================================================================


class TestFormatOutput:
    """Test format_derivative_selection output."""

    def test_format_includes_theorem(self):
        """Output should include theorem code."""
        result = run_workflow("S2", "ツール生成")
        output = format_derivative_selection(result)

        assert "S2" in output

    def test_format_includes_x_series(self):
        """Output should include X-series recommendations."""
        result = run_workflow("H1", "傾向評価")
        output = format_derivative_selection(result)

        assert "X-series" in output or "推奨" in output

    def test_format_includes_workflow(self):
        """Output should reference the workflow path."""
        result = run_workflow("K3", "目的確認")
        output = format_derivative_selection(result)

        workflow = THEOREM_TO_WORKFLOW["K3"]
        assert workflow in output


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_problem_context(self):
        """Empty context should still work."""
        result = run_workflow("O1", "")
        assert result.theorem == "O1"

    def test_long_problem_context(self):
        """Long context should work without error."""
        long_context = "テスト" * 1000
        result = run_workflow("O1", long_context)
        assert result.theorem == "O1"

    def test_japanese_input(self):
        """Japanese input should be processed correctly."""
        result = run_workflow("O1", "この問題の本質は何か？深く考察してほしい。")
        assert isinstance(result.derivative, str)

    def test_english_input(self):
        """English input should be processed correctly."""
        result = run_workflow("O1", "What is the essence of this problem?")
        assert isinstance(result.derivative, str)
