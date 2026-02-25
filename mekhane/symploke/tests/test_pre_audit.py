#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/symploke/tests/ O4→pre-audit→test_pre_audit が担う
# PURPOSE: Pre-audit スコアリングとファイルソートのユニットテスト
"""Pre-audit scoring and file reordering tests."""

import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


# --- Inline mock (AIAuditor の依存を避ける) ---


# PURPOSE: Mock severity の実装
class MockSeverity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# PURPOSE: Mock issue の実装
@dataclass
class MockIssue:
    severity: str
    code: str = "AI-000"
    name: str = "Test"
    line: int = 1
    message: str = "test"


# PURPOSE: Mock audit result の実装
@dataclass
class MockAuditResult:
    file_path: Path
    issues: List[MockIssue] = field(default_factory=list)


# --- スコアリング関数 (scheduler と同じロジックを抽出) ---


# PURPOSE: Pre-audit スコア計算。scheduler 内の inline ロジックと同一。
def calculate_audit_score(issues: list[MockIssue]) -> int:
    """Pre-audit スコア計算。scheduler 内の inline ロジックと同一。"""
    return sum(
        10 if i.severity == MockSeverity.CRITICAL
        else 5 if i.severity == MockSeverity.HIGH
        else 1 if i.severity == MockSeverity.MEDIUM
        else 0
        for i in issues
    )


# PURPOSE: スコア降順でファイルを再ソート。
def reorder_files_by_score(
    files: list[str], file_scores: dict[str, int]
) -> list[str]:
    """スコア降順でファイルを再ソート。"""
    return sorted(files, key=lambda f: file_scores.get(f, 0), reverse=True)


# === Tests ===


# PURPOSE: スコアリング公式のテスト。
class TestAuditScoring(unittest.TestCase):
    """スコアリング公式のテスト。"""

    # PURPOSE: critical_scores_10 をテストする
    def test_critical_scores_10(self):
        issues = [MockIssue(severity=MockSeverity.CRITICAL)]
        self.assertEqual(calculate_audit_score(issues), 10)

    # PURPOSE: high_scores_5 をテストする
    def test_high_scores_5(self):
        issues = [MockIssue(severity=MockSeverity.HIGH)]
        self.assertEqual(calculate_audit_score(issues), 5)

    # PURPOSE: medium_scores_1 をテストする
    def test_medium_scores_1(self):
        issues = [MockIssue(severity=MockSeverity.MEDIUM)]
        self.assertEqual(calculate_audit_score(issues), 1)

    # PURPOSE: low_scores_0 をテストする
    def test_low_scores_0(self):
        issues = [MockIssue(severity=MockSeverity.LOW)]
        self.assertEqual(calculate_audit_score(issues), 0)

    # PURPOSE: mixed_severity をテストする
    def test_mixed_severity(self):
        issues = [
            MockIssue(severity=MockSeverity.CRITICAL),  # 10
            MockIssue(severity=MockSeverity.HIGH),       # 5
            MockIssue(severity=MockSeverity.MEDIUM),     # 1
            MockIssue(severity=MockSeverity.LOW),        # 0
        ]
        self.assertEqual(calculate_audit_score(issues), 16)

    # PURPOSE: no_issues_scores_zero をテストする
    def test_no_issues_scores_zero(self):
        self.assertEqual(calculate_audit_score([]), 0)

    # PURPOSE: multiple_criticals をテストする
    def test_multiple_criticals(self):
        issues = [MockIssue(severity=MockSeverity.CRITICAL)] * 3
        self.assertEqual(calculate_audit_score(issues), 30)


# PURPOSE: ファイル優先度再ソートのテスト。
class TestFileReordering(unittest.TestCase):
    """ファイル優先度再ソートのテスト。"""

    # PURPOSE: sort_descending_by_score をテストする
    def test_sort_descending_by_score(self):
        files = ["a.py", "b.py", "c.py"]
        scores = {"a.py": 5, "b.py": 30, "c.py": 10}
        result = reorder_files_by_score(files, scores)
        self.assertEqual(result, ["b.py", "c.py", "a.py"])

    # PURPOSE: zero_score_files_at_end をテストする
    def test_zero_score_files_at_end(self):
        files = ["clean.py", "dirty.py"]
        scores = {"clean.py": 0, "dirty.py": 15}
        result = reorder_files_by_score(files, scores)
        self.assertEqual(result, ["dirty.py", "clean.py"])

    # PURPOSE: missing_score_treated_as_zero をテストする
    def test_missing_score_treated_as_zero(self):
        files = ["known.py", "unknown.py"]
        scores = {"known.py": 10}
        result = reorder_files_by_score(files, scores)
        self.assertEqual(result, ["known.py", "unknown.py"])

    # PURPOSE: equal_scores_preserve_order をテストする
    def test_equal_scores_preserve_order(self):
        files = ["a.py", "b.py", "c.py"]
        scores = {"a.py": 5, "b.py": 5, "c.py": 5}
        result = reorder_files_by_score(files, scores)
        # Python sort is stable — equal elements preserve original order
        self.assertEqual(result, ["a.py", "b.py", "c.py"])

    # PURPOSE: empty_files をテストする
    def test_empty_files(self):
        result = reorder_files_by_score([], {})
        self.assertEqual(result, [])

    # PURPOSE: single_file をテストする
    def test_single_file(self):
        result = reorder_files_by_score(["only.py"], {"only.py": 42})
        self.assertEqual(result, ["only.py"])


if __name__ == "__main__":
    unittest.main()
