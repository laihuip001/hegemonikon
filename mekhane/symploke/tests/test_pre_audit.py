# PROOF: [L2/Mekhane] <- mekhane/symploke/tests/ A0->Auto->AddedByCI
#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/symploke/tests/ O4→pre-audit→test_pre_audit が担う
# PURPOSE: Pre-audit スコアリングとファイルソートのユニットテスト
"""Pre-audit scoring and file reordering tests."""

import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


# --- Inline mock (AIAuditor の依存を避ける) ---


class MockSeverity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MockIssue:
    severity: str
    code: str = "AI-000"
    name: str = "Test"
    line: int = 1
    message: str = "test"


@dataclass
class MockAuditResult:
    file_path: Path
    issues: List[MockIssue] = field(default_factory=list)


# --- スコアリング関数 (scheduler と同じロジックを抽出) ---


def calculate_audit_score(issues: list[MockIssue]) -> int:
    """Pre-audit スコア計算。scheduler 内の inline ロジックと同一。"""
    return sum(
        10 if i.severity == MockSeverity.CRITICAL
        else 5 if i.severity == MockSeverity.HIGH
        else 1 if i.severity == MockSeverity.MEDIUM
        else 0
        for i in issues
    )


def reorder_files_by_score(
    files: list[str], file_scores: dict[str, int]
) -> list[str]:
    """スコア降順でファイルを再ソート。"""
    return sorted(files, key=lambda f: file_scores.get(f, 0), reverse=True)


# === Tests ===


class TestAuditScoring(unittest.TestCase):
    """スコアリング公式のテスト。"""

    def test_critical_scores_10(self):
        issues = [MockIssue(severity=MockSeverity.CRITICAL)]
        self.assertEqual(calculate_audit_score(issues), 10)

    def test_high_scores_5(self):
        issues = [MockIssue(severity=MockSeverity.HIGH)]
        self.assertEqual(calculate_audit_score(issues), 5)

    def test_medium_scores_1(self):
        issues = [MockIssue(severity=MockSeverity.MEDIUM)]
        self.assertEqual(calculate_audit_score(issues), 1)

    def test_low_scores_0(self):
        issues = [MockIssue(severity=MockSeverity.LOW)]
        self.assertEqual(calculate_audit_score(issues), 0)

    def test_mixed_severity(self):
        issues = [
            MockIssue(severity=MockSeverity.CRITICAL),  # 10
            MockIssue(severity=MockSeverity.HIGH),       # 5
            MockIssue(severity=MockSeverity.MEDIUM),     # 1
            MockIssue(severity=MockSeverity.LOW),        # 0
        ]
        self.assertEqual(calculate_audit_score(issues), 16)

    def test_no_issues_scores_zero(self):
        self.assertEqual(calculate_audit_score([]), 0)

    def test_multiple_criticals(self):
        issues = [MockIssue(severity=MockSeverity.CRITICAL)] * 3
        self.assertEqual(calculate_audit_score(issues), 30)


class TestFileReordering(unittest.TestCase):
    """ファイル優先度再ソートのテスト。"""

    def test_sort_descending_by_score(self):
        files = ["a.py", "b.py", "c.py"]
        scores = {"a.py": 5, "b.py": 30, "c.py": 10}
        result = reorder_files_by_score(files, scores)
        self.assertEqual(result, ["b.py", "c.py", "a.py"])

    def test_zero_score_files_at_end(self):
        files = ["clean.py", "dirty.py"]
        scores = {"clean.py": 0, "dirty.py": 15}
        result = reorder_files_by_score(files, scores)
        self.assertEqual(result, ["dirty.py", "clean.py"])

    def test_missing_score_treated_as_zero(self):
        files = ["known.py", "unknown.py"]
        scores = {"known.py": 10}
        result = reorder_files_by_score(files, scores)
        self.assertEqual(result, ["known.py", "unknown.py"])

    def test_equal_scores_preserve_order(self):
        files = ["a.py", "b.py", "c.py"]
        scores = {"a.py": 5, "b.py": 5, "c.py": 5}
        result = reorder_files_by_score(files, scores)
        # Python sort is stable — equal elements preserve original order
        self.assertEqual(result, ["a.py", "b.py", "c.py"])

    def test_empty_files(self):
        result = reorder_files_by_score([], {})
        self.assertEqual(result, [])

    def test_single_file(self):
        result = reorder_files_by_score(["only.py"], {"only.py": 42})
        self.assertEqual(result, ["only.py"])


if __name__ == "__main__":
    unittest.main()
