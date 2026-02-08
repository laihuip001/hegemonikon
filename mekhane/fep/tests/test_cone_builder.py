#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → cone_builder.py (@converge C0-C3) の正確性を検証する必要がある
   → compute_dispersion, converge, describe_cone の動作保証
   → test_cone_builder.py が担う

Q.E.D.
"""

import pytest

from mekhane.fep.category import Cone, Series
from mekhane.fep.cone_builder import (
    compute_dispersion,
    converge,
    describe_cone,
    is_uniform_pw,
    normalize_pw,
    resolve_method,
)


# =============================================================================
# C0: Precision Weighting
# =============================================================================


class TestNormalizePW:
    """C0: PW 正規化テスト。"""

    def test_none_pw_gives_uniform(self):
        result = normalize_pw({"O1": "a", "O2": "b"}, pw=None)
        assert all(v == 1.0 for v in result.values())

    def test_positive_pw_increases_weight(self):
        result = normalize_pw({"O1": "a"}, pw={"O1": 1.0})
        assert result["O1"] == 2.0

    def test_negative_pw_decreases_weight(self):
        result = normalize_pw({"O1": "a"}, pw={"O1": -1.0})
        assert result["O1"] == 0.0

    def test_pw_clamped_to_range(self):
        result = normalize_pw({"O1": "a"}, pw={"O1": 5.0})
        assert result["O1"] == 2.0  # clamped to 1.0 → 1+1=2

    def test_missing_pw_keys_default_to_neutral(self):
        result = normalize_pw({"O1": "a", "O2": "b"}, pw={"O1": 0.5})
        assert result["O2"] == 1.0


class TestIsUniformPW:
    """PW 均等判定テスト。"""

    def test_none_is_uniform(self):
        assert is_uniform_pw(None) is True

    def test_empty_is_uniform(self):
        assert is_uniform_pw({}) is True

    def test_all_zero_is_uniform(self):
        assert is_uniform_pw({"O1": 0.0, "O2": 0.0}) is True

    def test_nonzero_is_not_uniform(self):
        assert is_uniform_pw({"O1": 0.5}) is False


# =============================================================================
# C1: Dispersion
# =============================================================================


class TestComputeDispersion:
    """C1: V[outputs] 計算テスト。"""

    def test_empty_outputs(self):
        assert compute_dispersion({}) == 0.0

    def test_single_output(self):
        assert compute_dispersion({"O1": "hello"}) == 0.0

    def test_identical_outputs_low_dispersion(self):
        v = compute_dispersion({
            "O1": "同じテキスト",
            "O2": "同じテキスト",
            "O3": "同じテキスト",
            "O4": "同じテキスト",
        })
        assert v == 0.0

    def test_different_outputs_high_dispersion(self):
        v = compute_dispersion({
            "O1": "alpha beta gamma",
            "O2": "one two three",
            "O3": "foo bar baz",
            "O4": "xyz uvw rst",
        })
        assert v > 0.5

    def test_negation_contradiction_adds_bonus(self):
        """否定混在で V が上がる。"""
        base = compute_dispersion({
            "H1": "進むべきだ",
            "H2": "進むべきだ",
        })
        with_neg = compute_dispersion({
            "H1": "進むべきだ",
            "H2": "進むべきではない",
        })
        assert with_neg > base

    def test_direction_contradiction_adds_bonus(self):
        """方向性矛盾 (GO vs WAIT) で V が上がる。"""
        v = compute_dispersion({
            "K1": "実行する、開始する",
            "K2": "中止する、止める",
        })
        # 方向性ボーナス (+0.2) が加算される
        assert v > 0.3


# =============================================================================
# C2: Resolution Method
# =============================================================================


class TestResolveMethod:
    """C2: 解消法判定テスト。"""

    def test_low_dispersion_uniform_pw(self):
        assert resolve_method(0.05, pw=None) == "simple"

    def test_low_dispersion_with_pw(self):
        assert resolve_method(0.05, pw={"O1": 0.5}) == "pw_weighted"

    def test_medium_dispersion(self):
        assert resolve_method(0.2) == "pw_weighted"

    def test_high_dispersion(self):
        assert resolve_method(0.5) == "root"


# =============================================================================
# converge() pipeline
# =============================================================================


class TestConverge:
    """統合パイプラインテスト。"""

    def test_basic_converge(self):
        cone = converge(Series.O, {
            "O1": "認識",
            "O2": "意志",
            "O3": "探求",
            "O4": "行動",
        })
        assert isinstance(cone, Cone)
        assert cone.series == Series.O
        assert len(cone.projections) == 4
        assert cone.dispersion >= 0.0
        assert cone.resolution_method in ("simple", "pw_weighted", "root")

    def test_converge_with_pw(self):
        cone = converge(
            Series.A,
            {"A1": "感情", "A2": "判断", "A3": "見識", "A4": "知識"},
            pw={"A2": 1.0, "A1": -0.5},
        )
        assert cone.pw["A2"] == 1.0
        assert cone.pw["A1"] == -0.5

    def test_converge_with_apex(self):
        cone = converge(
            Series.H,
            {"H1": "接近", "H2": "HIGH", "H3": "欲求", "H4": "信念"},
            apex="動機は明確: 前進する",
        )
        assert cone.apex == "動機は明確: 前進する"

    def test_confidence_auto_calculated(self):
        """confidence 未指定時は自動計算される。"""
        cone = converge(Series.O, {
            "O1": "同じ", "O2": "同じ", "O3": "同じ", "O4": "同じ",
        })
        assert cone.confidence > 0

    def test_confidence_external_overrides(self):
        """外部 confidence は自動計算を上書きする。"""
        cone = converge(
            Series.O,
            {"O1": "a", "O2": "b", "O3": "c", "O4": "d"},
            confidence=95.0,
        )
        assert cone.confidence == 95.0

    def test_universality_requires_low_dispersion(self):
        """is_universal = dispersion ≤ 0.1 AND confidence ≥ 70。"""
        cone = converge(Series.O, {
            "O1": "同じ結論", "O2": "同じ結論", "O3": "同じ結論", "O4": "同じ結論",
        })
        assert cone.is_universal is True

    def test_s_series_devil_flag(self):
        """S-series で V > 0.1 なら needs_devil = True。"""
        cone = converge(Series.S, {
            "S1": "Micro", "S2": "Macro", "S3": "不問", "S4": "段階的",
        })
        # describe_cone に Devil 推奨が含まれる
        out = describe_cone(cone)
        assert "Devil" in out


# =============================================================================
# describe_cone()
# =============================================================================


class TestDescribeCone:
    """LLM フォーマットテスト。"""

    def test_output_contains_series_name(self):
        cone = converge(Series.O, {
            "O1": "a", "O2": "b", "O3": "c", "O4": "d",
        })
        out = describe_cone(cone)
        assert "Ousia" in out

    def test_output_contains_v_outputs(self):
        cone = converge(Series.H, {
            "H1": "a", "H2": "b", "H3": "c", "H4": "d",
        })
        out = describe_cone(cone)
        assert "V[outputs]" in out

    def test_pw_section_shown_when_non_uniform(self):
        cone = converge(
            Series.A,
            {"A1": "a", "A2": "b", "A3": "c", "A4": "d"},
            pw={"A2": 1.0},
        )
        out = describe_cone(cone)
        assert "Precision Weighting" in out

    def test_pw_section_hidden_when_uniform(self):
        cone = converge(Series.A, {
            "A1": "a", "A2": "b", "A3": "c", "A4": "d",
        })
        out = describe_cone(cone)
        assert "Precision Weighting" not in out

    def test_devil_only_for_s_series(self):
        """Devil 推奨は S-series のみ。"""
        for s in [Series.O, Series.H, Series.P, Series.K, Series.A]:
            cone = converge(s, {
                f"{s.name[0]}1": "x",
                f"{s.name[0]}2": "y",
                f"{s.name[0]}3": "z",
                f"{s.name[0]}4": "w",
            })
            out = describe_cone(cone)
            assert "Devil" not in out, f"Devil should not appear for {s.name}"
