# PROOF: [L2/Mekhane] <- mekhane/tests/ A0->Auto->AddedByCI
"""Tests for TrendAnalyzer — 合成データで全機能をテスト。"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from mekhane.basanos.trend_analyzer import FileProfile, TrendAnalyzer
from mekhane.basanos.pipeline import DomainWeight, RotationState


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fixtures — 合成レポートデータ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _make_issue(file: str, name: str, severity: str = "medium") -> dict:
    return {
        "file": file,
        "name": name,
        "severity": severity,
        "code": "AI-001",
        "location": f"{file}:10",
        "description": f"Test issue: {name}",
    }


def _make_report(date: str, issues: list) -> dict:
    return {
        "timestamp": f"{date}T06:00:00",
        "files_scanned": 10,
        "l0_issues": issues,
        "l1_results": [],
        "l2_triggered": False,
        "l2_session_id": None,
        "domains_reviewed": ["Naming", "Logic"],
        "needs_l2": len([i for i in issues if i["severity"] in ("critical", "high")]) > 0,
        "summary": f"{len(issues)} issues found",
    }


@pytest.fixture
def reviews_dir(tmp_path):
    """7日分の合成レポートデータを生成。"""
    reviews = tmp_path / "daily_reviews"
    reviews.mkdir()

    today = datetime.now()
    for i in range(7):
        date = (today - timedelta(days=6 - i)).strftime("%Y-%m-%d")
        issues = [
            _make_issue("mekhane/basanos/pipeline.py", "Naming Hallucination", "high"),
        ]
        # pipeline.py は毎日出る (streak=7)
        # utils.py は前半3日だけ
        if i < 3:
            issues.append(
                _make_issue("mekhane/utils.py", "Logic Contradiction", "medium")
            )
        # day 5-6: 新しいファイルが登場
        if i >= 5:
            issues.append(
                _make_issue("mekhane/api/server.py", "Boundary Error", "critical")
            )

        report = _make_report(date, issues)
        (reviews / f"{date}.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2)
        )

    return reviews


@pytest.fixture
def analyzer(reviews_dir):
    return TrendAnalyzer(reviews_dir=reviews_dir, days=14)


@pytest.fixture
def empty_analyzer(tmp_path):
    empty_dir = tmp_path / "empty_reviews"
    empty_dir.mkdir()
    return TrendAnalyzer(reviews_dir=empty_dir, days=14)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestLoadReports:
    def test_load_all(self, analyzer):
        reports = analyzer.load_reports()
        assert len(reports) == 7
        assert all("_date" in r for r in reports)

    def test_dates_sorted(self, analyzer):
        analyzer.load_reports()
        assert analyzer.dates == sorted(analyzer.dates)
        assert len(analyzer.dates) == 7

    def test_empty_dir(self, empty_analyzer):
        reports = empty_analyzer.load_reports()
        assert reports == []
        assert empty_analyzer.dates == []

    def test_nonexistent_dir(self, tmp_path):
        a = TrendAnalyzer(reviews_dir=tmp_path / "nonexistent")
        assert a.load_reports() == []


class TestFileProfiles:
    def test_profiles_count(self, analyzer):
        profiles = analyzer.file_profiles()
        assert len(profiles) == 3  # pipeline.py, utils.py, server.py

    def test_pipeline_streak(self, analyzer):
        profiles = analyzer.file_profiles()
        p = profiles["mekhane/basanos/pipeline.py"]
        assert p.total_issues == 7
        assert p.streak == 7  # every day
        assert p.days_active == 7

    def test_utils_streak(self, analyzer):
        profiles = analyzer.file_profiles()
        p = profiles["mekhane/utils.py"]
        assert p.total_issues == 3
        assert p.streak == 0  # not in recent days
        assert p.days_active == 3

    def test_server_streak(self, analyzer):
        profiles = analyzer.file_profiles()
        p = profiles["mekhane/api/server.py"]
        assert p.total_issues == 2
        assert p.streak == 2  # last 2 days
        assert p.days_active == 2

    def test_issue_types_tracked(self, analyzer):
        profiles = analyzer.file_profiles()
        p = profiles["mekhane/basanos/pipeline.py"]
        assert "Naming" in p.issue_types
        assert p.issue_types["Naming"] == 7


class TestHotFiles:
    def test_ranking(self, analyzer):
        hot = analyzer.hot_files(top_n=3)
        assert len(hot) == 3
        # pipeline.py should be hottest (7 issues, 7 streak)
        assert hot[0].path == "mekhane/basanos/pipeline.py"

    def test_top_n(self, analyzer):
        hot = analyzer.hot_files(top_n=1)
        assert len(hot) == 1

    def test_heat_positive(self, analyzer):
        hot = analyzer.hot_files()
        for fp in hot:
            assert fp.heat >= 0.0

    def test_empty(self, empty_analyzer):
        hot = empty_analyzer.hot_files()
        assert hot == []


class TestCategoryTrends:
    def test_categories_present(self, analyzer):
        trends = analyzer.category_trends()
        assert "Naming" in trends
        assert "Logic" in trends
        assert "Boundary" in trends

    def test_naming_all_days(self, analyzer):
        trends = analyzer.category_trends()
        # Naming appears every day
        assert sum(trends["Naming"]) == 7

    def test_velocity_naming(self, analyzer):
        velocity = analyzer.category_velocity()
        # Naming is stable (1/day) → velocity ≈ 0
        assert abs(velocity.get("Naming", 0)) < 0.5

    def test_velocity_boundary_rising(self, analyzer):
        velocity = analyzer.category_velocity()
        # Boundary only in last 2 days → positive slope
        assert velocity.get("Boundary", 0) > 0


class TestThresholds:
    def test_suggest_thresholds(self, analyzer):
        thresholds = analyzer.suggest_thresholds()
        assert len(thresholds) > 0
        for cat, t in thresholds.items():
            assert 0.3 <= t <= 1.5

    def test_empty(self, empty_analyzer):
        thresholds = empty_analyzer.suggest_thresholds()
        assert thresholds == {}


class TestApplyToRotation:
    def test_apply(self, analyzer):
        state = RotationState(
            domains={
                "Naming": DomainWeight(name="Naming", weight=1.0),
                "Logic": DomainWeight(name="Logic", weight=1.0),
                "Boundary": DomainWeight(name="Boundary", weight=0.8),
            }
        )
        changes = analyzer.apply_to_rotation(state)

        assert "hot_files" in changes
        assert len(changes["hot_files"]) > 0
        # Naming weight should have increased (pipeline.py is hot, top category=Naming)
        assert state.domains["Naming"].weight >= 1.0

    def test_empty_data(self, empty_analyzer):
        state = RotationState(domains={})
        changes = empty_analyzer.apply_to_rotation(state)
        assert changes["hot_files"] == []
        assert changes["weight_adjustments"] == {}


class TestSummary:
    def test_summary_with_data(self, analyzer):
        s = analyzer.summary()
        assert "Trend Analysis" in s
        assert "Hot files" in s

    def test_summary_empty(self, empty_analyzer):
        s = empty_analyzer.summary()
        assert "No data" in s


class TestFileProfileHeat:
    def test_zero_issues(self):
        fp = FileProfile(path="test.py")
        assert fp.heat == 0.0

    def test_heat_increases_with_streak(self):
        fp1 = FileProfile(
            path="a.py", total_issues=5, days_active=5, streak=1,
            last_seen=datetime.now().strftime("%Y-%m-%d"),
        )
        fp2 = FileProfile(
            path="b.py", total_issues=5, days_active=5, streak=5,
            last_seen=datetime.now().strftime("%Y-%m-%d"),
        )
        assert fp2.heat > fp1.heat
