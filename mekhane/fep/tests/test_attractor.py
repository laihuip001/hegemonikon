# PROOF: [L2/テスト] <- mekhane/fep/tests/
# PURPOSE: SeriesAttractor の basin of attraction を検証する
"""
Test suite for SeriesAttractor

各 Series に対応する入力が正しい attractor に収束するかを検証。
Spisak & Friston 2025 の知見:
- 直交 attractor は入力空間を効率的に張る
- 境界入力は oscillatory activity で複数 attractor を活性化
"""

import pytest
from mekhane.fep.attractor import SeriesAttractor, AttractorResult


@pytest.fixture(scope="module")
def attractor():
    """Module-scoped fixture: embedding は1回だけ計算"""
    return SeriesAttractor(threshold=0.10, oscillation_margin=0.05)


class TestBasinOfAttraction:
    """各 Series の basin of attraction テスト"""

    def test_o_series_why(self, attractor: SeriesAttractor):
        """'why' → O-series"""
        results = attractor.suggest("Why does this project exist? What is its fundamental purpose?")
        assert len(results) >= 1
        assert results[0].series == "O"

    def test_o_series_essence(self, attractor: SeriesAttractor):
        """'essence' → O-series"""
        results = attractor.suggest("What is the essential nature and meaning of this system?")
        assert len(results) >= 1
        assert results[0].series == "O"

    def test_s_series_design(self, attractor: SeriesAttractor):
        """'design' → S-series"""
        results = attractor.suggest("How should we design the architecture and implementation plan?")
        assert len(results) >= 1
        assert results[0].series == "S"

    def test_s_series_method(self, attractor: SeriesAttractor):
        """'method' → S-series"""
        results = attractor.suggest("What framework and methodology should we use to build this?")
        assert len(results) >= 1
        assert results[0].series == "S"

    def test_h_series_emotion(self, attractor: SeriesAttractor):
        """'emotion' → H-series"""
        results = attractor.suggest("How do you feel about this? What is your gut feeling and emotional response?")
        assert len(results) >= 1
        assert results[0].series == "H"

    def test_p_series_scope(self, attractor: SeriesAttractor):
        """'scope' → P-series"""
        results = attractor.suggest("Define the boundaries and scope of this domain. What is in and out of scope?")
        assert len(results) >= 1
        assert results[0].series == "P"

    def test_k_series_timing(self, attractor: SeriesAttractor):
        """'timing' → K-series"""
        results = attractor.suggest("Is now the right time? What is the deadline and schedule?")
        assert len(results) >= 1
        assert results[0].series == "K"

    def test_k_series_research(self, attractor: SeriesAttractor):
        """'research' → K-series"""
        results = attractor.suggest("We need to research the academic literature and review scholarly papers")
        assert len(results) >= 1
        assert results[0].series == "K"

    def test_a_series_judgment(self, attractor: SeriesAttractor):
        """'judgment' → A-series"""
        results = attractor.suggest("Evaluate these alternatives and make a precise judgment about which is correct")
        assert len(results) >= 1
        assert results[0].series == "A"


class TestOscillation:
    """境界入力の oscillatory activity テスト"""

    def test_ambiguous_returns_multiple(self, attractor: SeriesAttractor):
        """曖昧入力 → 複数 Series が活性化"""
        results = attractor.suggest_all("全体を分析する")
        # suggest_all は常に6つ返す
        assert len(results) == 6

    def test_all_series_above_zero(self, attractor: SeriesAttractor):
        """全 Series が0以上の similarity を持つ"""
        results = attractor.suggest_all("考える")
        for r in results:
            assert r.similarity >= 0.0


class TestEdgeCases:
    """エッジケーステスト"""

    def test_empty_input(self, attractor: SeriesAttractor):
        """空文字列でもエラーにならない"""
        results = attractor.suggest("")
        assert isinstance(results, list)

    def test_result_has_workflows(self, attractor: SeriesAttractor):
        """結果に workflows が含まれる"""
        results = attractor.suggest("なぜ")
        if results:
            assert len(results[0].workflows) > 0

    def test_result_repr(self, attractor: SeriesAttractor):
        """AttractorResult の repr が動作する"""
        result = AttractorResult(
            series="O", name="Ousia (本質)",
            similarity=0.742, workflows=["/noe"]
        )
        assert "O" in repr(result)
        assert "0.742" in repr(result)

    def test_suggest_all_returns_six(self, attractor: SeriesAttractor):
        """suggest_all は常に6 Series を返す"""
        results = attractor.suggest_all("テスト")
        assert len(results) == 6
        series_set = {r.series for r in results}
        assert series_set == {"O", "S", "H", "P", "K", "A"}
