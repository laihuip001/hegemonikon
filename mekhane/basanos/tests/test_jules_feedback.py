# PROOF: [L3/テスト] <- mekhane/basanos/tests/ A0→Implementation→test_jules_feedback
"""Tests for JulesFeedback — L2結果→L0精度フィードバック。"""

import json
from pathlib import Path

import pytest

from mekhane.basanos.jules_feedback import JulesFeedback, FeedbackEntry
from mekhane.basanos.pipeline import DomainWeight, RotationState


# PURPOSE: feedback_dir の処理
@pytest.fixture
def feedback_dir(tmp_path):
    d = tmp_path / "jules_feedback"
    d.mkdir()
    return d


# PURPOSE: fb の処理
@pytest.fixture
def fb(feedback_dir):
    return JulesFeedback(feedback_dir=feedback_dir)


# PURPOSE: 過去のフィードバック履歴を持つインスタンス。
@pytest.fixture
def fb_with_history(feedback_dir):
    """過去のフィードバック履歴を持つインスタンス。"""
    fb = JulesFeedback(feedback_dir=feedback_dir)
    history = [
        {
            "session_id": "s1",
            "date": "2026-02-18",
            "verdict": "fix",
            "issues_reviewed": 3,
            "issues_fixed": 2,
            "issues_dismissed": 0,
            "checker_adjustments": {"AI-001": 0.05, "AI-003": 0.05},
        },
        {
            "session_id": "s2",
            "date": "2026-02-17",
            "verdict": "false_positive",
            "issues_reviewed": 2,
            "issues_dismissed": 2,
            "issues_fixed": 0,
            "checker_adjustments": {"AI-001": -0.1, "AI-005": -0.1},
        },
        {
            "session_id": "s3",
            "date": "2026-02-16",
            "verdict": "fix",
            "issues_reviewed": 1,
            "issues_fixed": 1,
            "issues_dismissed": 0,
            "checker_adjustments": {"AI-001": 0.05},
        },
    ]
    (feedback_dir / "feedback_history.json").write_text(
        json.dumps(history, indent=2)
    )
    return fb


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FeedbackEntry
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Test feedback entry の実装
class TestFeedbackEntry:
    # PURPOSE: to_dict をテストする
    def test_to_dict(self):
        e = FeedbackEntry(
            session_id="s1", date="2026-02-18", verdict="fix",
            issues_reviewed=3, issues_fixed=2,
            checker_adjustments={"AI-001": 0.05},
        )
        d = e.to_dict()
        assert d["session_id"] == "s1"
        assert d["verdict"] == "fix"
        assert d["checker_adjustments"]["AI-001"] == 0.05

    # PURPOSE: from_dict をテストする
    def test_from_dict(self):
        d = {"session_id": "s2", "date": "2026-02-17", "verdict": "false_positive"}
        e = FeedbackEntry.from_dict(d)
        assert e.session_id == "s2"
        assert e.verdict == "false_positive"

    # PURPOSE: roundtrip をテストする
    def test_roundtrip(self):
        e = FeedbackEntry(
            session_id="s1", date="2026-02-18", verdict="fix",
            checker_adjustments={"AI-001": 0.05},
        )
        e2 = FeedbackEntry.from_dict(e.to_dict())
        assert e.session_id == e2.session_id
        assert e.checker_adjustments == e2.checker_adjustments


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Registration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Test registration の実装
class TestRegistration:
    # PURPOSE: register_session をテストする
    def test_register_session(self, fb, feedback_dir):
        issues = [
            {"code": "AI-001", "name": "Naming Hallucination"},
            {"code": "AI-003", "name": "Context Drift"},
        ]
        fb.register_session("session-abc", issues)

        pending = json.loads((feedback_dir / "pending_sessions.json").read_text())
        assert len(pending) == 1
        assert pending[0]["session_id"] == "session-abc"
        assert pending[0]["issue_count"] == 2

    # PURPOSE: register_dedup をテストする
    def test_register_dedup(self, fb):
        issues = [{"code": "AI-001"}]
        fb.register_session("session-abc", issues)
        fb.register_session("session-abc", issues)  # duplicate

        pending = fb._load_pending()
        assert len(pending) == 1

    # PURPOSE: register_multiple をテストする
    def test_register_multiple(self, fb):
        fb.register_session("s1", [{"code": "AI-001"}])
        fb.register_session("s2", [{"code": "AI-003"}])

        pending = fb._load_pending()
        assert len(pending) == 2


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Checker Adjustments
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Test checker adjustments の実装
class TestCheckerAdjustments:
    # PURPOSE: fix_positive_adjustment をテストする
    def test_fix_positive_adjustment(self, fb):
        adj = fb._compute_checker_adjustments(
            ["AI-001", "AI-003"], "fix", {"fixed": 2}
        )
        assert adj["AI-001"] == 0.05
        assert adj["AI-003"] == 0.05

    # PURPOSE: false_positive_negative_adjustment をテストする
    def test_false_positive_negative_adjustment(self, fb):
        adj = fb._compute_checker_adjustments(
            ["AI-001"], "false_positive", {"dismissed": 1}
        )
        assert adj["AI-001"] == -0.1

    # PURPOSE: error_no_adjustment をテストする
    def test_error_no_adjustment(self, fb):
        adj = fb._compute_checker_adjustments(
            ["AI-001"], "error", {}
        )
        assert adj == {}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cumulative Adjustments
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Test cumulative adjustments の実装
class TestCumulativeAdjustments:
    # PURPOSE: cumulative をテストする
    def test_cumulative(self, fb_with_history):
        adj = fb_with_history.compute_cumulative_adjustments()
        # AI-001: +0.05 +(-0.1) +0.05 = 0.0
        assert adj["AI-001"] == 0.0
        # AI-003: +0.05
        assert adj["AI-003"] == 0.05
        # AI-005: -0.1
        assert adj["AI-005"] == -0.1

    # PURPOSE: empty_history をテストする
    def test_empty_history(self, fb):
        adj = fb.compute_cumulative_adjustments()
        assert adj == {}

    # PURPOSE: clamp をテストする
    def test_clamp(self, feedback_dir):
        fb = JulesFeedback(feedback_dir=feedback_dir)
        # Create extreme history
        history = [
            {
                "session_id": f"s{i}",
                "date": "2026-02-18",
                "verdict": "false_positive",
                "checker_adjustments": {"AI-001": -0.5},
            }
            for i in range(10)
        ]
        (feedback_dir / "feedback_history.json").write_text(json.dumps(history))

        adj = fb.compute_cumulative_adjustments()
        assert adj["AI-001"] == -1.0  # clamped at -1.0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Apply to Rotation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Test apply to rotation の実装
class TestApplyToRotation:
    # PURPOSE: apply_adjustments をテストする
    def test_apply_adjustments(self, fb_with_history):
        state = RotationState(
            domains={
                "Naming": DomainWeight(name="Naming", weight=1.0),
                "Logic": DomainWeight(name="Logic", weight=1.0),
            }
        )
        changes = fb_with_history.apply_to_rotation(state)

        # AI-001/AI-003/AI-005 all map to "AI" → "Naming"
        # But only if domain exists
        assert isinstance(changes, dict)

    # PURPOSE: empty_feedback をテストする
    def test_empty_feedback(self, fb):
        state = RotationState(domains={})
        changes = fb.apply_to_rotation(state)
        assert changes["adjustments_applied"] == {}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Test summary の実装
class TestSummary:
    # PURPOSE: summary_with_data をテストする
    def test_summary_with_data(self, fb_with_history):
        s = fb_with_history.summary()
        assert "Jules Feedback" in s
        assert "fix" in s
        assert "false_positive" in s

    # PURPOSE: summary_empty をテストする
    def test_summary_empty(self, fb):
        s = fb.summary()
        assert "No sessions" in s


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Collect — without Jules API (mock)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Test collect の実装
class TestCollect:
    # PURPOSE: collect_no_pending をテストする
    def test_collect_no_pending(self, fb):
        completed = fb.collect_completed()
        assert completed == []

    # PURPOSE: API key がない場合、pending は保持される。
    def test_collect_with_no_api(self, fb):
        """API key がない場合、pending は保持される。"""
        fb.register_session("s1", [{"code": "AI-001"}])
        completed = fb.collect_completed()
        # No API key → session stays pending
        assert completed == []
        # Still in pending
        pending = fb._load_pending()
        assert len(pending) == 1
