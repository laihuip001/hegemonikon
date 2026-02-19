#!/usr/bin/env python3
"""Tests for bc_violation_logger.py."""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.bc_violation_logger import (
    FeedbackEntry,
    log_entry,
    read_all_entries,
    filter_entries,
    compute_stats,
    compute_trend,
    format_dashboard,
    format_session_summary,
    LOG_DIR,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def log_dir(tmp_path, monkeypatch):
    """テスト用ログディレクトリ"""
    import scripts.bc_violation_logger as mod
    monkeypatch.setattr(mod, "LOG_DIR", tmp_path)
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "violations.jsonl")
    return tmp_path


@pytest.fixture
def sample_entries() -> list[FeedbackEntry]:
    """テスト用サンプルデータ"""
    now = datetime.now()
    return [
        FeedbackEntry(
            timestamp=(now - timedelta(days=2)).isoformat(),
            feedback_type="reprimand",
            bc_ids=["BC-1", "BC-3"],
            pattern="skip_bias",
            severity="high",
            description="WF定義を読まずに実行",
            creator_words="真剣にやれコラ",
            session_id="session-001",
        ),
        FeedbackEntry(
            timestamp=(now - timedelta(days=1)).isoformat(),
            feedback_type="self_detected",
            bc_ids=["BC-10"],
            pattern="skip_bias",
            severity="medium",
            description="dispatch()を使わず手動実行",
            session_id="session-002",
        ),
        FeedbackEntry(
            timestamp=now.isoformat(),
            feedback_type="acknowledgment",
            description="圏論分析の深さが良い",
            creator_words="すごい！",
            session_id="session-002",
        ),
        FeedbackEntry(
            timestamp=now.isoformat(),
            feedback_type="reprimand",
            bc_ids=["BC-1", "BC-7"],
            pattern="selective_omission",
            severity="high",
            description="PJリストを省略",
            creator_words="省略するな",
            session_id="session-002",
        ),
    ]


# ============================================================
# Tests: Data Model
# ============================================================

class TestFeedbackEntry:
    """FeedbackEntry のテスト"""

    def test_to_dict_roundtrip(self):
        entry = FeedbackEntry(
            timestamp="2026-02-19T05:00:00",
            feedback_type="reprimand",
            bc_ids=["BC-1"],
            pattern="skip_bias",
            severity="high",
            description="テスト",
            creator_words="コラ",
        )
        d = entry.to_dict()
        restored = FeedbackEntry.from_dict(d)
        assert restored.feedback_type == "reprimand"
        assert restored.bc_ids == ["BC-1"]
        assert restored.creator_words == "コラ"

    def test_from_dict_ignores_unknown(self):
        """未知のフィールドは無視"""
        d = {
            "timestamp": "2026-02-19T05:00:00",
            "feedback_type": "reprimand",
            "unknown_field": "value",
        }
        entry = FeedbackEntry.from_dict(d)
        assert entry.feedback_type == "reprimand"


# ============================================================
# Tests: Logger I/O
# ============================================================

class TestLoggerIO:
    """ログ書込/読込テスト"""

    def test_log_and_read(self, log_dir, sample_entries):
        """書込→読込の往復"""
        for e in sample_entries:
            log_entry(e)

        entries = read_all_entries(log_dir / "violations.jsonl")
        assert len(entries) == 4
        assert entries[0].feedback_type == "reprimand"
        assert entries[2].feedback_type == "acknowledgment"

    def test_empty_file(self, log_dir):
        """空ファイルは空リスト"""
        entries = read_all_entries(log_dir / "violations.jsonl")
        assert entries == []

    def test_append_mode(self, log_dir):
        """複数回のアペンド"""
        entry1 = FeedbackEntry(
            timestamp="2026-02-19T01:00:00",
            feedback_type="reprimand",
        )
        entry2 = FeedbackEntry(
            timestamp="2026-02-19T02:00:00",
            feedback_type="acknowledgment",
        )
        log_entry(entry1)
        log_entry(entry2)
        entries = read_all_entries(log_dir / "violations.jsonl")
        assert len(entries) == 2

    def test_jsonl_format(self, log_dir):
        """JSONL 形式 (1行1レコード)"""
        entry = FeedbackEntry(
            timestamp="2026-02-19T01:00:00",
            feedback_type="reprimand",
        )
        log_entry(entry)
        content = (log_dir / "violations.jsonl").read_text()
        lines = content.strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["feedback_type"] == "reprimand"


# ============================================================
# Tests: Filtering
# ============================================================

class TestFilter:
    """フィルタリングテスト"""

    def test_filter_by_type(self, sample_entries):
        result = filter_entries(sample_entries, feedback_type="reprimand")
        assert len(result) == 2

    def test_filter_by_pattern(self, sample_entries):
        result = filter_entries(sample_entries, pattern="skip_bias")
        assert len(result) == 2

    def test_filter_by_session(self, sample_entries):
        result = filter_entries(sample_entries, session_id="session-002")
        assert len(result) == 3

    def test_filter_by_days(self, sample_entries):
        result = filter_entries(sample_entries, since_days=1)
        assert len(result) >= 2  # today + yesterday


# ============================================================
# Tests: Statistics
# ============================================================

class TestStatistics:
    """統計計算テスト"""

    def test_basic_counts(self, sample_entries):
        stats = compute_stats(sample_entries)
        assert stats["total"] == 4
        assert stats["by_type"]["reprimand"] == 2
        assert stats["by_type"]["acknowledgment"] == 1
        assert stats["by_type"]["self_detected"] == 1

    def test_bc_counts(self, sample_entries):
        stats = compute_stats(sample_entries)
        assert stats["by_bc"]["BC-1"] == 2  # V-001 + V-004
        assert stats["by_bc"]["BC-10"] == 1

    def test_self_detection_rate(self, sample_entries):
        stats = compute_stats(sample_entries)
        # self_detected=1 / (reprimand=2 + self_detected=1) = 33.3%
        assert stats["self_detection_rate"] == pytest.approx(33.3, abs=0.1)

    def test_reprimand_rate(self, sample_entries):
        stats = compute_stats(sample_entries)
        # reprimand=2 / (reprimand=2 + acknowledgment=1) = 66.7%
        assert stats["reprimand_rate"] == pytest.approx(66.7, abs=0.1)

    def test_empty_stats(self):
        stats = compute_stats([])
        assert stats["total"] == 0
        assert stats["self_detection_rate"] == 0.0

    def test_creator_words(self, sample_entries):
        stats = compute_stats(sample_entries)
        assert len(stats["creator_words_samples"]) >= 2
        words = [s["words"] for s in stats["creator_words_samples"]]
        assert any("省略" in w for w in words)


# ============================================================
# Tests: Trend
# ============================================================

class TestTrend:
    """トレンド計算テスト"""

    def test_trend_structure(self, sample_entries):
        trend = compute_trend(sample_entries, weeks=4)
        assert len(trend) == 4
        for w in trend:
            assert "week" in w
            assert "reprimands" in w
            assert "acknowledgments" in w
            assert "self_detected" in w


# ============================================================
# Tests: Formatters
# ============================================================

class TestFormatters:
    """フォーマッターテスト"""

    def test_dashboard_output(self, sample_entries):
        output = format_dashboard(sample_entries)
        assert "ダッシュボード" in output
        assert "叱責" in output
        assert "承認" in output
        assert "自己検出率" in output

    def test_session_summary(self, sample_entries):
        output = format_session_summary(sample_entries, session_id="session-002")
        assert "セッション" in output

    def test_session_summary_empty(self):
        output = format_session_summary([])
        assert "違反記録なし" in output

    def test_dashboard_with_creator_words(self, sample_entries):
        output = format_dashboard(sample_entries)
        assert "Creator の言葉" in output
