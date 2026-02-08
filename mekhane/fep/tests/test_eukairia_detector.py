# PROOF: [L3/テスト] <- mekhane/fep/tests/ 対象モジュールが存在→検証が必要
"""
Tests for K1 Eukairia Detector module

テスト項目:
1. OpportunityWindow, OpportunityScale, OpportunityDecision enums
2. OpportunityContext の計算
3. detect_opportunity の各判定パス
4. FEP integration
"""

import pytest
from mekhane.fep.eukairia_detector import (
    OpportunityWindow,
    OpportunityScale,
    OpportunityDecision,
    OpportunityContext,
    EukairiaResult,
    detect_opportunity,
    format_eukairia_markdown,
    encode_eukairia_observation,
    _calculate_readiness,
    _calculate_window,
)


# PURPOSE: OpportunityWindow enum tests
class TestOpportunityWindow:
    """OpportunityWindow enum tests"""

    # PURPOSE: all_windows_exist をテストする
    def test_all_windows_exist(self):
        assert OpportunityWindow.WIDE.value == "wide"
        assert OpportunityWindow.NARROW.value == "narrow"
        assert OpportunityWindow.CLOSING.value == "closing"


# PURPOSE: OpportunityScale enum tests
class TestOpportunityScale:
    """OpportunityScale enum tests"""

    # PURPOSE: all_scales_exist をテストする
    def test_all_scales_exist(self):
        assert OpportunityScale.MICRO.value == "micro"
        assert OpportunityScale.MACRO.value == "macro"


# PURPOSE: OpportunityDecision enum tests
class TestOpportunityDecision:
    """OpportunityDecision enum tests"""

    # PURPOSE: all_decisions_exist をテストする
    def test_all_decisions_exist(self):
        assert OpportunityDecision.GO.value == "go"
        assert OpportunityDecision.WAIT.value == "wait"
        assert OpportunityDecision.PASS.value == "pass"


# PURPOSE: EukairiaResult dataclass tests
class TestEukairiaResult:
    """EukairiaResult dataclass tests"""

    # PURPOSE: should_act をテストする
    def test_should_act(self):
        result = EukairiaResult(
            action="test",
            window=OpportunityWindow.WIDE,
            scale=OpportunityScale.MICRO,
            decision=OpportunityDecision.GO,
            confidence=0.8,
            rationale="好機です",
            expected_return=0.7,
            expected_risk=0.2,
            opportunity_cost=0.3,
            readiness_score=0.8,
            recommendation="行動開始",
        )
        assert result.should_act is True
        assert result.should_wait is False
        assert result.net_value == pytest.approx(0.5)

    # PURPOSE: should_wait をテストする
    def test_should_wait(self):
        result = EukairiaResult(
            action="test",
            window=OpportunityWindow.NARROW,
            scale=OpportunityScale.MICRO,
            decision=OpportunityDecision.WAIT,
            confidence=0.6,
            rationale="待機",
            expected_return=0.4,
            expected_risk=0.3,
            opportunity_cost=0.4,
            readiness_score=0.5,
            recommendation="待機",
        )
        assert result.should_act is False
        assert result.should_wait is True


# PURPOSE: OpportunityContext tests
class TestOpportunityContext:
    """OpportunityContext tests"""

    # PURPOSE: default_values をテストする
    def test_default_values(self):
        ctx = OpportunityContext()
        assert ctx.environment_ready == 0.5
        assert ctx.resources_available == 0.5
        assert ctx.competition_high is False


# PURPOSE: _calculate_readiness tests
class TestCalculateReadiness:
    """_calculate_readiness tests"""

    # PURPOSE: high_readiness をテストする
    def test_high_readiness(self):
        ctx = OpportunityContext(
            environment_ready=0.9,
            resources_available=0.9,
            skills_prepared=0.9,
            timing_favorable=0.9,
        )
        readiness = _calculate_readiness(ctx)
        assert readiness > 0.8

    # PURPOSE: low_readiness をテストする
    def test_low_readiness(self):
        ctx = OpportunityContext(
            environment_ready=0.2,
            resources_available=0.2,
            skills_prepared=0.2,
            timing_favorable=0.2,
        )
        readiness = _calculate_readiness(ctx)
        assert readiness < 0.3

    # PURPOSE: competition_reduces_readiness をテストする
    def test_competition_reduces_readiness(self):
        ctx_no_comp = OpportunityContext(
            environment_ready=0.8,
            resources_available=0.8,
            skills_prepared=0.8,
            timing_favorable=0.8,
            competition_high=False,
        )
        ctx_with_comp = OpportunityContext(
            environment_ready=0.8,
            resources_available=0.8,
            skills_prepared=0.8,
            timing_favorable=0.8,
            competition_high=True,
        )
        assert _calculate_readiness(ctx_with_comp) < _calculate_readiness(ctx_no_comp)


# PURPOSE: _calculate_window tests
class TestCalculateWindow:
    """_calculate_window tests"""

    # PURPOSE: closing_window_high_pressure をテストする
    def test_closing_window_high_pressure(self):
        ctx = OpportunityContext(deadline_pressure=0.9)
        assert _calculate_window(ctx) == OpportunityWindow.CLOSING

    # PURPOSE: wide_window をテストする
    def test_wide_window(self):
        ctx = OpportunityContext(timing_favorable=0.8, deadline_pressure=0.2)
        assert _calculate_window(ctx) == OpportunityWindow.WIDE

    # PURPOSE: narrow_window をテストする
    def test_narrow_window(self):
        ctx = OpportunityContext(timing_favorable=0.4, deadline_pressure=0.5)
        assert _calculate_window(ctx) == OpportunityWindow.NARROW


# PURPOSE: detect_opportunity integration tests
class TestDetectOpportunity:
    """detect_opportunity integration tests"""

    # PURPOSE: go_decision_high_readiness をテストする
    def test_go_decision_high_readiness(self):
        ctx = OpportunityContext(
            environment_ready=0.9,
            resources_available=0.9,
            skills_prepared=0.8,
            timing_favorable=0.8,
        )
        result = detect_opportunity(
            action="新機能リリース",
            context=ctx,
            action_value=0.7,
        )
        assert result.decision == OpportunityDecision.GO
        assert result.should_act is True

    # PURPOSE: wait_decision_low_readiness をテストする
    def test_wait_decision_low_readiness(self):
        ctx = OpportunityContext(
            environment_ready=0.8,
            resources_available=0.3,  # Low resources
            skills_prepared=0.4,  # Low skills
            timing_favorable=0.7,
        )
        result = detect_opportunity(
            action="複雑なタスク",
            context=ctx,
            action_value=0.6,
        )
        # Low readiness should lead to WAIT
        assert result.decision in (OpportunityDecision.WAIT, OpportunityDecision.PASS)

    # PURPOSE: pass_decision_high_risk をテストする
    def test_pass_decision_high_risk(self):
        ctx = OpportunityContext(
            environment_ready=0.2,
            resources_available=0.2,
            skills_prepared=0.2,
            timing_favorable=0.2,
            competition_high=True,
            deadline_pressure=0.3,
        )
        result = detect_opportunity(
            action="高リスク行動",
            context=ctx,
            action_value=0.5,
        )
        # High risk, low readiness → PASS
        assert result.decision == OpportunityDecision.PASS

    # PURPOSE: go_on_closing_window をテストする
    def test_go_on_closing_window(self):
        ctx = OpportunityContext(
            environment_ready=0.6,
            resources_available=0.6,
            skills_prepared=0.6,
            timing_favorable=0.5,
            deadline_pressure=0.9,  # Closing window
        )
        result = detect_opportunity(
            action="最後のチャンス",
            context=ctx,
            action_value=0.6,
        )
        # Closing window should push toward GO if net >= 0
        assert result.window == OpportunityWindow.CLOSING

    # PURPOSE: factors_are_populated をテストする
    def test_factors_are_populated(self):
        ctx = OpportunityContext(
            environment_ready=0.9,
            resources_available=0.9,
            skills_prepared=0.9,
            timing_favorable=0.8,
        )
        result = detect_opportunity("テスト", ctx)
        assert len(result.factors) > 0

    # PURPOSE: default_context をテストする
    def test_default_context(self):
        result = detect_opportunity("デフォルト行動")
        assert result.action == "デフォルト行動"
        assert result.scale == OpportunityScale.MICRO


# PURPOSE: format_eukairia_markdown tests
class TestFormatEukairiaMarkdown:
    """format_eukairia_markdown tests"""

    # PURPOSE: format_includes_key_fields をテストする
    def test_format_includes_key_fields(self):
        ctx = OpportunityContext(
            environment_ready=0.8,
            resources_available=0.8,
            skills_prepared=0.7,
            timing_favorable=0.7,
        )
        result = detect_opportunity("テスト行動", ctx)
        markdown = format_eukairia_markdown(result)
        assert "K1 Eukairia" in markdown
        assert "テスト行動" in markdown
        assert "判定" in markdown


# PURPOSE: encode_eukairia_observation tests
class TestEncodeEukairiaObservation:
    """encode_eukairia_observation tests"""

    # PURPOSE: encode_go_decision をテストする
    def test_encode_go_decision(self):
        result = EukairiaResult(
            action="test",
            window=OpportunityWindow.WIDE,
            scale=OpportunityScale.MICRO,
            decision=OpportunityDecision.GO,
            confidence=0.8,
            rationale="",
            expected_return=0.7,
            expected_risk=0.2,
            opportunity_cost=0.3,
            readiness_score=0.85,
            recommendation="",
        )
        obs = encode_eukairia_observation(result)
        assert obs["context_clarity"] == 0.85  # readiness
        assert obs["urgency"] == 0.3  # WIDE window
        assert obs["confidence"] == 0.8

    # PURPOSE: encode_closing_window をテストする
    def test_encode_closing_window(self):
        result = EukairiaResult(
            action="test",
            window=OpportunityWindow.CLOSING,
            scale=OpportunityScale.MACRO,
            decision=OpportunityDecision.GO,
            confidence=0.7,
            rationale="",
            expected_return=0.5,
            expected_risk=0.4,
            opportunity_cost=0.8,
            readiness_score=0.6,
            recommendation="",
        )
        obs = encode_eukairia_observation(result)
        assert obs["urgency"] == 0.9  # CLOSING window
