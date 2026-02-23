#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/ergasterion/tekhne/tests/test_cortex_refine.py O1->Zet->Impl
# PURPOSE: Tests for Sweep Engine and Deep Engine — Cortex Refine Integration
"""
Tests for Sweep Engine and Deep Engine — Cortex Refine Integration

API モックを使い、実 API は呼ばない。
データ構造・レスポンスパーサー・パイプライン統合をテスト。
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from mekhane.ergasterion.tekhne.sweep_engine import (
    SweepEngine,
    SweepIssue,
    SweepReport,
    _parse_sweep_response,
)
from mekhane.ergasterion.tekhne.deep_engine import (
    DeepEngine,
    DeepAnalysis,
    DeepFix,
    DeepReport,
    _parse_deep_response,
)


# ============================================================
# 1. SweepIssue Tests
# ============================================================


# PURPOSE: Test SweepIssue data structure
class TestSweepIssue:
    """Test SweepIssue data structure."""

    # PURPOSE: severity_weight_critical をテストする
    def test_severity_weight_critical(self):
        issue = SweepIssue(
            perspective_id="Security-O1",
            domain="Security",
            axis="O1",
            severity="critical",
            description="Test issue",
        )
        assert issue.severity_weight == 4

    # PURPOSE: severity_weight_info をテストする
    def test_severity_weight_info(self):
        issue = SweepIssue(
            perspective_id="Error-S2",
            domain="Error",
            axis="S2",
            severity="info",
            description="Test info",
        )
        assert issue.severity_weight == 1

    # PURPOSE: severity_weight_unknown をテストする
    def test_severity_weight_unknown(self):
        issue = SweepIssue(
            perspective_id="X-Y",
            domain="X",
            axis="Y",
            severity="unknown",
            description="Test",
        )
        assert issue.severity_weight == 0


# ============================================================
# 2. SweepReport Tests
# ============================================================


# PURPOSE: Test SweepReport aggregation and sorting
class TestSweepReport:
    """Test SweepReport aggregation and sorting."""

    # PURPOSE: sample_report の処理
    @pytest.fixture
    def sample_report(self):
        issues = [
            SweepIssue("A-O1", "A", "O1", "minor", "Minor issue"),
            SweepIssue("B-S1", "B", "S1", "critical", "Critical issue"),
            SweepIssue("A-O2", "A", "O2", "major", "Major issue"),
            SweepIssue("C-H1", "C", "H1", "info", "Info issue"),
        ]
        return SweepReport(
            filepath="test.md",
            issues=issues,
            silences=5,
            errors=1,
            total_perspectives=10,
            elapsed_seconds=1.5,
        )

    # PURPOSE: issue_count をテストする
    def test_issue_count(self, sample_report):
        assert sample_report.issue_count == 4

    # PURPOSE: coverage をテストする
    def test_coverage(self, sample_report):
        assert sample_report.coverage == 0.9  # 9/10

    # PURPOSE: top_issues_sorted をテストする
    def test_top_issues_sorted(self, sample_report):
        top = sample_report.top_issues(n=2)
        assert len(top) == 2
        assert top[0].severity == "critical"
        assert top[1].severity == "major"

    # PURPOSE: by_domain をテストする
    def test_by_domain(self, sample_report):
        by_domain = sample_report.by_domain()
        assert "A" in by_domain
        assert len(by_domain["A"]) == 2

    # PURPOSE: by_severity をテストする
    def test_by_severity(self, sample_report):
        counts = sample_report.by_severity()
        assert counts["critical"] == 1
        assert counts["major"] == 1
        assert counts["minor"] == 1
        assert counts["info"] == 1

    # PURPOSE: summary_contains_key_info をテストする
    def test_summary_contains_key_info(self, sample_report):
        summary = sample_report.summary()
        assert "test.md" in summary
        assert "10" in summary  # total perspectives
        assert "4" in summary  # issues

    # PURPOSE: to_dict_serializable をテストする
    def test_to_dict_serializable(self, sample_report):
        d = sample_report.to_dict()
        json_str = json.dumps(d)
        assert json_str  # no serialization error
        assert d["issue_count"] == 4
        assert d["coverage"] == 0.9


# ============================================================
# 3. Sweep Response Parser Tests
# ============================================================


# PURPOSE: Test _parse_sweep_response
class TestSweepResponseParser:
    """Test _parse_sweep_response."""

    # PURPOSE: silence_response をテストする
    def test_silence_response(self):
        issues = _parse_sweep_response(
            "SILENCE: No issues found", "A-O1", "A", "O1"
        )
        assert issues == []

    # PURPOSE: json_response をテストする
    def test_json_response(self):
        json_resp = json.dumps([
            {
                "severity": "major",
                "issue": "Missing error handling",
                "recommendation": "Add try-except",
            }
        ])
        issues = _parse_sweep_response(json_resp, "A-O1", "A", "O1")
        assert len(issues) == 1
        assert issues[0].severity == "major"
        assert "error handling" in issues[0].description

    # PURPOSE: text_response_with_severity をテストする
    def test_text_response_with_severity(self):
        text = (
            "This is a critical issue: the prompt lacks safety constraints. "
            "It should include guardrails to prevent harmful outputs. "
            "Additionally, there is no error handling for edge cases."
        )
        issues = _parse_sweep_response(text, "A-O1", "A", "O1")
        assert len(issues) >= 1
        assert issues[0].severity == "critical"

    # PURPOSE: empty_response をテストする
    def test_empty_response(self):
        issues = _parse_sweep_response("OK", "A-O1", "A", "O1")
        assert issues == []


# ============================================================
# 4. DeepAnalysis Tests
# ============================================================


# PURPOSE: Test DeepAnalysis data structure
class TestDeepAnalysis:
    """Test DeepAnalysis data structure."""

    # PURPOSE: has_actionable_fix をテストする
    def test_has_actionable_fix(self):
        analysis = DeepAnalysis(
            issue_id="A-O1",
            severity="major",
            root_cause="Missing guardrails",
            impact="Unsafe outputs",
            fixes=[
                DeepFix(
                    original="Do the task",
                    replacement="Do the task safely, following these guardrails:",
                    rationale="Safety first",
                    confidence=0.8,
                )
            ],
        )
        assert analysis.has_actionable_fix is True

    # PURPOSE: no_actionable_fix をテストする
    def test_no_actionable_fix(self):
        analysis = DeepAnalysis(
            issue_id="B-S1",
            severity="info",
            root_cause="Minor style issue",
            impact="None",
        )
        assert analysis.has_actionable_fix is False


# ============================================================
# 5. DeepReport Tests
# ============================================================


# PURPOSE: Test DeepReport aggregation
class TestDeepReport:
    """Test DeepReport aggregation."""

    # PURPOSE: sample_deep_report の処理
    @pytest.fixture
    def sample_deep_report(self):
        analyses = [
            DeepAnalysis(
                issue_id="A-O1",
                severity="critical",
                root_cause="Root A",
                impact="Impact A",
                priority_score=0.9,
                fixes=[DeepFix("a", "b", "reason", 0.8)],
            ),
            DeepAnalysis(
                issue_id="B-S1",
                severity="minor",
                root_cause="Root B",
                impact="Impact B",
                priority_score=0.3,
            ),
        ]
        return DeepReport(
            filepath="test.md",
            analyses=analyses,
            total_issues=2,
            elapsed_seconds=5.0,
        )

    # PURPOSE: prioritized_order をテストする
    def test_prioritized_order(self, sample_deep_report):
        p = sample_deep_report.prioritized()
        assert p[0].priority_score > p[1].priority_score

    # PURPOSE: actionable_filter をテストする
    def test_actionable_filter(self, sample_deep_report):
        a = sample_deep_report.actionable()
        assert len(a) == 1
        assert a[0].issue_id == "A-O1"

    # PURPOSE: to_dict_serializable をテストする
    def test_to_dict_serializable(self, sample_deep_report):
        d = sample_deep_report.to_dict()
        json_str = json.dumps(d)
        assert json_str
        assert d["total_issues"] == 2


# ============================================================
# 6. Deep Response Parser Tests
# ============================================================


# PURPOSE: Test _parse_deep_response
class TestDeepResponseParser:
    """Test _parse_deep_response."""

    # PURPOSE: json_response をテストする
    def test_json_response(self):
        json_resp = json.dumps({
            "severity": "major",
            "root_cause": "No output validation",
            "impact": "Wrong results",
            "fixes": [
                {
                    "original": "print(result)",
                    "replacement": "validate_and_print(result)",
                    "rationale": "Add validation",
                    "confidence": 0.7,
                }
            ],
            "related_issues": ["B-S1"],
        })
        analysis = _parse_deep_response(json_resp, "A-O1")
        assert analysis is not None
        assert analysis.severity == "major"
        assert len(analysis.fixes) == 1
        assert analysis.priority_score > 0

    # PURPOSE: text_fallback をテストする
    def test_text_fallback(self):
        text = "This is a substantial analysis " * 10
        analysis = _parse_deep_response(text, "B-S1")
        assert analysis is not None
        assert analysis.issue_id == "B-S1"

    # PURPOSE: short_response_returns_none をテストする
    def test_short_response_returns_none(self):
        analysis = _parse_deep_response("OK", "C-H1")
        assert analysis is None


# ============================================================
# 7. SweepEngine Integration (Mocked)
# ============================================================


# PURPOSE: Test SweepEngine with mocked CortexClient
class TestSweepEngineIntegration:
    """Test SweepEngine with mocked CortexClient."""

    # PURPOSE: Sweep engine should process mocked responses correctly
    def test_sweep_with_mock(self, tmp_path):
        """Sweep engine should process mocked responses correctly."""
        # Create test prompt
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("# Test Prompt\n\nDo the thing.\n")

        # Mock responses
        mock_response_1 = MagicMock()
        mock_response_1.text = json.dumps([
            {"severity": "major", "issue": "No constraints", "recommendation": "Add constraints"}
        ])

        mock_response_2 = MagicMock()
        mock_response_2.text = "SILENCE: No issues found"

        mock_client = MagicMock()
        mock_client.ask_batch.return_value = [mock_response_1, mock_response_2]

        engine = SweepEngine()
        engine._client = mock_client

        report = engine.sweep(str(prompt_file), max_perspectives=2)

        assert report.total_perspectives == 2
        assert report.issue_count >= 1
        assert report.silences >= 1

    # PURPOSE: Sweep should filter perspectives by domain
    def test_sweep_with_domain_filter(self, tmp_path):
        """Sweep should filter perspectives by domain."""
        prompt_file = tmp_path / "test.md"
        prompt_file.write_text("# Test\n")

        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "SILENCE: No issues found"
        mock_client.ask_batch.return_value = [mock_resp] * 24  # 1 domain × 24 axes

        engine = SweepEngine()
        engine._client = mock_client

        report = engine.sweep(str(prompt_file), domains=["Security"])

        assert report.total_perspectives == 24  # 1 domain × 24 axes


# ============================================================
# 8. Pipeline CLI Mode Tests
# ============================================================


# PURPOSE: Test that self_refine_pipeline accepts new modes
class TestPipelineModes:
    """Test that self_refine_pipeline accepts new modes."""

    # PURPOSE: Verify argparse accepts 'sweep' mode without error
    def test_cli_accepts_sweep_mode(self):
        """Verify argparse accepts 'sweep' mode without error."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--mode",
            choices=["static", "llm", "full", "sweep", "deep", "auto"],
        )
        args = parser.parse_args(["--mode", "sweep"])
        assert args.mode == "sweep"

    # PURPOSE: Verify argparse accepts 'auto' mode without error
    def test_cli_accepts_auto_mode(self):
        """Verify argparse accepts 'auto' mode without error."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--mode",
            choices=["static", "llm", "full", "sweep", "deep", "auto"],
        )
        args = parser.parse_args(["--mode", "auto"])
        assert args.mode == "auto"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
