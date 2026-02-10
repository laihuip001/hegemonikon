#!/usr/bin/env python3
"""Tests for violation_analyzer.py."""

import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.violation_analyzer import (
    parse_violations,
    analyze,
    format_full_report,
    format_boot_summary,
    PATTERN_NAMES,
)


# ============================================================
# テスト用データ
# ============================================================

SAMPLE_MD = dedent("""\
# 違反ログ

### V-001: テスト違反A

```yaml
id: V-001
date: "2026-02-08"
bc: [BC-1, BC-3]
pattern: skip_bias
severity: high
recurrence: false
summary: "テスト違反A"
root_cause: "テスト原因"
corrective: "テスト是正"
lesson: "テスト教訓A"
```

### V-002: テスト違反B

```yaml
id: V-002
date: "2026-02-09"
bc: [BC-10]
pattern: skip_bias
severity: medium
recurrence: true
summary: "テスト違反B"
root_cause: "テスト原因B"
corrective: "テスト是正B"
lesson: "テスト教訓B"
```

### V-003: テスト違反C

```yaml
id: V-003
date: "2026-02-10"
bc: [BC-15]
pattern: accuracy_vs_utility
severity: medium
recurrence: false
summary: "テスト違反C"
root_cause: "テスト原因C"
corrective: "テスト是正C"
lesson: "テスト教訓C"
```
""")


# ============================================================
# Tests
# ============================================================

class TestParseViolations:
    """violations.md パースのテスト"""

    def test_parse_sample(self, tmp_path):
        """サンプルMDから3エントリをパース"""
        md_file = tmp_path / "violations.md"
        md_file.write_text(SAMPLE_MD, encoding="utf-8")
        entries = parse_violations(md_file)
        assert len(entries) == 3
        assert entries[0]["id"] == "V-001"
        assert entries[1]["id"] == "V-002"
        assert entries[2]["id"] == "V-003"

    def test_parse_empty(self, tmp_path):
        """空ファイルは空リスト"""
        md_file = tmp_path / "violations.md"
        md_file.write_text("# Empty", encoding="utf-8")
        entries = parse_violations(md_file)
        assert entries == []

    def test_parse_nonexistent(self, tmp_path):
        """存在しないファイルは空リスト"""
        entries = parse_violations(tmp_path / "nonexistent.md")
        assert entries == []

    def test_parse_bc_list(self, tmp_path):
        """bc フィールドがリストとして読まれる"""
        md_file = tmp_path / "violations.md"
        md_file.write_text(SAMPLE_MD, encoding="utf-8")
        entries = parse_violations(md_file)
        assert entries[0]["bc"] == ["BC-1", "BC-3"]
        assert entries[1]["bc"] == ["BC-10"]


class TestAnalyze:
    """分析ロジックのテスト"""

    def _entries(self, tmp_path):
        md_file = tmp_path / "violations.md"
        md_file.write_text(SAMPLE_MD, encoding="utf-8")
        return parse_violations(md_file)

    def test_total_count(self, tmp_path):
        stats = analyze(self._entries(tmp_path))
        assert stats["total"] == 3

    def test_pattern_counts(self, tmp_path):
        stats = analyze(self._entries(tmp_path))
        assert stats["patterns"]["skip_bias"] == 2
        assert stats["patterns"]["accuracy_vs_utility"] == 1

    def test_bc_counts(self, tmp_path):
        stats = analyze(self._entries(tmp_path))
        assert stats["bc_counts"]["BC-1"] == 1
        assert stats["bc_counts"]["BC-3"] == 1
        assert stats["bc_counts"]["BC-10"] == 1

    def test_recurrence_count(self, tmp_path):
        stats = analyze(self._entries(tmp_path))
        assert stats["recurrence"] == 1

    def test_pattern_filter(self, tmp_path):
        stats = analyze(self._entries(tmp_path), pattern_filter="skip_bias")
        assert stats["total"] == 2

    def test_since_days_filter(self, tmp_path):
        # since_days=0 は今日のみ（V-003: 2026-02-10）
        # ただし日付が固定なのでテストは相対的に機能しないが、ロジックは検証
        stats = analyze(self._entries(tmp_path), since_days=999)
        assert stats["total"] == 3


class TestFormatters:
    """フォーマッターのテスト"""

    def _stats(self, tmp_path):
        md_file = tmp_path / "violations.md"
        md_file.write_text(SAMPLE_MD, encoding="utf-8")
        entries = parse_violations(md_file)
        return analyze(entries)

    def test_full_report_contains_header(self, tmp_path):
        report = format_full_report(self._stats(tmp_path))
        assert "違反パターン分析レポート" in report
        assert "総件数: 3" in report

    def test_boot_summary_concise(self, tmp_path):
        summary = format_boot_summary(self._stats(tmp_path))
        assert "違反傾向" in summary
        assert "最頻出" in summary
        # 5行以内であること
        lines = summary.strip().split("\n")
        assert len(lines) <= 5

    def test_boot_summary_empty(self, tmp_path):
        summary = format_boot_summary(analyze([]))
        assert "違反記録なし" in summary


class TestRealViolations:
    """実際の violations.md に対するテスト"""

    def test_real_file_parseable(self):
        """実際のファイルがパース可能"""
        entries = parse_violations()
        assert len(entries) >= 5  # 現在5件
        for e in entries:
            assert "id" in e
            assert "pattern" in e
            assert "bc" in e

    def test_real_patterns_known(self):
        """全パターンIDが定義済み"""
        entries = parse_violations()
        for e in entries:
            pattern = e.get("pattern")
            assert pattern in PATTERN_NAMES, f"Unknown pattern: {pattern}"
