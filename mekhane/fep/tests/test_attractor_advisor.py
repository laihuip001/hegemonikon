# PROOF: [L2/テスト] <- mekhane/fep/tests/
"""Tests for AttractorAdvisor and OscillationType diagnosis"""

import pytest
from mekhane.fep.attractor import (
    OscillationType,
    SeriesAttractor,
    SuggestResult,
)
from mekhane.fep.attractor_advisor import AttractorAdvisor, Recommendation


@pytest.fixture(scope="module")
def advisor():
    return AttractorAdvisor()


@pytest.fixture(scope="module")
def attractor():
    return SeriesAttractor(threshold=0.10, oscillation_margin=0.05)


# --- OscillationType / diagnose() tests ---

class TestDiagnose:
    """diagnose() メソッドと OscillationType のテスト"""

    def test_clear_convergence(self, attractor: SeriesAttractor):
        """明確な入力 → CLEAR"""
        result = attractor.diagnose(
            "How should we design the architecture and implementation plan?"
        )
        assert result.oscillation == OscillationType.CLEAR
        assert result.primary.series == "S"
        assert result.top_similarity > 0.6
        assert result.gap > 0.08

    def test_clear_scope(self, attractor: SeriesAttractor):
        """Scope → P に明確収束"""
        result = attractor.diagnose(
            "Define the boundaries and scope of this domain"
        )
        assert result.oscillation == OscillationType.CLEAR
        assert result.primary.series == "P"

    def test_suggest_result_primary(self, attractor: SeriesAttractor):
        """SuggestResult.primary プロパティ"""
        result = attractor.diagnose("Why does this exist?")
        assert result.primary is not None
        assert result.primary.series == "O"

    def test_suggest_result_is_clear(self, attractor: SeriesAttractor):
        """SuggestResult.is_clear プロパティ"""
        result = attractor.diagnose(
            "Define the boundaries and scope of this domain"
        )
        assert result.is_clear is True

    def test_suggest_result_repr(self, attractor: SeriesAttractor):
        """SuggestResult の repr"""
        result = attractor.diagnose("Why?")
        repr_str = repr(result)
        assert "top=" in repr_str

    def test_diagnose_returns_gap(self, attractor: SeriesAttractor):
        """diagnose() が gap を返す"""
        result = attractor.diagnose("Design the architecture")
        assert result.gap >= 0.0


# --- AttractorAdvisor tests ---

class TestAttractorAdvisor:
    """AttractorAdvisor のテスト"""

    def test_recommend_clear(self, advisor: AttractorAdvisor):
        """明確な入力 → 推薦テキスト生成"""
        rec = advisor.recommend(
            "How should we design the architecture?"
        )
        assert isinstance(rec, Recommendation)
        assert "S" in rec.series
        assert len(rec.workflows) > 0
        assert rec.confidence > 0.5

    def test_recommend_has_advice(self, advisor: AttractorAdvisor):
        """推薦に advice テキストが含まれる"""
        rec = advisor.recommend("Why does this project exist?")
        assert len(rec.advice) > 0

    def test_format_for_llm_clear(self, advisor: AttractorAdvisor):
        """LLM 注入形式: 明確な収束"""
        fmt = advisor.format_for_llm(
            "Define the boundaries and scope"
        )
        assert fmt.startswith("[Attractor:")
        assert "P" in fmt

    def test_format_for_llm_contains_workflows(self, advisor: AttractorAdvisor):
        """LLM 形式にワークフローが含まれる"""
        fmt = advisor.format_for_llm("Why does this exist?")
        assert "/" in fmt  # ワークフロー名は / で始まる

    def test_recommend_repr(self, advisor: AttractorAdvisor):
        """Recommendation の repr"""
        rec = advisor.recommend("Evaluate alternatives")
        repr_str = repr(rec)
        assert "Rec:" in repr_str
        assert "conf=" in repr_str


# --- Backward compatibility ---

class TestBackwardCompatibility:
    """既存の suggest() API が壊れていないことを確認"""

    def test_suggest_still_works(self, attractor: SeriesAttractor):
        """suggest() は AttractorResult のリストを返す"""
        results = attractor.suggest("Why does this exist?")
        assert isinstance(results, list)
        assert len(results) >= 1
        assert results[0].series == "O"

    def test_suggest_all_still_works(self, attractor: SeriesAttractor):
        """suggest_all() は 6 Series を返す"""
        results = attractor.suggest_all("test")
        assert len(results) == 6
