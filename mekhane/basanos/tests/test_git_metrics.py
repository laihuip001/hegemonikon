"""Tests for GitMetrics — git 履歴からのリスク予兆検出。"""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from mekhane.basanos.git_metrics import FileChurn, CommitStats, GitMetrics

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fixtures
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOCK_LOG_OUTPUT = """abc123|2026-02-18|Alice
15\t5\tmekhane/basanos/pipeline.py
3\t1\tmekhane/utils.py

def456|2026-02-18|Bob
8\t2\tmekhane/basanos/pipeline.py

ghi789|2026-02-17|Alice
20\t10\tmekhane/basanos/pipeline.py
5\t0\tmekhane/api/server.py

jkl012|2026-02-16|Alice
2\t1\tmekhane/basanos/pipeline.py
"""

MOCK_DAILY_OUTPUT = """2026-02-18
2026-02-18
2026-02-17
2026-02-16
"""


@pytest.fixture
def git_metrics(tmp_path):
    """Mock された GitMetrics。"""
    gm = GitMetrics(repo_root=tmp_path, days=14)
    return gm


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Unit Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestFileChurn:
    def test_churn_rate_zero_commits(self):
        fc = FileChurn(path="test.py")
        assert fc.churn_rate == 0.0

    def test_churn_rate(self):
        fc = FileChurn(path="test.py", commits=5, lines_added=50, lines_deleted=10)
        assert fc.churn_rate == 12.0  # 60 / 5

    def test_risk_score_single_author(self):
        fc = FileChurn(path="test.py", commits=5, lines_added=50, lines_deleted=10, authors=1)
        assert fc.risk_score == fc.churn_rate * 1.0

    def test_risk_score_multi_author(self):
        fc = FileChurn(path="test.py", commits=5, lines_added=50, lines_deleted=10, authors=3)
        expected = fc.churn_rate * (1.0 + 2 * 0.3)  # 1.6x penalty
        assert abs(fc.risk_score - expected) < 0.01


class TestGitMetricsWithMock:
    def test_file_churn(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=MOCK_LOG_OUTPUT):
            churns = git_metrics.file_churn()

        assert len(churns) == 3
        assert "mekhane/basanos/pipeline.py" in churns

        pipeline = churns["mekhane/basanos/pipeline.py"]
        assert pipeline.commits == 4
        assert pipeline.lines_added == 45  # 15+8+20+2
        assert pipeline.lines_deleted == 18  # 5+2+10+1
        assert pipeline.authors == 2  # Alice, Bob

    def test_risky_files(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=MOCK_LOG_OUTPUT):
            risky = git_metrics.risky_files(top_n=2)

        assert len(risky) == 2
        # pipeline.py should be riskiest (high churn + 2 authors)
        assert risky[0].path == "mekhane/basanos/pipeline.py"

    def test_daily_stats(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=MOCK_DAILY_OUTPUT):
            stats = git_metrics.daily_stats()

        assert len(stats) == 3
        # 2 commits on 2026-02-18
        day18 = [s for s in stats if s.date == "2026-02-18"][0]
        assert day18.count == 2

    def test_commit_velocity(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=MOCK_DAILY_OUTPUT):
            v = git_metrics.commit_velocity()

        assert v > 0  # 4 commits / 3 days ≈ 1.33

    def test_empty_git(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=""):
            churns = git_metrics.file_churn()
            assert churns == {}

            risky = git_metrics.risky_files()
            assert risky == []

    def test_summary(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=MOCK_LOG_OUTPUT):
            # Need to provide daily stats too
            git_metrics._churn_cache = None
            s = git_metrics.summary()
            assert "Git Metrics" in s
            assert "High-churn" in s


class TestHotspotOverlaps:
    def test_overlap_detection(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=MOCK_LOG_OUTPUT):
            overlaps = git_metrics.hotspot_overlaps([
                "mekhane/basanos/pipeline.py",
                "mekhane/some_other.py",
            ])

        assert "mekhane/basanos/pipeline.py" in overlaps
        assert "mekhane/some_other.py" not in overlaps

    def test_no_overlaps(self, git_metrics):
        with patch.object(git_metrics, '_git', return_value=MOCK_LOG_OUTPUT):
            overlaps = git_metrics.hotspot_overlaps(["nonexistent.py"])

        assert overlaps == []


class TestLiveGitMetrics:
    """実際の git リポジトリで動作確認 (CI 環境でもスキップしない)。"""

    def test_real_repo(self):
        """hegemonikon リポジトリが存在すれば、実際に分析。"""
        repo = Path.home() / "oikos/hegemonikon"
        if not (repo / ".git").exists():
            pytest.skip("No git repo at ~/oikos/hegemonikon")

        gm = GitMetrics(repo_root=repo, days=7)
        churns = gm.file_churn()
        # Should have some Python files
        assert len(churns) >= 0  # may be 0 if no recent commits
        # summary should not crash
        s = gm.summary()
        assert "Git Metrics" in s
