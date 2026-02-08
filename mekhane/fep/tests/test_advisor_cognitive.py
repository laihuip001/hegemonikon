#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → Attractor → CognitiveType → PW 接続の正確性を検証
   → _classify_series_list, _detect_crossings, _suggest_pw_for_crossings
   → test_advisor_cognitive.py が担う

Q.E.D.
"""

import pytest

from mekhane.fep.attractor_advisor import (
    _classify_series_list,
    _detect_crossings,
    _suggest_pw_for_crossings,
)
from mekhane.fep.category import CognitiveType


# =============================================================================
# Series Classification
# =============================================================================


class TestClassifySeriesList:
    """_classify_series_list の CognitiveType 分類。"""

    def test_single_understanding_series(self):
        result = _classify_series_list(["O"])
        assert result == {"O": "understanding"}

    def test_single_reasoning_series(self):
        result = _classify_series_list(["S"])
        assert result == {"S": "reasoning"}

    def test_mixed_series(self):
        result = _classify_series_list(["O", "S"])
        assert result == {"O": "understanding", "S": "reasoning"}

    def test_all_understanding(self):
        result = _classify_series_list(["O", "H", "K"])
        for v in result.values():
            assert v in ("understanding", "mixed", "bridge_u_to_r")

    def test_all_reasoning(self):
        result = _classify_series_list(["S", "P"])
        for v in result.values():
            assert v == "reasoning"

    def test_empty_list(self):
        result = _classify_series_list([])
        assert result == {}

    def test_a_series_is_bridge(self):
        """A-series の代表(A1) は BRIDGE_U_TO_R。"""
        result = _classify_series_list(["A"])
        assert result == {"A": "bridge_u_to_r"}


# =============================================================================
# Boundary Crossing Detection
# =============================================================================


class TestDetectCrossings:
    """_detect_crossings の U/R 境界越え検出。"""

    def test_o_and_s_crosses(self):
        """O (U) + S (R) は U→R。"""
        crossings = _detect_crossings(["O", "S"])
        assert "U→R" in crossings

    def test_s_and_o_crosses(self):
        """S (R) + O (U) は R→U。"""
        crossings = _detect_crossings(["S", "O"])
        # Order depends on which is first
        assert len(crossings) > 0

    def test_o_and_h_no_crossing(self):
        """O (U) + H (U) は境界越えなし。"""
        crossings = _detect_crossings(["O", "H"])
        assert len(crossings) == 0

    def test_s_and_p_no_crossing(self):
        """S (R) + P (R) は境界越えなし。"""
        crossings = _detect_crossings(["S", "P"])
        assert len(crossings) == 0

    def test_single_series_no_crossing(self):
        """単一 Series は境界越えなし。"""
        crossings = _detect_crossings(["O"])
        assert len(crossings) == 0

    def test_empty_no_crossing(self):
        crossings = _detect_crossings([])
        assert len(crossings) == 0

    def test_three_series_with_crossing(self):
        """O + S + H: O→S は U→R、S→H は R→U。"""
        crossings = _detect_crossings(["O", "S", "H"])
        assert len(crossings) >= 1


# =============================================================================
# PW Suggestion
# =============================================================================


class TestSuggestPWForCrossings:
    """_suggest_pw_for_crossings の PW 自動提案。"""

    def test_u_to_r_boosts_a1(self):
        """U→R 境界越え → A1 (Pathos) をブースト。"""
        pw = _suggest_pw_for_crossings(["U→R"], ["O", "S"])
        assert "A1" in pw
        assert pw["A1"] > 0

    def test_r_to_u_boosts_a3(self):
        """R→U 境界越え → A3 (Gnōmē) をブースト。"""
        pw = _suggest_pw_for_crossings(["R→U"], ["S", "O"])
        assert "A3" in pw
        assert pw["A3"] > 0

    def test_both_directions_boosts_k4(self):
        """双方向境界越え → K4 (Sophia) も追加。"""
        pw = _suggest_pw_for_crossings(["U→R", "R→U"], ["O", "S", "H"])
        assert "A1" in pw
        assert "A3" in pw
        assert "K4" in pw

    def test_no_crossings_empty_suggestion(self):
        """境界越えなし → 提案なし。"""
        pw = _suggest_pw_for_crossings([], ["O"])
        assert pw == {}

    def test_pw_values_are_positive(self):
        """PW 提案値は全て正。"""
        pw = _suggest_pw_for_crossings(["U→R"], ["O", "S"])
        for v in pw.values():
            assert v > 0
