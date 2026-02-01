# PROOF: [L3/テスト] <- mekhane/fep/tests/ 対象モジュールが存在→検証が必要
"""
Tests for O4 Energeia Executor module

テスト項目:
1. ExecutionContext の正常動作
2. EnergеiaExecutor の各フェーズ
3. K3 Telos 統合
4. P4 Tekhnē 統合
5. full_cycle 一括実行
"""

import pytest
from datetime import datetime
from mekhane.fep.energeia_executor import (
    ExecutionPhase,
    ExecutionStatus,
    ExecutionContext,
    ExecutionResult,
    EnergеiaExecutor,
    format_execution_markdown,
    encode_execution_observation,
)
from mekhane.fep.telos_checker import AlignmentStatus
from mekhane.fep.tekhne_registry import (
    TekhnēRegistry,
    Technique,
    ActionCategory,
    TechniqueQuadrant,
)


class TestExecutionPhase:
    """ExecutionPhase enum tests"""

    def test_all_phases_exist(self):
        assert ExecutionPhase.INIT.value == "init"
        assert ExecutionPhase.EXECUTE.value == "execute"
        assert ExecutionPhase.VERIFY.value == "verify"
        assert ExecutionPhase.DEVIATION.value == "deviation"
        assert ExecutionPhase.CONFIRM.value == "confirm"
        assert ExecutionPhase.ROLLBACK.value == "rollback"


class TestExecutionStatus:
    """ExecutionStatus enum tests"""

    def test_all_statuses_exist(self):
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.ABORTED.value == "aborted"


class TestExecutionContext:
    """ExecutionContext dataclass tests"""

    def test_create_context(self):
        ctx = ExecutionContext(
            goal="テスト目標",
            plan="テスト計画",
            technique=None,
            phase=ExecutionPhase.INIT,
            status=ExecutionStatus.PENDING,
        )
        assert ctx.goal == "テスト目標"
        assert ctx.phase == ExecutionPhase.INIT
        assert ctx.errors == []

    def test_to_dict(self):
        ctx = ExecutionContext(
            goal="goal",
            plan="plan",
            technique=None,
            phase=ExecutionPhase.EXECUTE,
            status=ExecutionStatus.RUNNING,
        )
        d = ctx.to_dict()
        assert d["goal"] == "goal"
        assert d["phase"] == "execute"
        assert d["status"] == "running"


class TestEnergеiaExecutor:
    """EnergеiaExecutor class tests"""

    def test_initiate_creates_context(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(
            goal="テスト機能を実装する", plan="test_feature.py を作成する"
        )
        assert ctx.goal == "テスト機能を実装する"
        assert ctx.phase == ExecutionPhase.INIT
        assert ctx.status == ExecutionStatus.PENDING
        assert ctx.telos_result is not None

    def test_initiate_checks_telos_alignment(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="認証機能を実装する", plan="auth.py を作成する")
        # Should have telos result
        assert ctx.telos_result is not None
        assert ctx.telos_result.is_aligned

    def test_initiate_with_explicit_technique(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(
            goal="認識処理を実行", plan="analyze_data() を呼ぶ", technique_id="noe"
        )
        assert ctx.technique is not None
        assert ctx.technique.id == "noe"

    def test_execute_runs_action(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト計画")

        executed = False

        def action():
            nonlocal executed
            executed = True
            return "result"

        ctx = executor.execute(ctx, action)
        assert executed
        assert ctx.phase == ExecutionPhase.EXECUTE
        assert ctx.status == ExecutionStatus.RUNNING
        assert ctx.started_at is not None

    def test_execute_handles_exception(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト計画")

        def failing_action():
            raise ValueError("Action failed")

        with pytest.raises(ValueError):
            executor.execute(ctx, failing_action)

        assert len(ctx.errors) == 1
        assert "Action failed" in ctx.errors[0]

    def test_verify_all_pass(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト計画")

        verify_fns = [
            lambda: True,
            lambda: True,
        ]

        ctx = executor.verify(ctx, verify_fns)
        assert ctx.phase == ExecutionPhase.VERIFY
        assert ctx.checkpoints["phase_2"]["all_passed"] is True

    def test_verify_with_failure(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト計画")

        verify_fns = [
            lambda: True,
            lambda: False,  # This fails
        ]

        ctx = executor.verify(ctx, verify_fns)
        assert ctx.checkpoints["phase_2"]["all_passed"] is False

    def test_check_deviation_no_deviation(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト計画")
        ctx.artifacts = ["file1.py", "file2.py"]

        ctx = executor.check_deviation(ctx, expected_artifacts=["file1.py", "file2.py"])
        assert ctx.phase == ExecutionPhase.DEVIATION
        assert ctx.checkpoints["phase_3"]["has_deviation"] is False

    def test_check_deviation_missing_artifact(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト計画")
        ctx.artifacts = ["file1.py"]

        ctx = executor.check_deviation(ctx, expected_artifacts=["file1.py", "file2.py"])
        assert ctx.checkpoints["phase_3"]["has_deviation"] is True

    def test_confirm_completes(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="認証機能を実装", plan="auth.py 作成")
        ctx.started_at = datetime.now()

        result = executor.confirm(ctx, commit_prefix="feat")
        assert result.success is True
        assert result.context.status == ExecutionStatus.COMPLETED
        assert result.commit_message is not None
        assert "feat" in result.commit_message

    def test_abort_creates_failed_result(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト計画")

        result = executor.abort(ctx, "ユーザーによる中断")
        assert result.success is False
        assert result.context.status == ExecutionStatus.ABORTED
        assert "ユーザーによる中断" in result.context.errors[0]

    def test_full_cycle_success(self):
        executor = EnergеiaExecutor()

        result = executor.full_cycle(
            goal="テスト機能",
            plan="test.py を作成",
            action_fn=lambda: "output",
            verify_fns=[lambda: True],
        )

        assert result.success is True
        assert result.context.status == ExecutionStatus.COMPLETED


class TestFormatExecutionMarkdown:
    """format_execution_markdown tests"""

    def test_formats_successful_result(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト目的", plan="テスト計画")
        ctx = executor.execute(ctx, lambda: None)
        result = executor.confirm(ctx)

        markdown = format_execution_markdown(result)
        assert "O4 Energeia" in markdown
        assert "PHASE 0" in markdown
        assert "PHASE 1" in markdown


class TestEncodeExecutionObservation:
    """encode_execution_observation tests"""

    def test_encodes_successful_result(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト")
        result = executor.confirm(ctx)

        obs = encode_execution_observation(result)
        assert obs["context_clarity"] == 0.9  # success
        assert obs["urgency"] == 0.0  # no errors

    def test_encodes_failed_result(self):
        executor = EnergеiaExecutor()
        ctx = executor.initiate(goal="テスト", plan="テスト")
        result = executor.abort(ctx, "エラー")

        obs = encode_execution_observation(result)
        assert obs["context_clarity"] == 0.3  # failure
        assert obs["urgency"] == 0.3  # 1 error
