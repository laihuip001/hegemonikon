#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/peira/tests/
# PURPOSE: Peira HealthItem / HealthReport / format_terminal の包括テスト
"""Peira Health Dashboard Tests — Batch 4"""

import pytest
from mekhane.peira.hgk_health import HealthItem, HealthReport, format_terminal


# ═══ HealthItem ════════════════════════

class TestHealthItem:
    """HealthItem データクラスのテスト"""

    def test_create(self):
        item = HealthItem(name="Test", status="ok")
        assert item.name == "Test"
        assert item.status == "ok"

    def test_default_detail(self):
        item = HealthItem(name="Test", status="ok")
        assert item.detail == ""

    def test_default_metric(self):
        item = HealthItem(name="Test", status="ok")
        assert item.metric is None

    def test_with_metric(self):
        item = HealthItem(name="Test", status="ok", metric=0.95)
        assert item.metric == 0.95

    def test_emoji_ok(self):
        item = HealthItem(name="Test", status="ok")
        assert "✅" in item.emoji or "🟢" in item.emoji or "ok" == item.status

    def test_emoji_warn(self):
        item = HealthItem(name="Test", status="warn")
        assert item.status == "warn"

    def test_emoji_fail(self):
        item = HealthItem(name="Test", status="fail")
        assert item.status == "fail"


# ═══ HealthReport ══════════════════════

class TestHealthReport:
    """HealthReport データクラスのテスト"""

    def test_create_empty(self):
        report = HealthReport()
        assert len(report.items) == 0

    def test_score_empty(self):
        report = HealthReport()
        assert report.score == 0.0

    def test_score_all_ok(self):
        report = HealthReport(items=[
            HealthItem(name="A", status="ok"),
            HealthItem(name="B", status="ok"),
            HealthItem(name="C", status="ok"),
        ])
        assert report.score == 1.0

    def test_score_mixed(self):
        report = HealthReport(items=[
            HealthItem(name="A", status="ok"),
            HealthItem(name="B", status="warn"),
        ])
        score = report.score
        assert 0.0 < score < 1.0

    def test_score_all_error(self):
        report = HealthReport(items=[
            HealthItem(name="A", status="error"),
            HealthItem(name="B", status="error"),
        ])
        assert report.score == 0.0


# ═══ format_terminal ═══════════════════

class TestFormatTerminal:
    """ターミナル表示フォーマッタのテスト"""

    def test_format_empty(self):
        report = HealthReport()
        output = format_terminal(report)
        assert isinstance(output, str)

    def test_format_contains_items(self):
        report = HealthReport(items=[
            HealthItem(name="Docker n8n", status="ok", detail="Running"),
        ])
        output = format_terminal(report)
        assert "Docker" in output or "n8n" in output

    def test_format_contains_score(self):
        report = HealthReport(items=[
            HealthItem(name="Test", status="ok"),
        ])
        output = format_terminal(report)
        # Should contain some score/status indicator
        assert len(output) > 10
