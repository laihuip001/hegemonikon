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


# PURPOSE: UML ステージの設定が正しい。
class TestUMLStageConfig:
    """UML ステージの設定が正しい。"""

    # PURPOSE: five_stages_defined をテストする
    def test_five_stages_defined(self):
        """Verify five stages defined behavior."""
        assert len(UMLStage) == 5

    # PURPOSE: all_stages_have_theorems をテストする
    def test_all_stages_have_theorems(self):
        """Verify all stages have theorems behavior."""
        for stage in UMLStage:
            assert stage in STAGE_TO_THEOREM

    # PURPOSE: all_stages_have_questions をテストする
    def test_all_stages_have_questions(self):
        """Verify all stages have questions behavior."""
        for stage in UMLStage:
            assert stage in STAGE_QUESTIONS
            assert len(STAGE_QUESTIONS[stage]) > 10

    # PURPOSE: all_stages_have_cognitive_types をテストする
    def test_all_stages_have_cognitive_types(self):
        """Verify all stages have cognitive types behavior."""
        for stage in UMLStage:
            assert stage in STAGE_TO_COGNITIVE

    # PURPOSE: η₁-η₅ の射がステージにマッピングされている。
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


# PURPOSE: Pre-check Stage 1: O1 理解確認。
class TestCheckUnderstanding:
    """Pre-check Stage 1: O1 理解確認。"""

    # PURPOSE: sufficient_input_passes をテストする
    def test_sufficient_input_passes(self):
        """Verify sufficient input passes behavior."""
        result = check_understanding("これは十分な長さの入力テキストです。理解が可能。")
        assert result.passed
        assert result.theorem == "O1"

    # PURPOSE: empty_input_fails をテストする
    def test_empty_input_fails(self):
        """Verify empty input fails behavior."""
        result = check_understanding("")
        assert not result.passed

    # PURPOSE: short_input_fails をテストする
    def test_short_input_fails(self):
        """Verify short input fails behavior."""
        result = check_understanding("短い")
        assert not result.passed

    # PURPOSE: cognitive_type_is_understanding をテストする
    def test_cognitive_type_is_understanding(self):
        """Verify cognitive type is understanding behavior."""
        result = check_understanding("十分な長さの入力テキスト。理解確認。")
        assert result.cognitive_type == CognitiveType.UNDERSTANDING.value


# PURPOSE: Pre-check Stage 2: A1 直感確認。
class TestCheckIntuition:
    """Pre-check Stage 2: A1 直感確認。"""

    # PURPOSE: 十分な長さの入力 → 直感形成可能。
    def test_sufficient_input_passes(self):
        """十分な長さの入力 → 直感形成可能。"""
        result = check_intuition("これは十分な長さの入力テキストです")
        assert result.passed

    # PURPOSE: 短すぎる入力 → 直感形成不可 (/m dia+ P1)
    def test_short_input_fails(self):
        """短すぎる入力 → 直感形成不可 (/m dia+ P1)."""
        result = check_intuition("短い")
        assert not result.passed
        assert "短すぎ" in result.result

    # PURPOSE: 緊急+熟考の矛盾 → fail (/m dia+ P1)
    def test_contradictory_signals_fail(self):
        """緊急+熟考の矛盾 → fail (/m dia+ P1)."""
        result = check_intuition("緊急だけどじっくり考えたい")
        assert not result.passed
        assert "矛盾" in result.result

    # PURPOSE: detects_question をテストする
    def test_detects_question(self):
        """Verify detects question behavior."""
        result = check_intuition("これはどうすればいい？")
        assert "問い" in result.result

    # PURPOSE: detects_uncertainty をテストする
    def test_detects_uncertainty(self):
        """Verify detects uncertainty behavior."""
        result = check_intuition("これはわからない点がある")
        assert "不確実" in result.result

    # PURPOSE: detects_urgency をテストする
    def test_detects_urgency(self):
        """Verify detects urgency behavior."""
        result = check_intuition("緊急でこの問題を解決してほしい")
        assert "即応" in result.result

    # PURPOSE: cognitive_type_is_bridge をテストする
    def test_cognitive_type_is_bridge(self):
        """Verify cognitive type is bridge behavior."""
        result = check_intuition("これは十分な長さの入力テキストです")
        assert result.cognitive_type == CognitiveType.BRIDGE_U_TO_R.value


# =============================================================================
# Post-checks
# =============================================================================


# PURPOSE: Post-check Stage 3: A2 批判的再評価。
class TestCheckEvaluation:
    """Post-check Stage 3: A2 批判的再評価。"""

    # PURPOSE: good_output_passes をテストする
    def test_good_output_passes(self):
        """Verify good output passes behavior."""
        result = check_evaluation(
            output="これは十分に長い出力テキストであり、文脈と関連がある。",
            context="入力テキストの文脈情報。関連する内容。",
            confidence=70.0,
        )
        assert result.passed

    # PURPOSE: empty_output_fails をテストする
    def test_empty_output_fails(self):
        """Verify empty output fails behavior."""
        result = check_evaluation(output="", context="context", confidence=50.0)
        assert not result.passed

    # PURPOSE: overconfidence_detected をテストする
    def test_overconfidence_detected(self):
        """Verify overconfidence detected behavior."""
        result = check_evaluation(
            output="十分な出力テキスト。これは正確です。",
            context="入力",
            confidence=95.0,
        )
        assert not result.passed
        assert "過信" in result.result or "FP" in result.result

    # PURPOSE: moderate_confidence_passes をテストする
    def test_moderate_confidence_passes(self):
        """Verify moderate confidence passes behavior."""
        result = check_evaluation(
            output="これは十分に長い出力テキストです。内容も適切。",
            context="入力テキストの文脈情報。",
            confidence=75.0,
        )
        assert result.passed


# PURPOSE: Post-check Stage 4: O4 決定確認。
class TestCheckDecision:
    """Post-check Stage 4: O4 決定確認。"""

    # PURPOSE: valid_output_passes をテストする
    def test_valid_output_passes(self):
        """Verify valid output passes behavior."""
        result = check_decision("これは有効な決定結果です。十分な内容がある。")
        assert result.passed

    # PURPOSE: empty_output_fails をテストする
    def test_empty_output_fails(self):
        """Verify empty output fails behavior."""
        result = check_decision("")
        assert not result.passed

    # PURPOSE: template_detected をテストする
    def test_template_detected(self):
        """Verify template detected behavior."""
        result = check_decision("TODO: ここに決定を記入する。残りの部分を完成させよ。")
        assert not result.passed
        assert "テンプレート" in result.result

    # PURPOSE: fixme_detected をテストする
    def test_fixme_detected(self):
        """Verify fixme detected behavior."""
        result = check_decision("FIXME: この部分は修正が必要。しかし進める。")
        assert not result.passed


# PURPOSE: Post-check Stage 5: A4 確信度。
class TestCheckConfidence:
    """Post-check Stage 5: A4 確信度。"""

    # PURPOSE: reasonable_confidence_passes をテストする
    def test_reasonable_confidence_passes(self):
        """Verify reasonable confidence passes behavior."""
        result = check_confidence(confidence=75.0, output="出力テキスト")
        assert result.passed

    # PURPOSE: zero_confidence_fails をテストする
    def test_zero_confidence_fails(self):
        """Verify zero confidence fails behavior."""
        result = check_confidence(confidence=0.0, output="出力")
        assert not result.passed
        assert "未設定" in result.result

    # PURPOSE: overconfidence_fails をテストする
    def test_overconfidence_fails(self):
        """Verify overconfidence fails behavior."""
        result = check_confidence(confidence=95.0, output="出力テキスト")
        assert not result.passed
        assert "過信" in result.result

    # PURPOSE: extreme_underconfidence_fails をテストする
    def test_extreme_underconfidence_fails(self):
        """Verify extreme underconfidence fails behavior."""
        result = check_confidence(confidence=5.0, output="出力")
        assert not result.passed
        assert "極端" in result.result

    # PURPOSE: bc6_label_detected をテストする
    def test_bc6_label_detected(self):
        """Verify bc6 label detected behavior."""
        result = check_confidence(
            confidence=75.0,
            output="[確信] これは正しい結果です。",
        )
        assert result.passed
        assert "BC-6" in result.result


# =============================================================================
# Orchestrators
# =============================================================================


# PURPOSE: run_pre_checks() が2つのチェックを返す。
class TestRunPreChecks:
    """run_pre_checks() が2つのチェックを返す。"""

    # PURPOSE: returns_two_checks をテストする
    def test_returns_two_checks(self):
        """Verify returns two checks behavior."""
        checks = run_pre_checks("十分な長さの入力テキスト。理解可能。")
        assert len(checks) == 2

    # PURPOSE: first_is_understanding をテストする
    def test_first_is_understanding(self):
        """Verify first is understanding behavior."""
        checks = run_pre_checks("十分な長さの入力テキスト。理解可能。")
        assert checks[0].stage == UMLStage.PRE_UNDERSTANDING

    # PURPOSE: second_is_intuition をテストする
    def test_second_is_intuition(self):
        """Verify second is intuition behavior."""
        checks = run_pre_checks("十分な長さの入力テキスト。理解可能。")
        assert checks[1].stage == UMLStage.PRE_INTUITION


# PURPOSE: run_post_checks() が3つのチェックを返す。
class TestRunPostChecks:
    """run_post_checks() が3つのチェックを返す。"""

    # PURPOSE: returns_three_checks をテストする
    def test_returns_three_checks(self):
        """Verify returns three checks behavior."""
        checks = run_post_checks("十分な出力テキスト", "入力", 75.0)
        assert len(checks) == 3

    # PURPOSE: stages_in_order をテストする
    def test_stages_in_order(self):
        """Verify stages in order behavior."""
        checks = run_post_checks("十分な出力テキスト", "入力", 75.0)
        assert checks[0].stage == UMLStage.POST_EVALUATION
        assert checks[1].stage == UMLStage.POST_DECISION
        assert checks[2].stage == UMLStage.POST_CONFIDENCE


# =============================================================================
# Full UML
# =============================================================================


# PURPOSE: run_full_uml() — 5段階一括実行。
class TestRunFullUML:
    """run_full_uml() — 5段階一括実行。"""

    # PURPOSE: returns_uml_report をテストする
    def test_returns_uml_report(self):
        """Verify returns uml report behavior."""
        report = run_full_uml(
            context="これは理解可能な入力テキストです。",
            output="これは有効な出力テキストです。十分な内容。",
            wf_name="test",
            confidence=75.0,
        )
        assert isinstance(report, UMLReport)

    # PURPOSE: five_total_checks をテストする
    def test_five_total_checks(self):
        """Verify five total checks behavior."""
        report = run_full_uml(
            context="入力テキスト。十分な長さ。",
            output="出力テキスト。十分な長さ。",
            wf_name="test",
            confidence=75.0,
        )
        assert report.total_count == 5

    # PURPOSE: all_pass_for_good_input をテストする
    def test_all_pass_for_good_input(self):
        """Verify all pass for good input behavior."""
        report = run_full_uml(
            context="これは十分に長い入力テキストです。理解可能。",
            output="これは十分に長い出力テキストです。有効な決定。",
            wf_name="test",
            confidence=75.0,
        )
        assert report.overall_pass

    # PURPOSE: AMP フィードバック: 過信時に Stage 3 → Stage 1 ループ。
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

    # PURPOSE: no_feedback_for_normal_confidence をテストする
    def test_no_feedback_for_normal_confidence(self):
        """Verify no feedback for normal confidence behavior."""
        report = run_full_uml(
            context="入力テキスト。理解可能。十分。",
            output="出力テキスト。有効な決定。十分。",
            wf_name="test",
            confidence=75.0,
        )
        assert not report.feedback_loop_triggered

    # PURPOSE: summary_format をテストする
    def test_summary_format(self):
        """Verify summary format behavior."""
        report = run_full_uml(
            context="入力テキスト。理解可能な文章。",
            output="出力テキスト。十分な内容。",
            wf_name="noe",
            confidence=75.0,
        )
        assert "UML [noe]" in report.summary
        assert "/" in report.summary  # "N/5"

    # PURPOSE: describe_format をテストする
    def test_describe_format(self):
        """Verify describe format behavior."""
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

    # PURPOSE: wf_name_preserved をテストする
    def test_wf_name_preserved(self):
        """Verify wf name preserved behavior."""
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


# PURPOSE: 定数が適切に設定されている。
class TestConstants:
    """定数が適切に設定されている。"""

    # PURPOSE: false_positive_rate をテストする
    def test_false_positive_rate(self):
        """Verify false positive rate behavior."""
        assert MP_FALSE_POSITIVE_RATE == 0.325

    # PURPOSE: overconfidence_threshold をテストする
    def test_overconfidence_threshold(self):
        """Verify overconfidence threshold behavior."""
        assert OVERCONFIDENCE_THRESHOLD == 90.0

    # PURPOSE: max_feedback_loops をテストする
    def test_max_feedback_loops(self):
        """Verify max feedback loops behavior."""
        assert MAX_FEEDBACK_LOOPS == 3
