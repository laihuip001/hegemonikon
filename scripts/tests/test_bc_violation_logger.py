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

    def test_bye_section(self, sample_entries):
        """format_bye_section のテスト"""
        from scripts.bc_violation_logger import format_bye_section
        output = format_bye_section(sample_entries)
        assert "BC フィードバック" in output
        assert "叱責率" in output
        assert "自己検出率" in output
        assert "Creator の言葉" in output

    def test_bye_section_empty(self):
        """空エントリの bye_section"""
        from scripts.bc_violation_logger import format_bye_section
        output = format_bye_section([])
        assert "なし" in output

    def test_boot_summary(self, sample_entries):
        """format_boot_summary のテスト"""
        from scripts.bc_violation_logger import format_boot_summary
        output = format_boot_summary(sample_entries)
        assert "BC:" in output
        assert "叱責率" in output
        # 1行サマリーであること
        assert output.count("\n") == 0

    def test_boot_summary_empty(self):
        """空エントリの boot_summary"""
        from scripts.bc_violation_logger import format_boot_summary
        output = format_boot_summary([])
        assert "記録なし" in output or output == ""


# ============================================================
# Tests: Escalation
# ============================================================

class TestEscalation:
    """violations.md 昇格機能のテスト"""

    def test_suggest_escalation_severity(self, sample_entries):
        """severity>=high で昇格候補"""
        from scripts.bc_violation_logger import suggest_escalation
        # sample_entries: skip_bias(high) x1, selective_omission(high) x1
        # violations.md にこれらのパターンが既に存在するため二重提案防止で除外される場合がある
        # テスト用に新パターンを使う
        entries = [
            FeedbackEntry(
                timestamp="2026-02-19T10:00",
                feedback_type="reprimand",
                bc_ids=["BC-1"],
                pattern="new_pattern_a",
                severity="high",
                description="テスト用"
            ),
        ]
        candidates = suggest_escalation(entries, min_severity="high", min_occurrences=99)
        assert len(candidates) == 1
        assert candidates[0]["pattern"] == "new_pattern_a"
        assert candidates[0]["reason"] == "severity"

    def test_suggest_escalation_recurrence(self):
        """min_occurrences で昇格候補"""
        from scripts.bc_violation_logger import suggest_escalation
        entries = [
            FeedbackEntry(timestamp="2026-02-19T10:00", feedback_type="self_detected",
                          pattern="new_pattern_b", severity="low", description="1"),
            FeedbackEntry(timestamp="2026-02-19T11:00", feedback_type="self_detected",
                          pattern="new_pattern_b", severity="low", description="2"),
        ]
        candidates = suggest_escalation(entries, min_severity="critical", min_occurrences=2)
        assert len(candidates) == 1
        assert candidates[0]["reason"] == "recurrence"
        assert candidates[0]["count"] == 2

    def test_suggest_escalation_both(self):
        """severity + recurrence で both"""
        from scripts.bc_violation_logger import suggest_escalation
        entries = [
            FeedbackEntry(timestamp="2026-02-19T10:00", feedback_type="reprimand",
                          pattern="new_pattern_c", severity="high", description="1"),
            FeedbackEntry(timestamp="2026-02-19T11:00", feedback_type="reprimand",
                          pattern="new_pattern_c", severity="high", description="2"),
        ]
        candidates = suggest_escalation(entries, min_severity="high", min_occurrences=2)
        assert len(candidates) == 1
        assert candidates[0]["reason"] == "both"

    def test_suggest_escalation_empty(self):
        """空エントリ"""
        from scripts.bc_violation_logger import suggest_escalation
        assert suggest_escalation([]) == []

    def test_suggest_escalation_no_match(self):
        """条件に合わないエントリ"""
        from scripts.bc_violation_logger import suggest_escalation
        entries = [
            FeedbackEntry(timestamp="2026-02-19T10:00", feedback_type="acknowledgment",
                          pattern="new_pattern_d", severity="low", description="OK"),
        ]
        candidates = suggest_escalation(entries, min_severity="high", min_occurrences=3)
        assert candidates == []

    def test_escalation_template_format(self):
        """テンプレートに必要な YAML フィールドが含まれる"""
        from scripts.bc_violation_logger import suggest_escalation
        entries = [
            FeedbackEntry(timestamp="2026-02-19T10:00", feedback_type="reprimand",
                          bc_ids=["BC-1", "BC-3"], pattern="new_pattern_e",
                          severity="critical", description="テスト違反",
                          creator_words="ダメだ"),
        ]
        candidates = suggest_escalation(entries, min_severity="critical")
        assert len(candidates) >= 1
        tpl = candidates[0]["template"]
        assert "id: V-" in tpl
        assert "pattern: new_pattern_e" in tpl
        assert "severity: critical" in tpl
        assert "BC-1" in tpl
        assert "BC-3" in tpl
        assert "ダメだ" in tpl

    def test_next_violation_id_from_file(self, tmp_path):
        """_next_violation_id のファイルベーステスト"""
        from scripts.bc_violation_logger import _next_violation_id
        md = tmp_path / "violations.md"
        md.write_text("""
### V-001: テスト

```yaml
id: V-001
pattern: skip_bias
```

V-001 の再発についてはこちら。

### V-005: テスト2

```yaml
id: V-005
pattern: overconfidence
```
""")
        result = _next_violation_id(md)
        assert result == "V-006"

    def test_next_violation_id_empty(self, tmp_path):
        """空ファイル"""
        from scripts.bc_violation_logger import _next_violation_id
        md = tmp_path / "violations.md"
        md.write_text("# 違反ログ\n\nまだなし\n")
        result = _next_violation_id(md)
        assert result == "V-001"

    def test_next_violation_id_not_exists(self, tmp_path):
        """ファイルが存在しない"""
        from scripts.bc_violation_logger import _next_violation_id
        result = _next_violation_id(tmp_path / "nonexistent.md")
        assert result == "V-001"

    def test_next_violation_id_ignores_body_mentions(self, tmp_path):
        """本文中の V-NNN 言及は無視する"""
        from scripts.bc_violation_logger import _next_violation_id
        md = tmp_path / "violations.md"
        md.write_text("""
### V-003: テスト

```yaml
id: V-003
pattern: skip_bias
```

V-006 の再発。V-008 と同様。V-999 のような番号も本文にあるが無視。
""")
        result = _next_violation_id(md)
        # id: V-003 のみを検出 → V-004
        assert result == "V-004"

    def test_existing_patterns_detection(self, tmp_path):
        """_existing_patterns_in_violations のテスト"""
        from scripts.bc_violation_logger import _existing_patterns_in_violations
        md = tmp_path / "violations.md"
        md.write_text("""
```yaml
id: V-001
pattern: skip_bias
```

```yaml
id: V-002
pattern: selective_omission
```
""")
        result = _existing_patterns_in_violations(md)
        assert result == {"skip_bias", "selective_omission"}

    def test_duplicate_prevention(self, tmp_path):
        """violations.md に既存のパターンは提案されない"""
        from scripts.bc_violation_logger import (
            suggest_escalation, _existing_patterns_in_violations,
            VIOLATIONS_MD,
        )
        import scripts.bc_violation_logger as mod

        # violations.md に skip_bias が既存
        md = tmp_path / "violations.md"
        md.write_text("""
```yaml
id: V-001
pattern: skip_bias
```
""")
        # monkeypatch 相当: VIOLATIONS_MD を一時的に変更
        orig = mod.VIOLATIONS_MD
        try:
            mod.VIOLATIONS_MD = md
            entries = [
                FeedbackEntry(timestamp="2026-02-19T10:00", feedback_type="reprimand",
                              pattern="skip_bias", severity="high", description="既存"),
                FeedbackEntry(timestamp="2026-02-19T11:00", feedback_type="reprimand",
                              pattern="new_pattern_f", severity="high", description="新規"),
            ]
            candidates = suggest_escalation(entries)
            patterns = [c["pattern"] for c in candidates]
            assert "skip_bias" not in patterns  # 二重提案防止
            assert "new_pattern_f" in patterns  # 新規は提案される
        finally:
            mod.VIOLATIONS_MD = orig
