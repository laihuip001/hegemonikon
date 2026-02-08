# PROOF: [L3/テスト] <- mekhane/fep/tests/ 対象モジュールが存在→検証が必要
"""
Tests for K2 Chronos Evaluator module

テスト項目:
1. TimeScale, CertaintyLevel, SlackLevel enums
2. 期限パース (ISO日付, 日本語, 英語)
3. 緊急度・余裕度計算
4. evaluate_time の統合テスト
"""

import pytest
from datetime import datetime, timedelta
from mekhane.fep.chronos_evaluator import (
    TimeScale,
    CertaintyLevel,
    SlackLevel,
    ChronosResult,
    evaluate_time,
    format_chronos_markdown,
    encode_chronos_observation,
    _parse_deadline,
    _calculate_urgency,
    _calculate_slack,
)


# PURPOSE: TimeScale enum tests
class TestTimeScale:
    """TimeScale enum tests"""

    # PURPOSE: all_scales_exist をテストする
    def test_all_scales_exist(self):
        assert TimeScale.IMMEDIATE.value == "immediate"
        assert TimeScale.SHORT.value == "short"
        assert TimeScale.MEDIUM.value == "medium"
        assert TimeScale.LONG.value == "long"


# PURPOSE: CertaintyLevel enum tests
class TestCertaintyLevel:
    """CertaintyLevel enum tests"""

    # PURPOSE: certainty_levels をテストする
    def test_certainty_levels(self):
        assert CertaintyLevel.CERTAIN.value == "C"
        assert CertaintyLevel.UNCERTAIN.value == "U"


# PURPOSE: SlackLevel enum tests
class TestSlackLevel:
    """SlackLevel enum tests"""

    # PURPOSE: slack_levels をテストする
    def test_slack_levels(self):
        assert SlackLevel.AMPLE.value == "ample"
        assert SlackLevel.ADEQUATE.value == "adequate"
        assert SlackLevel.TIGHT.value == "tight"
        assert SlackLevel.OVERDUE.value == "overdue"


# PURPOSE: ChronosResult dataclass tests
class TestChronosResult:
    """ChronosResult dataclass tests"""

    # PURPOSE: is_overdue をテストする
    def test_is_overdue(self):
        result = ChronosResult(
            task="test",
            deadline=None,
            deadline_str="過去",
            time_scale=TimeScale.IMMEDIATE,
            certainty=CertaintyLevel.CERTAIN,
            slack=SlackLevel.OVERDUE,
            urgency=1.0,
            estimated_hours=1.0,
            remaining_hours=0,
            recommendation="",
        )
        assert result.is_overdue is True
        assert result.needs_acceleration is True

    # PURPOSE: not_overdue をテストする
    def test_not_overdue(self):
        result = ChronosResult(
            task="test",
            deadline=None,
            deadline_str="来週",
            time_scale=TimeScale.SHORT,
            certainty=CertaintyLevel.UNCERTAIN,
            slack=SlackLevel.ADEQUATE,
            urgency=0.6,
            estimated_hours=4.0,
            remaining_hours=168,
            recommendation="",
        )
        assert result.is_overdue is False
        assert result.needs_acceleration is False


# PURPOSE: _parse_deadline tests
class TestParseDeadline:
    """_parse_deadline tests"""

    # PURPOSE: parse_iso_date をテストする
    def test_parse_iso_date(self):
        # Future date
        future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        deadline, scale, certainty = _parse_deadline(future)
        assert deadline is not None
        assert certainty == CertaintyLevel.CERTAIN

    # PURPOSE: parse_japanese_today をテストする
    def test_parse_japanese_today(self):
        deadline, scale, certainty = _parse_deadline("今日")
        assert deadline is not None
        assert scale == TimeScale.IMMEDIATE
        assert certainty == CertaintyLevel.CERTAIN

    # PURPOSE: parse_japanese_tomorrow をテストする
    def test_parse_japanese_tomorrow(self):
        deadline, scale, certainty = _parse_deadline("明日")
        assert deadline is not None
        assert scale == TimeScale.IMMEDIATE

    # PURPOSE: parse_japanese_days をテストする
    def test_parse_japanese_days(self):
        deadline, scale, certainty = _parse_deadline("3日")
        assert deadline is not None
        assert scale == TimeScale.SHORT

    # PURPOSE: parse_english_tomorrow をテストする
    def test_parse_english_tomorrow(self):
        deadline, scale, certainty = _parse_deadline("tomorrow")
        assert deadline is not None
        assert scale == TimeScale.IMMEDIATE

    # PURPOSE: parse_english_days をテストする
    def test_parse_english_days(self):
        deadline, scale, certainty = _parse_deadline("5 days")
        assert deadline is not None
        assert scale == TimeScale.SHORT

    # PURPOSE: parse_unknown をテストする
    def test_parse_unknown(self):
        deadline, scale, certainty = _parse_deadline("something unknown")
        assert deadline is None
        assert certainty == CertaintyLevel.UNCERTAIN


# PURPOSE: _calculate_urgency tests
class TestCalculateUrgency:
    """_calculate_urgency tests"""

    # PURPOSE: urgency_immediate をテストする
    def test_urgency_immediate(self):
        assert _calculate_urgency(12) == 1.0  # < 24h

    # PURPOSE: urgency_3days をテストする
    def test_urgency_3days(self):
        assert _calculate_urgency(48) == 0.8  # < 72h

    # PURPOSE: urgency_week をテストする
    def test_urgency_week(self):
        assert _calculate_urgency(120) == 0.6  # < 168h

    # PURPOSE: urgency_3weeks をテストする
    def test_urgency_3weeks(self):
        assert _calculate_urgency(336) == 0.4  # < 504h

    # PURPOSE: urgency_none をテストする
    def test_urgency_none(self):
        assert _calculate_urgency(None) == 0.3


# PURPOSE: _calculate_slack tests
class TestCalculateSlack:
    """_calculate_slack tests"""

    # PURPOSE: slack_ample をテストする
    def test_slack_ample(self):
        assert _calculate_slack(100, 40) == SlackLevel.AMPLE  # ratio = 2.5

    # PURPOSE: slack_adequate をテストする
    def test_slack_adequate(self):
        assert _calculate_slack(60, 40) == SlackLevel.ADEQUATE  # ratio = 1.5

    # PURPOSE: slack_tight をテストする
    def test_slack_tight(self):
        assert _calculate_slack(30, 40) == SlackLevel.TIGHT  # ratio = 0.75

    # PURPOSE: slack_overdue をテストする
    def test_slack_overdue(self):
        assert _calculate_slack(10, 40) == SlackLevel.OVERDUE  # ratio = 0.25

    # PURPOSE: slack_zero_remaining をテストする
    def test_slack_zero_remaining(self):
        assert _calculate_slack(0, 40) == SlackLevel.OVERDUE

    # PURPOSE: slack_none_remaining をテストする
    def test_slack_none_remaining(self):
        assert _calculate_slack(None, 40) == SlackLevel.ADEQUATE


# PURPOSE: evaluate_time integration tests
class TestEvaluateTime:
    """evaluate_time integration tests"""

    # PURPOSE: evaluate_with_iso_date をテストする
    def test_evaluate_with_iso_date(self):
        future = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        result = evaluate_time(
            task="テスト実装",
            deadline_str=future,
            estimated_hours=10,
        )
        assert result.task == "テスト実装"
        assert result.deadline is not None
        assert result.certainty == CertaintyLevel.CERTAIN

    # PURPOSE: evaluate_with_japanese をテストする
    def test_evaluate_with_japanese(self):
        result = evaluate_time(
            task="ドキュメント作成",
            deadline_str="来週",
            estimated_hours=5,
        )
        assert result.deadline is not None
        assert result.time_scale == TimeScale.SHORT

    # PURPOSE: evaluate_includes_critical_path をテストする
    def test_evaluate_includes_critical_path(self):
        result = evaluate_time(
            task="最終レビュー",
            deadline_str="3日",
            estimated_hours=2,
            critical_path=["設計完了", "実装完了"],
        )
        assert len(result.critical_path) == 2

    # PURPOSE: evaluate_generates_recommendation をテストする
    def test_evaluate_generates_recommendation(self):
        result = evaluate_time(
            task="緊急対応",
            deadline_str="今日",
            estimated_hours=30,  # More than 24h remaining → TIGHT/OVERDUE
        )
        assert "⚠️" in result.recommendation or "🛑" in result.recommendation


# PURPOSE: format_chronos_markdown tests
class TestFormatChronosMarkdown:
    """format_chronos_markdown tests"""

    # PURPOSE: format_includes_key_fields をテストする
    def test_format_includes_key_fields(self):
        result = evaluate_time(
            task="テストタスク",
            deadline_str="明日",
            estimated_hours=4,
        )
        markdown = format_chronos_markdown(result)
        assert "K2 Chronos" in markdown
        assert "テストタスク" in markdown
        assert "余裕度" in markdown


# PURPOSE: encode_chronos_observation tests
class TestEncodeChronosObservation:
    """encode_chronos_observation tests"""

    # PURPOSE: encode_certain_deadline をテストする
    def test_encode_certain_deadline(self):
        result = ChronosResult(
            task="test",
            deadline=datetime.now() + timedelta(hours=48),
            deadline_str="2 days",
            time_scale=TimeScale.SHORT,
            certainty=CertaintyLevel.CERTAIN,
            slack=SlackLevel.ADEQUATE,
            urgency=0.8,
            estimated_hours=10,
            remaining_hours=48,
            recommendation="計画通り",
        )
        obs = encode_chronos_observation(result)
        assert obs["context_clarity"] == 0.9  # Certain
        assert obs["urgency"] == 0.8
        assert obs["confidence"] == 0.7  # Adequate

    # PURPOSE: encode_uncertain_deadline をテストする
    def test_encode_uncertain_deadline(self):
        result = ChronosResult(
            task="test",
            deadline=None,
            deadline_str="来週くらい",
            time_scale=TimeScale.SHORT,
            certainty=CertaintyLevel.UNCERTAIN,
            slack=SlackLevel.TIGHT,
            urgency=0.6,
            estimated_hours=20,
            remaining_hours=100,
            recommendation="加速",
        )
        obs = encode_chronos_observation(result)
        assert obs["context_clarity"] == 0.5  # Uncertain
        assert obs["confidence"] == 0.4  # Tight
