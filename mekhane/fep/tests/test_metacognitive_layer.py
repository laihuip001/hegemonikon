#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → UML (Universal Metacognitive Layer) の正確性を検証する必要がある
   → 5段階チェック + AMP フィードバックループ
   → test_metacognitive_layer.py が担う

Q.E.D.
"""

import pytest

from mekhane.fep.metacognitive_layer import (
    MAX_FEEDBACK_LOOPS,
    MP_FALSE_POSITIVE_RATE,
    OVERCONFIDENCE_THRESHOLD,
    STAGE_QUESTIONS,
    STAGE_TO_COGNITIVE,
    STAGE_TO_THEOREM,
    MetacognitiveCheck,
    UMLReport,
    UMLStage,
    check_confidence,
    check_decision,
    check_evaluation,
    check_intuition,
    check_understanding,
    run_full_uml,
    run_post_checks,
    run_pre_checks,
)
from mekhane.fep.category import CognitiveType


# =============================================================================
# Stage Configuration
# =============================================================================


class TestUMLStageConfig:
    """UML ステージの設定が正しい。"""

    def test_five_stages_defined(self):
        assert len(UMLStage) == 5

    def test_all_stages_have_theorems(self):
        for stage in UMLStage:
            assert stage in STAGE_TO_THEOREM

    def test_all_stages_have_questions(self):
        for stage in UMLStage:
            assert stage in STAGE_QUESTIONS
            assert len(STAGE_QUESTIONS[stage]) > 10

    def test_all_stages_have_cognitive_types(self):
        for stage in UMLStage:
            assert stage in STAGE_TO_COGNITIVE

    def test_stage_theorem_mapping(self):
        """η₁-η₅ の射がステージにマッピングされている。"""
        assert STAGE_TO_THEOREM[UMLStage.PRE_UNDERSTANDING] == "O1"
        assert STAGE_TO_THEOREM[UMLStage.PRE_INTUITION] == "A1"
        assert STAGE_TO_THEOREM[UMLStage.POST_EVALUATION] == "A2"
        assert STAGE_TO_THEOREM[UMLStage.POST_DECISION] == "O4"
        assert STAGE_TO_THEOREM[UMLStage.POST_CONFIDENCE] == "A4"


# =============================================================================
# Pre-checks
# =============================================================================


class TestCheckUnderstanding:
    """Pre-check Stage 1: O1 理解確認。"""

    def test_sufficient_input_passes(self):
        result = check_understanding("これは十分な長さの入力テキストです。理解が可能。")
        assert result.passed
        assert result.theorem == "O1"

    def test_empty_input_fails(self):
        result = check_understanding("")
        assert not result.passed

    def test_short_input_fails(self):
        result = check_understanding("短い")
        assert not result.passed

    def test_cognitive_type_is_understanding(self):
        result = check_understanding("十分な長さの入力テキスト。理解確認。")
        assert result.cognitive_type == CognitiveType.UNDERSTANDING.value


class TestCheckIntuition:
    """Pre-check Stage 2: A1 直感確認。"""

    def test_always_passes(self):
        """直感は常に形成可能 — 「わからない」も直感。"""
        result = check_intuition("何でも入力")
        assert result.passed

    def test_detects_question(self):
        result = check_intuition("これはどうすればいい？")
        assert "問い" in result.result

    def test_detects_uncertainty(self):
        result = check_intuition("これはわからない点がある")
        assert "不確実" in result.result

    def test_cognitive_type_is_bridge(self):
        result = check_intuition("入力テキスト")
        assert result.cognitive_type == CognitiveType.BRIDGE_U_TO_R.value


# =============================================================================
# Post-checks
# =============================================================================


class TestCheckEvaluation:
    """Post-check Stage 3: A2 批判的再評価。"""

    def test_good_output_passes(self):
        result = check_evaluation(
            output="これは十分に長い出力テキストであり、文脈と関連がある。",
            context="入力テキストの文脈情報。関連する内容。",
            confidence=70.0,
        )
        assert result.passed

    def test_empty_output_fails(self):
        result = check_evaluation(output="", context="context", confidence=50.0)
        assert not result.passed

    def test_overconfidence_detected(self):
        result = check_evaluation(
            output="十分な出力テキスト。これは正確です。",
            context="入力",
            confidence=95.0,
        )
        assert not result.passed
        assert "過信" in result.result or "FP" in result.result

    def test_moderate_confidence_passes(self):
        result = check_evaluation(
            output="十分な出力テキスト。",
            context="入力テキスト",
            confidence=75.0,
        )
        assert result.passed


class TestCheckDecision:
    """Post-check Stage 4: O4 決定確認。"""

    def test_valid_output_passes(self):
        result = check_decision("これは有効な決定結果です。十分な内容がある。")
        assert result.passed

    def test_empty_output_fails(self):
        result = check_decision("")
        assert not result.passed

    def test_template_detected(self):
        result = check_decision("TODO: ここに決定を記入する。残りの部分を完成させよ。")
        assert not result.passed
        assert "テンプレート" in result.result

    def test_fixme_detected(self):
        result = check_decision("FIXME: この部分は修正が必要。しかし進める。")
        assert not result.passed


class TestCheckConfidence:
    """Post-check Stage 5: A4 確信度。"""

    def test_reasonable_confidence_passes(self):
        result = check_confidence(confidence=75.0, output="出力テキスト")
        assert result.passed

    def test_zero_confidence_fails(self):
        result = check_confidence(confidence=0.0, output="出力")
        assert not result.passed
        assert "未設定" in result.result

    def test_overconfidence_fails(self):
        result = check_confidence(confidence=95.0, output="出力テキスト")
        assert not result.passed
        assert "過信" in result.result

    def test_extreme_underconfidence_fails(self):
        result = check_confidence(confidence=5.0, output="出力")
        assert not result.passed
        assert "極端" in result.result

    def test_bc6_label_detected(self):
        result = check_confidence(
            confidence=75.0,
            output="[確信] これは正しい結果です。",
        )
        assert result.passed
        assert "BC-6" in result.result


# =============================================================================
# Orchestrators
# =============================================================================


class TestRunPreChecks:
    """run_pre_checks() が2つのチェックを返す。"""

    def test_returns_two_checks(self):
        checks = run_pre_checks("十分な長さの入力テキスト。理解可能。")
        assert len(checks) == 2

    def test_first_is_understanding(self):
        checks = run_pre_checks("十分な長さの入力テキスト。理解可能。")
        assert checks[0].stage == UMLStage.PRE_UNDERSTANDING

    def test_second_is_intuition(self):
        checks = run_pre_checks("十分な長さの入力テキスト。理解可能。")
        assert checks[1].stage == UMLStage.PRE_INTUITION


class TestRunPostChecks:
    """run_post_checks() が3つのチェックを返す。"""

    def test_returns_three_checks(self):
        checks = run_post_checks("十分な出力テキスト", "入力", 75.0)
        assert len(checks) == 3

    def test_stages_in_order(self):
        checks = run_post_checks("十分な出力テキスト", "入力", 75.0)
        assert checks[0].stage == UMLStage.POST_EVALUATION
        assert checks[1].stage == UMLStage.POST_DECISION
        assert checks[2].stage == UMLStage.POST_CONFIDENCE


# =============================================================================
# Full UML
# =============================================================================


class TestRunFullUML:
    """run_full_uml() — 5段階一括実行。"""

    def test_returns_uml_report(self):
        report = run_full_uml(
            context="これは理解可能な入力テキストです。",
            output="これは有効な出力テキストです。十分な内容。",
            wf_name="test",
            confidence=75.0,
        )
        assert isinstance(report, UMLReport)

    def test_five_total_checks(self):
        report = run_full_uml(
            context="入力テキスト。十分な長さ。",
            output="出力テキスト。十分な長さ。",
            wf_name="test",
            confidence=75.0,
        )
        assert report.total_count == 5

    def test_all_pass_for_good_input(self):
        report = run_full_uml(
            context="これは十分に長い入力テキストです。理解可能。",
            output="これは十分に長い出力テキストです。有効な決定。",
            wf_name="test",
            confidence=75.0,
        )
        assert report.overall_pass

    def test_feedback_loop_on_overconfidence(self):
        """AMP フィードバック: 過信時に Stage 3 → Stage 1 ループ。"""
        report = run_full_uml(
            context="入力テキスト。理解可能な内容。",
            output="出力テキスト。十分な内容がある。",
            wf_name="test",
            confidence=95.0,  # Over threshold
        )
        assert report.feedback_loop_triggered
        assert "X-AO1" in report.feedback_reason or "A2" in report.feedback_reason

    def test_no_feedback_for_normal_confidence(self):
        report = run_full_uml(
            context="入力テキスト。理解可能。十分。",
            output="出力テキスト。有効な決定。十分。",
            wf_name="test",
            confidence=75.0,
        )
        assert not report.feedback_loop_triggered

    def test_summary_format(self):
        report = run_full_uml(
            context="入力テキスト。理解可能な文章。",
            output="出力テキスト。十分な内容。",
            wf_name="noe",
            confidence=75.0,
        )
        assert "UML [noe]" in report.summary
        assert "/" in report.summary  # "N/5"

    def test_describe_format(self):
        report = run_full_uml(
            context="入力テキスト。理解可能な文章です。",
            output="出力テキスト。十分で有効な内容。",
            wf_name="dia",
            confidence=75.0,
        )
        desc = report.describe()
        assert "### UML Report" in desc
        assert "Pre-1" in desc
        assert "Post-3" in desc

    def test_wf_name_preserved(self):
        report = run_full_uml(
            context="テスト入力。十分な長さのテキスト。",
            output="テスト出力。十分な長さのテキスト。",
            wf_name="mek",
            confidence=50.0,
        )
        assert report.wf_name == "mek"


# =============================================================================
# Constants
# =============================================================================


class TestConstants:
    """定数が適切に設定されている。"""

    def test_false_positive_rate(self):
        assert MP_FALSE_POSITIVE_RATE == 0.325

    def test_overconfidence_threshold(self):
        assert OVERCONFIDENCE_THRESHOLD == 90.0

    def test_max_feedback_loops(self):
        assert MAX_FEEDBACK_LOOPS == 3
