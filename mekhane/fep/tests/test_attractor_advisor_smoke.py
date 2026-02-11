"""Smoke test: attractor_advisor.py が import 可能であることを保証する。

/dia+ で指摘された死角:
- attractor_advisor.py を直接 import するテストがなかった
- 構文エラーが既存テストで検出されなかった
- このテストがあれば CI で即座に検出される
"""
import pytest


# PURPOSE: Verify import attractor advisor behaves correctly
def test_import_attractor_advisor():
    """attractor_advisor モジュールが構文的に正しく import できること。"""
    from mekhane.fep import attractor_advisor
    assert hasattr(attractor_advisor, "AttractorAdvisor")
    assert hasattr(attractor_advisor, "Recommendation")
    assert hasattr(attractor_advisor, "CompoundRecommendation")


# PURPOSE: Verify attractor advisor instantiation behaves correctly
def test_attractor_advisor_instantiation():
    """AttractorAdvisor がインスタンス化できること (force_cpu=True で軽量)。"""
    from mekhane.fep.attractor_advisor import AttractorAdvisor
    advisor = AttractorAdvisor(force_cpu=True, use_gnosis=False)
    assert advisor is not None
    assert hasattr(advisor, "recommend")
    assert hasattr(advisor, "format_for_llm")
    assert hasattr(advisor, "recommend_compound")


# PURPOSE: Verify recommendation dataclass behaves correctly
def test_recommendation_dataclass():
    """Recommendation dataclass のフィールドが期待通りであること。"""
    from mekhane.fep.attractor_advisor import Recommendation
    from mekhane.fep.attractor import OscillationType, OscillationDiagnosis

    # 最小構成で生成
    interp = OscillationDiagnosis(
        oscillation=OscillationType.CLEAR,
        theory="test",
        action="test",
        morphisms=[],
        confidence_modifier=0.0,
    )
    rec = Recommendation(
        advice="test advice",
        workflows=["/noe"],
        series=["O"],
        oscillation=OscillationType.CLEAR,
        confidence=0.9,
        interpretation=interp,
    )
    assert rec.advice == "test advice"
    assert rec.confidence == 0.9
    assert rec.cognitive_types == {}
    assert rec.boundary_crossings == []
    assert rec.pw_suggestion == {}
