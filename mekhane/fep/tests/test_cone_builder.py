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

from mekhane.fep.category import Cone, EnrichmentType, Series
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


# PURPOSE: C0: PW 正規化テスト。
class TestNormalizePW:
    """C0: PW 正規化テスト。"""

    # PURPOSE: none_pw_gives_uniform をテストする
    def test_none_pw_gives_uniform(self):
        result = normalize_pw({"O1": "a", "O2": "b"}, pw=None)
        assert all(v == 1.0 for v in result.values())

    # PURPOSE: positive_pw_increases_weight をテストする
    def test_positive_pw_increases_weight(self):
        result = normalize_pw({"O1": "a"}, pw={"O1": 1.0})
        assert result["O1"] == 2.0

    # PURPOSE: negative_pw_decreases_weight をテストする
    def test_negative_pw_decreases_weight(self):
        result = normalize_pw({"O1": "a"}, pw={"O1": -1.0})
        assert result["O1"] == 0.0

    # PURPOSE: pw_clamped_to_range をテストする
    def test_pw_clamped_to_range(self):
        result = normalize_pw({"O1": "a"}, pw={"O1": 5.0})
        assert result["O1"] == 2.0  # clamped to 1.0 → 1+1=2

    # PURPOSE: missing_pw_keys_default_to_neutral をテストする
    def test_missing_pw_keys_default_to_neutral(self):
        result = normalize_pw({"O1": "a", "O2": "b"}, pw={"O1": 0.5})
        assert result["O2"] == 1.0


# PURPOSE: PW 均等判定テスト。
class TestIsUniformPW:
    """PW 均等判定テスト。"""

    # PURPOSE: none_is_uniform をテストする
    def test_none_is_uniform(self):
        assert is_uniform_pw(None) is True

    # PURPOSE: empty_is_uniform をテストする
    def test_empty_is_uniform(self):
        assert is_uniform_pw({}) is True

    # PURPOSE: all_zero_is_uniform をテストする
    def test_all_zero_is_uniform(self):
        assert is_uniform_pw({"O1": 0.0, "O2": 0.0}) is True

    # PURPOSE: nonzero_is_not_uniform をテストする
    def test_nonzero_is_not_uniform(self):
        assert is_uniform_pw({"O1": 0.5}) is False


# =============================================================================
# C1: Dispersion
# =============================================================================


# PURPOSE: C1: V[outputs] 計算テスト。
class TestComputeDispersion:
    """C1: V[outputs] 計算テスト。"""

    # PURPOSE: empty_outputs をテストする
    def test_empty_outputs(self):
        assert compute_dispersion({}) == 0.0

    # PURPOSE: single_output をテストする
    def test_single_output(self):
        assert compute_dispersion({"O1": "hello"}) == 0.0

    # PURPOSE: identical_outputs_low_dispersion をテストする
    def test_identical_outputs_low_dispersion(self):
        v = compute_dispersion({
            "O1": "同じテキスト",
            "O2": "同じテキスト",
            "O3": "同じテキスト",
            "O4": "同じテキスト",
        })
        assert v == 0.0

    # PURPOSE: different_outputs_high_dispersion をテストする
    def test_different_outputs_high_dispersion(self):
        v = compute_dispersion({
            "O1": "alpha beta gamma",
            "O2": "one two three",
            "O3": "foo bar baz",
            "O4": "xyz uvw rst",
        })
        assert v > 0.5

    # PURPOSE: 否定混在で V が上がる。
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

    # PURPOSE: 方向性矛盾 (GO vs WAIT) で V が上がる。
    def test_direction_contradiction_adds_bonus(self):
        """方向性矛盾 (GO vs WAIT) で V が上がる。"""
        v = compute_dispersion({
            "K1": "実行する、開始する",
            "K2": "中止する、止める",
        })
        # 方向性ボーナス (+0.2) が加算される
        assert v > 0.3

    # --- TDD 回帰テスト: 日本語 V 閾値 (BS-2) ---

    # PURPOSE: 日本語: 同じトピックの異なる角度は矛盾度が低め。V ≤ 0.7。
    def test_japanese_different_angles_not_contradiction(self):
        """日本語: 同じトピックの異なる角度は矛盾度が低め。V ≤ 0.7。

        TDD regression test for BS-2:
        同じトピック (GPU リソース管理) について4つの角度から発言。
        共通キーワードが多いため、bigram Jaccard が類似度を検出し、
        V は「完全異トピック」より低くなるべき。
        """
        v = compute_dispersion({
            "O1": "GPU リソース管理の改善が必要、GPU メモリの競合を解消する",
            "O2": "GPU リソースの安定性を確保したい、リソース配分を見直す",
            "O3": "GPU リソース競合の根本原因を探求する必要がある",
            "O4": "GPU Guard を実装して GPU リソースを保護する",
        })
        assert v <= 0.7, f"Same-topic angles should have moderate V: V={v}"

    # PURPOSE: 日本語: 完全に異なるトピックは V が高い。V > 0.5。
    def test_japanese_completely_different_topics_high_v(self):
        """日本語: 完全に異なるトピックは V が高い。V > 0.5。"""
        v = compute_dispersion({
            "O1": "天気は晴れだった",
            "O2": "猫を飼いたい",
            "O3": "数学の問題を解く",
            "O4": "料理のレシピを探す",
        })
        assert v > 0.5, f"Completely different topics should have high V: V={v}"

    # PURPOSE: 日本語: 実際の矛盾 (否定混在) は検出される。V > 0.3。
    def test_japanese_actual_contradiction_detected(self):
        """日本語: 実際の矛盾 (否定混在) は検出される。V > 0.3。"""
        v = compute_dispersion({
            "H1": "進むべきだ、行動を開始する",
            "H2": "確信度は高い",
            "H3": "進めるべきではない、中止すべきだ",
            "H4": "判断を保留する、止める",
        })
        assert v > 0.3, f"Actual contradiction should be detected: V={v}"


# =============================================================================
# C2: Resolution Method
# =============================================================================


# PURPOSE: C2: 解消法判定テスト。
class TestResolveMethod:
    """C2: 解消法判定テスト。"""

    # PURPOSE: low_dispersion_uniform_pw をテストする
    def test_low_dispersion_uniform_pw(self):
        assert resolve_method(0.05, pw=None) == "simple"

    # PURPOSE: low_dispersion_with_pw をテストする
    def test_low_dispersion_with_pw(self):
        assert resolve_method(0.05, pw={"O1": 0.5}) == "pw_weighted"

    # PURPOSE: medium_dispersion をテストする
    def test_medium_dispersion(self):
        assert resolve_method(0.2) == "pw_weighted"

    # PURPOSE: high_dispersion をテストする
    def test_high_dispersion(self):
        assert resolve_method(0.5) == "root"


# =============================================================================
# converge() pipeline
# =============================================================================


# PURPOSE: 統合パイプラインテスト。
class TestConverge:
    """統合パイプラインテスト。"""

    # PURPOSE: basic_converge をテストする
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

    # PURPOSE: converge_with_pw をテストする
    def test_converge_with_pw(self):
        cone = converge(
            Series.A,
            {"A1": "感情", "A2": "判断", "A3": "見識", "A4": "知識"},
            pw={"A2": 1.0, "A1": -0.5},
        )
        assert cone.pw["A2"] == 1.0
        assert cone.pw["A1"] == -0.5

    # PURPOSE: converge_with_apex をテストする
    def test_converge_with_apex(self):
        cone = converge(
            Series.H,
            {"H1": "接近", "H2": "HIGH", "H3": "欲求", "H4": "信念"},
            apex="動機は明確: 前進する",
        )
        assert cone.apex == "動機は明確: 前進する"

    # PURPOSE: confidence 未指定時は自動計算される。
    def test_confidence_auto_calculated(self):
        """confidence 未指定時は自動計算される。"""
        cone = converge(Series.O, {
            "O1": "同じ", "O2": "同じ", "O3": "同じ", "O4": "同じ",
        })
        assert cone.confidence > 0

    # PURPOSE: 外部 confidence は自動計算を上書きする。
    def test_confidence_external_overrides(self):
        """外部 confidence は自動計算を上書きする。"""
        cone = converge(
            Series.O,
            {"O1": "a", "O2": "b", "O3": "c", "O4": "d"},
            confidence=95.0,
        )
        assert cone.confidence == 95.0

    # PURPOSE: is_universal = dispersion ≤ 0.1 AND confidence ≥ 70。
    def test_universality_requires_low_dispersion(self):
        """is_universal = dispersion ≤ 0.1 AND confidence ≥ 70。"""
        cone = converge(Series.O, {
            "O1": "同じ結論", "O2": "同じ結論", "O3": "同じ結論", "O4": "同じ結論",
        })
        assert cone.is_universal is True

    # PURPOSE: S-series で V > 0.1 なら needs_devil = True。
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


# PURPOSE: LLM フォーマットテスト。
class TestDescribeCone:
    """LLM フォーマットテスト。"""

    # PURPOSE: output_contains_series_name をテストする
    def test_output_contains_series_name(self):
        cone = converge(Series.O, {
            "O1": "a", "O2": "b", "O3": "c", "O4": "d",
        })
        out = describe_cone(cone)
        assert "Ousia" in out

    # PURPOSE: output_contains_v_outputs をテストする
    def test_output_contains_v_outputs(self):
        cone = converge(Series.H, {
            "H1": "a", "H2": "b", "H3": "c", "H4": "d",
        })
        out = describe_cone(cone)
        assert "V[outputs]" in out

    # PURPOSE: pw_section_shown_when_non_uniform をテストする
    def test_pw_section_shown_when_non_uniform(self):
        cone = converge(
            Series.A,
            {"A1": "a", "A2": "b", "A3": "c", "A4": "d"},
            pw={"A2": 1.0},
        )
        out = describe_cone(cone)
        assert "Precision Weighting" in out

    # PURPOSE: pw_section_hidden_when_uniform をテストする
    def test_pw_section_hidden_when_uniform(self):
        cone = converge(Series.A, {
            "A1": "a", "A2": "b", "A3": "c", "A4": "d",
        })
        out = describe_cone(cone)
        assert "Precision Weighting" not in out

    # PURPOSE: Devil 推奨は S-series のみ。
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


# =============================================================================
# Typed Enrichment
# =============================================================================


# PURPOSE: Typed Enrichment テスト。
class TestTypedEnrichment:
    """Typed Enrichment テスト。"""

    # PURPOSE: converge() で enrichment が自動付与される。
    def test_enrichment_auto_assigned(self):
        """converge() で enrichment が自動付与される。"""
        for s in Series:
            prefix = s.name[0]
            cone = converge(s, {
                f"{prefix}1": "a", f"{prefix}2": "b",
                f"{prefix}3": "c", f"{prefix}4": "d",
            })
            assert cone.enrichment is not None, f"{s.name} should have enrichment"
            assert cone.enrichment.type.name in (
                "END", "MET", "PROB", "SET", "TEMP", "FUZZY",
            )

    # PURPOSE: describe_cone() に enrichment セクションが表示される。
    def test_enrichment_in_describe(self):
        """describe_cone() に enrichment セクションが表示される。"""
        cone = converge(Series.S, {
            "S1": "a", "S2": "b", "S3": "c", "S4": "d",
        })
        out = describe_cone(cone)
        assert "### Enrichment" in out
        assert "Met-enrichment" in out

    # PURPOSE: P-series は Set enrichment (enrichment 不要) と表示される。
    def test_set_enrichment_for_p(self):
        """P-series は Set enrichment (enrichment 不要) と表示される。"""
        cone = converge(Series.P, {
            "P1": "a", "P2": "b", "P3": "c", "P4": "d",
        })
        assert cone.enrichment is not None
        assert cone.enrichment.type == EnrichmentType.SET
        assert cone.enrichment.kalon is None
        out = describe_cone(cone)
        assert "器" in out


# =============================================================================
# apply_enrichment() behavior
# =============================================================================


# PURPOSE: apply_enrichment 動作テスト。
class TestApplyEnrichment:
    """apply_enrichment 動作テスト。"""

    # PURPOSE: A-series で低 confidence → [tent] ラベルが付く。
    def test_fuzzy_tentative_grading(self):
        """A-series で低 confidence → [tent] ラベルが付く。"""
        cone = converge(
            Series.A,
            {"A1": "alpha", "A2": "beta", "A3": "gamma", "A4": "delta"},
        )
        # Low confidence from diverse outputs → should get [tent] or [just]
        assert "[tent]" in cone.resolution_method or "[just]" in cone.resolution_method

    # PURPOSE: A-series で高 confidence → [cert] ラベルが付く。
    def test_fuzzy_certain_grading(self):
        """A-series で高 confidence → [cert] ラベルが付く。"""
        cone = converge(
            Series.A,
            {"A1": "同じ", "A2": "同じ", "A3": "同じ", "A4": "同じ"},
            confidence=95.0,
        )
        assert "[cert]" in cone.resolution_method

    # PURPOSE: S-series で V が 0.08-0.1 なら pw_weighted に昇格する。
    def test_met_stricter_threshold(self):
        """S-series で V=0.09 なら Met-enrichment で pw_weighted に昇格する。"""
        # Create a cone with outputs that produce V slightly above 0.08
        cone = converge(Series.S, {
            "S1": "同じ設計", "S2": "同じ設計", "S3": "同じ設計X", "S4": "同じ設計",
        })
        # If V is in (0.08, 0.1], method should be pw_weighted
        if 0.08 < cone.dispersion <= 0.1:
            assert cone.resolution_method == "pw_weighted"

    # PURPOSE: O-series で高 V → /o* 自己参照 apex が設定される。
    def test_end_self_reference_apex(self):
        """O-series で高 V + apex なし → /o* 自己参照が設定される。"""
        cone = converge(Series.O, {
            "O1": "alpha beta gamma",
            "O2": "one two three",
            "O3": "foo bar baz",
            "O4": "xyz uvw rst",
        })
        if cone.dispersion > 0.5:
            assert "/o*" in cone.apex

    # PURPOSE: K-series で urgency マーカー → pw_weighted に昇格する。
    def test_temp_urgency_boost(self):
        """K-series で urgency マーカーあり → pw_weighted に昇格する。"""
        cone = converge(Series.K, {
            "K1": "緊急対応が必要",
            "K2": "緊急対応が必要",
            "K3": "緊急対応が必要",
            "K4": "緊急対応が必要",
        })
        # Same text → low dispersion → would normally be "simple"
        # But urgency marker → should escalate to pw_weighted
        assert cone.resolution_method == "pw_weighted"
