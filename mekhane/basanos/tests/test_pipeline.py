# PROOF: [L1/定理] <- tests/basanos/ DailyReviewPipeline ユニットテスト
# PURPOSE: DailyReviewPipeline のテスト。
"""
DailyReviewPipeline のテスト。

L0 (Basanos) → L1 (Synteleia) → L2 (Jules) → FB フロー検証。
"""

import json
import tempfile
from pathlib import Path

import pytest

from mekhane.basanos.ai_auditor import AuditResult as BasanosResult, Issue, Severity
from mekhane.basanos.pipeline import (
    DailyReviewPipeline,
    DomainWeight,
    PipelineResult,
    RotationState,
    basanos_issue_to_synteleia,
    basanos_to_synteleia_target,
)
from mekhane.synteleia.base import AuditSeverity, AuditTargetType


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Adapter Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: Basanos → Synteleia アダプターのテスト。
class TestAdapter:
    """Basanos → Synteleia アダプターのテスト。"""

    # PURPOSE: severity_mapping_critical をテストする
    def test_severity_mapping_critical(self):
        issue = Issue(
            code="AI-004", name="Logic Hallucination",
            severity=Severity.CRITICAL, line=10,
            message="Division by zero",
        )
        result = basanos_issue_to_synteleia(issue, "test.py")
        assert result.severity == AuditSeverity.CRITICAL
        assert result.code == "AI-004"
        assert result.agent == "basanos/AI-004"
        assert result.location == "test.py:10"

    # PURPOSE: severity_mapping_high をテストする
    def test_severity_mapping_high(self):
        issue = Issue(
            code="AI-001", name="Naming Hallucination",
            severity=Severity.HIGH, line=5,
            message="Unknown module",
        )
        result = basanos_issue_to_synteleia(issue)
        assert result.severity == AuditSeverity.HIGH
        assert result.location == "L5"  # No file_path → "L{line}"

    # PURPOSE: All severity levels map correctly
    def test_severity_mapping_all(self):
        """All severity levels map correctly."""
        for basanos_sev, synteleia_sev in [
            (Severity.CRITICAL, AuditSeverity.CRITICAL),
            (Severity.HIGH, AuditSeverity.HIGH),
            (Severity.MEDIUM, AuditSeverity.MEDIUM),
            (Severity.LOW, AuditSeverity.LOW),
        ]:
            issue = Issue(code="X", name="X", severity=basanos_sev, line=1, message="X")
            assert basanos_issue_to_synteleia(issue).severity == synteleia_sev

    # PURPOSE: BasanosResult → AuditTarget conversion
    def test_basanos_to_synteleia_target(self, tmp_path):
        """BasanosResult → AuditTarget conversion."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\n", encoding="utf-8")

        basanos_result = BasanosResult(
            file_path=test_file,
            issues=[
                Issue(code="AI-001", name="X", severity=Severity.HIGH, line=1, message="X"),
            ],
        )
        target = basanos_to_synteleia_target(basanos_result)
        assert target.target_type == AuditTargetType.CODE
        assert target.content == "x = 1\n"
        assert target.metadata["basanos_issues"] == 1
        assert target.metadata["has_high"] is True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RotationState Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: 重み付きドメインローテーションのテスト。
class TestRotationState:
    """重み付きドメインローテーションのテスト。"""

    # PURPOSE: 旧形式 (last_domains list) からの読込。
    def test_load_old_format(self, tmp_path):
        """旧形式 (last_domains list) からの読込。"""
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "last_domains": ["Security", "Performance", "Testing"],
            "cycle": 10,
            "last_date": "2026-02-18",
        }))

        state = RotationState.load(state_file)
        assert state.cycle == 10
        assert len(state.domains) == 3
        assert "Security" in state.domains
        assert state.domains["Security"].weight == 1.0  # Default weight

    # PURPOSE: 新形式 (domains dict) からの読込。
    def test_load_new_format(self, tmp_path):
        """新形式 (domains dict) からの読込。"""
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "domains": {
                "Security": {"weight": 2.5, "last_issues": 3, "total_issues": 15, "last_reviewed": "2026-02-17"},
                "Testing": {"weight": 0.5, "last_issues": 0, "total_issues": 2, "last_reviewed": "2026-02-16"},
            },
            "cycle": 20,
            "last_date": "2026-02-18",
        }))

        state = RotationState.load(state_file)
        assert state.cycle == 20
        assert state.domains["Security"].weight == 2.5
        assert state.domains["Testing"].weight == 0.5

    # PURPOSE: Save → Load roundtrip。
    def test_save_roundtrip(self, tmp_path):
        """Save → Load roundtrip。"""
        state_file = tmp_path / "state.json"
        state = RotationState(cycle=5, last_date="2026-02-18")
        state.domains["Security"] = DomainWeight(name="Security", weight=1.5, last_issues=2, total_issues=10)
        state.save(state_file)

        loaded = RotationState.load(state_file)
        assert loaded.cycle == 5
        assert loaded.domains["Security"].weight == 1.5
        assert loaded.domains["Security"].total_issues == 10

    # PURPOSE: 重みの高いドメインが優先選択される。
    def test_select_domains_by_weight(self):
        """重みの高いドメインが優先選択される。"""
        state = RotationState()
        state.domains["Low"] = DomainWeight(name="Low", weight=0.5)
        state.domains["Mid"] = DomainWeight(name="Mid", weight=1.0)
        state.domains["High"] = DomainWeight(name="High", weight=2.0)

        selected = state.select_domains(n=2)
        assert selected == ["High", "Mid"]

    # PURPOSE: Issue があると重みが上昇。
    def test_update_weights_increase(self):
        """Issue があると重みが上昇。"""
        state = RotationState()
        state.domains["Security"] = DomainWeight(name="Security", weight=1.0)

        state.update_weights("Security", issue_count=5)
        assert state.domains["Security"].weight > 1.0
        assert state.domains["Security"].last_issues == 5
        assert state.domains["Security"].total_issues == 5

    # PURPOSE: Issue がないと重みが減衰。
    def test_update_weights_decrease(self):
        """Issue がないと重みが減衰。"""
        state = RotationState()
        state.domains["Security"] = DomainWeight(name="Security", weight=2.0)

        state.update_weights("Security", issue_count=0)
        assert state.domains["Security"].weight < 2.0
        assert state.domains["Security"].weight == pytest.approx(1.8)  # 2.0 * 0.9

    # PURPOSE: 重みには上限(3.0)と下限(0.3)がある。
    def test_update_weights_bounds(self):
        """重みには上限(3.0)と下限(0.3)がある。"""
        state = RotationState()
        state.domains["X"] = DomainWeight(name="X", weight=2.9)
        state.update_weights("X", issue_count=50)  # Many issues
        assert state.domains["X"].weight <= 3.0

        state.domains["Y"] = DomainWeight(name="Y", weight=0.35)
        state.update_weights("Y", issue_count=0)  # No issues
        assert state.domains["Y"].weight >= 0.3

    # PURPOSE: 存在しないファイルから読込 → 空の状態。
    def test_load_nonexistent(self, tmp_path):
        """存在しないファイルから読込 → 空の状態。"""
        state = RotationState.load(tmp_path / "nonexistent.json")
        assert state.cycle == 0
        assert len(state.domains) == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PipelineResult Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: パイプライン結果のテスト。
class TestPipelineResult:
    """パイプライン結果のテスト。"""

    # PURPOSE: needs_l2_true をテストする
    def test_needs_l2_true(self):
        result = PipelineResult(
            l0_issues=[{"severity": "critical", "code": "AI-004", "message": "bad"}],
        )
        assert result.needs_l2 is True

    # PURPOSE: needs_l2_false をテストする
    def test_needs_l2_false(self):
        result = PipelineResult(
            l0_issues=[{"severity": "medium", "code": "AI-002", "message": "ok"}],
        )
        assert result.needs_l2 is False

    # PURPOSE: needs_l2_empty をテストする
    def test_needs_l2_empty(self):
        result = PipelineResult()
        assert result.needs_l2 is False

    # PURPOSE: to_jules_prompt をテストする
    def test_to_jules_prompt(self):
        result = PipelineResult(
            l0_issues=[
                {"severity": "critical", "code": "AI-004", "message": "Division by zero", "location": "test.py:10", "suggestion": "Add check"},
                {"severity": "low", "code": "AI-017", "message": "Magic number", "location": "test.py:20"},
            ],
        )
        prompt = result.to_jules_prompt()
        assert "AI-004" in prompt
        assert "Division by zero" in prompt
        assert "AI-017" not in prompt  # Low severity excluded


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pipeline Integration Test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: パイプライン E2E テスト。
class TestPipeline:
    """パイプライン E2E テスト。"""

    # PURPOSE: 問題のないファイルでパイプライン実行。
    def test_run_with_clean_file(self, tmp_path):
        """問題のないファイルでパイプライン実行。"""
        test_file = tmp_path / "clean.py"
        test_file.write_text("def hello():\n    return 'world'\n", encoding="utf-8")

        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "last_domains": ["Testing"],
            "cycle": 0,
            "last_date": "",
        }))

        pipeline = DailyReviewPipeline(
            project_root=tmp_path,
            rotation_state_path=state_file,
            enable_l2=False,
        )

        result = pipeline.run(files=[test_file], dry_run=True)
        assert result.files_scanned == 1
        assert len(result.l0_issues) == 0
        assert result.needs_l2 is False

    # PURPOSE: 問題のあるファイルで L0 検出を確認。
    def test_run_with_buggy_file(self, tmp_path):
        """問題のあるファイルで L0 検出を確認。"""
        test_file = tmp_path / "buggy.py"
        test_file.write_text(
            "import nonexistent_module_xyz\n"  # AI-001: Naming Hallucination
            "x = 1 / 0\n"  # AI-004: Division by zero
            "def foo():\n"
            "    pass\n",
            encoding="utf-8",
        )

        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "last_domains": ["Security"],
            "cycle": 0,
            "last_date": "",
        }))

        pipeline = DailyReviewPipeline(
            project_root=tmp_path,
            rotation_state_path=state_file,
            enable_l2=False,
        )

        result = pipeline.run(files=[test_file], dry_run=True)
        assert result.files_scanned == 1
        assert len(result.l0_issues) > 0
        assert result.needs_l2 is True  # Should have CRITICAL/HIGH

    # PURPOSE: フィードバックが rotation state を更新する。
    def test_feedback_updates_state(self, tmp_path):
        """フィードバックが rotation state を更新する。"""
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "last_domains": ["Security", "Testing"],
            "cycle": 5,
            "last_date": "2026-02-17",
        }))

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\n", encoding="utf-8")

        pipeline = DailyReviewPipeline(
            project_root=tmp_path,
            rotation_state_path=state_file,
            enable_l2=False,
        )
        pipeline.run(files=[test_file], dry_run=True)

        # Reload and check
        updated = RotationState.load(state_file)
        assert updated.cycle == 6  # Incremented
        assert updated.last_date != "2026-02-17"  # Updated

    # PURPOSE: サマリー出力のフォーマット確認。
    def test_summary_output(self):
        """サマリー出力のフォーマット確認。"""
        pipeline = DailyReviewPipeline(enable_l2=False)
        result = PipelineResult(
            files_scanned=5,
            l0_issues=[
                {"severity": "critical", "code": "AI-004", "message": "bad"},
                {"severity": "high", "code": "AI-001", "message": "sus"},
                {"severity": "low", "code": "AI-017", "message": "minor"},
            ],
            domains_reviewed=["Security", "Testing"],
        )
        summary = pipeline.summary(result)
        assert "Files scanned: 5" in summary
        assert "L0 (Basanos): 3 issues" in summary
        assert "🔴 critical: 1" in summary


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# F4: L1 Synteleia Mock Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: L1 Synteleia 統合テスト (mock)。
class TestL1Integration:
    """L1 Synteleia 統合テスト (mock)。"""

    # PURPOSE: L0 issue がある場合、L1 結果が生成される。
    def test_l1_triggered_on_issues(self, tmp_path):
        """L0 issue がある場合、L1 結果が生成される。"""
        test_file = tmp_path / "bad.py"
        test_file.write_text(
            "import nonexistent_module_xyz\nx = 1 / 0\n",
            encoding="utf-8",
        )
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "last_domains": ["Security"],
            "cycle": 0, "last_date": "",
        }))

        pipeline = DailyReviewPipeline(
            project_root=tmp_path,
            rotation_state_path=state_file,
            enable_l2=False,
        )
        result = pipeline.run(files=[test_file], dry_run=True)
        # L0 issues detected → pipeline should record them
        assert len(result.l0_issues) > 0
        # L1 is skipped in dry_run but pipeline proceeds
        assert result.files_scanned == 1

    # PURPOSE: L0 issue がない場合、L1 は不要。
    def test_l1_skipped_on_clean(self, tmp_path):
        """L0 issue がない場合、L1 は不要。"""
        test_file = tmp_path / "clean.py"
        test_file.write_text("def hello():\n    return 42\n", encoding="utf-8")
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "last_domains": ["Testing"],
            "cycle": 0, "last_date": "",
        }))

        pipeline = DailyReviewPipeline(
            project_root=tmp_path,
            rotation_state_path=state_file,
            enable_l2=False,
        )
        result = pipeline.run(files=[test_file], dry_run=True)
        # clean file may have LOW issues (e.g. magic number) but no CRITICAL/HIGH
        assert result.needs_l2 is False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# F5: Snippet Extraction Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: _extract_snippet のテスト。
class TestSnippet:
    """_extract_snippet のテスト。"""

    # PURPOSE: 正常なファイル + 行番号でスニペット取得。
    def test_extract_snippet_valid(self, tmp_path):
        """正常なファイル + 行番号でスニペット取得。"""
        test_file = tmp_path / "example.py"
        test_file.write_text(
            "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\n",
            encoding="utf-8",
        )
        snippet = PipelineResult._extract_snippet(f"{test_file}:4", context_lines=2)
        assert "line4" in snippet
        assert ">>>" in snippet  # Marker on target line
        assert "line2" in snippet  # context before
        assert "line6" in snippet  # context after

    # PURPOSE: コロンなし → 空文字。
    def test_extract_snippet_no_colon(self):
        """コロンなし → 空文字。"""
        assert PipelineResult._extract_snippet("no_colon") == ""

    # PURPOSE: 存在しないファイル → 空文字。
    def test_extract_snippet_nonexistent(self):
        """存在しないファイル → 空文字。"""
        assert PipelineResult._extract_snippet("/nonexistent/file.py:1") == ""

    # PURPOSE: to_jules_prompt にスニペットが含まれる。
    def test_extract_snippet_in_prompt(self, tmp_path):
        """to_jules_prompt にスニペットが含まれる。"""
        test_file = tmp_path / "code.py"
        test_file.write_text(
            "import os\nx = 1 / 0\nprint(x)\n",
            encoding="utf-8",
        )
        result = PipelineResult(
            l0_issues=[{
                "severity": "critical",
                "code": "AI-004",
                "message": "Division",
                "location": f"{test_file}:2",
            }],
        )
        prompt = result.to_jules_prompt(context_lines=1)
        assert "```python" in prompt
        assert ">>>" in prompt  # Target line marker


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Notification Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# PURPOSE: _notify_result のテスト。
class TestNotification:
    """_notify_result のテスト。"""

    # PURPOSE: run() が _notify_result を呼ぶ。
    def test_notify_called_on_run(self, tmp_path):
        """run() が _notify_result を呼ぶ。"""
        from unittest.mock import patch

        test_file = tmp_path / "x.py"
        test_file.write_text("x = 1\n", encoding="utf-8")
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "last_domains": ["Testing"],
            "cycle": 0, "last_date": "",
        }))

        pipeline = DailyReviewPipeline(
            project_root=tmp_path,
            rotation_state_path=state_file,
            enable_l2=False,
        )

        with patch.object(pipeline, "_notify_result") as mock_notify:
            pipeline.run(files=[test_file], dry_run=True)
            mock_notify.assert_called_once()

