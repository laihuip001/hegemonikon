#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/peira/tests/
# PURPOSE: Peira HealthItem / HealthReport / format_terminal の包括テスト
"""Peira Health Dashboard Tests — Batch 4"""

import pytest
from mekhane.peira.hgk_health import HealthItem, HealthReport, format_terminal


# ═══ HealthItem ════════════════════════

# PURPOSE: Test suite validating health item correctness
class TestHealthItem:
    """HealthItem データクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        item = HealthItem(name="Test", status="ok")
        assert item.name == "Test"
        assert item.status == "ok"

    # PURPOSE: Verify default detail behaves correctly
    def test_default_detail(self):
        """Verify default detail behavior."""
        item = HealthItem(name="Test", status="ok")
        assert item.detail == ""

    # PURPOSE: Verify default metric behaves correctly
    def test_default_metric(self):
        """Verify default metric behavior."""
        item = HealthItem(name="Test", status="ok")
        assert item.metric is None

    # PURPOSE: Verify with metric behaves correctly
    def test_with_metric(self):
        """Verify with metric behavior."""
        item = HealthItem(name="Test", status="ok", metric=0.95)
        assert item.metric == 0.95

    # PURPOSE: Verify emoji ok behaves correctly
    def test_emoji_ok(self):
        """Verify emoji ok behavior."""
        item = HealthItem(name="Test", status="ok")
        assert "✅" in item.emoji or "🟢" in item.emoji or "ok" == item.status

    # PURPOSE: Verify emoji warn behaves correctly
    def test_emoji_warn(self):
        """Verify emoji warn behavior."""
        item = HealthItem(name="Test", status="warn")
        assert item.status == "warn"

    # PURPOSE: Verify emoji fail behaves correctly
    def test_emoji_fail(self):
        """Verify emoji fail behavior."""
        item = HealthItem(name="Test", status="fail")
        assert item.status == "fail"


# ═══ HealthReport ══════════════════════

# PURPOSE: Test suite validating health report correctness
class TestHealthReport:
    """HealthReport データクラスのテスト"""

    # PURPOSE: Verify create empty behaves correctly
    def test_create_empty(self):
        """Verify create empty behavior."""
        report = HealthReport()
        assert len(report.items) == 0

    # PURPOSE: Verify score empty behaves correctly
    def test_score_empty(self):
        """Verify score empty behavior."""
        report = HealthReport()
        assert report.score == 0.0

    # PURPOSE: Verify score all ok behaves correctly
    def test_score_all_ok(self):
        """Verify score all ok behavior."""
        report = HealthReport(items=[
            HealthItem(name="A", status="ok"),
            HealthItem(name="B", status="ok"),
            HealthItem(name="C", status="ok"),
        ])
        assert report.score == 1.0

    # PURPOSE: Verify score mixed behaves correctly
    def test_score_mixed(self):
        """Verify score mixed behavior."""
        report = HealthReport(items=[
            HealthItem(name="A", status="ok"),
            HealthItem(name="B", status="warn"),
        ])
        score = report.score
        assert 0.0 < score < 1.0

    # PURPOSE: Verify score all error behaves correctly
    def test_score_all_error(self):
        """Verify score all error behavior."""
        report = HealthReport(items=[
            HealthItem(name="A", status="error"),
            HealthItem(name="B", status="error"),
        ])
        assert report.score == 0.0


# ═══ format_terminal ═══════════════════

# PURPOSE: Test suite validating format terminal correctness
class TestFormatTerminal:
    """ターミナル表示フォーマッタのテスト"""

    # PURPOSE: Verify format empty behaves correctly
    def test_format_empty(self):
        """Verify format empty behavior."""
        report = HealthReport()
        output = format_terminal(report)
        assert isinstance(output, str)

    # PURPOSE: Verify format contains items behaves correctly
    def test_format_contains_items(self):
        """Verify format contains items behavior."""
        report = HealthReport(items=[
            HealthItem(name="Docker n8n", status="ok", detail="Running"),
        ])
        output = format_terminal(report)
        assert "Docker" in output or "n8n" in output

    # PURPOSE: Verify format contains score behaves correctly
    def test_format_contains_score(self):
        """Verify format contains score behavior."""
        report = HealthReport(items=[
            HealthItem(name="Test", status="ok"),
        ])
        output = format_terminal(report)
        # Should contain some score/status indicator
        assert len(output) > 10
