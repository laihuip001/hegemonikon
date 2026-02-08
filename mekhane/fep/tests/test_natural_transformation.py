#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → η₁-η₅ (MP↔HGK 自然変換) の操作的正確性を検証する必要がある
   → NaturalTransformation コンポーネントの存在 + 可換性
   → CognitiveType 分類の完全性
   → test_natural_transformation.py が担う

Q.E.D.
"""

import pytest

from mekhane.fep.category import (
    COGNITIVE_TYPES,
    FUNCTORS,
    MORPHISMS,
    NATURAL_TRANSFORMATIONS,
    THEOREMS,
    CognitiveType,
    NaturalTransformation,
    Series,
)
from mekhane.fep.cone_builder import (
    NaturalityResult,
    classify_cognitive_type,
    is_cross_boundary_morphism,
    verify_naturality,
)


# =============================================================================
# η₁-η₅ Component Existence
# =============================================================================


class TestMPHGKComponents:
    """η₁-η₅ の5コンポーネントが正しく定義されている。"""

    def test_mp_hgk_exists_in_registry(self):
        """mp_hgk NaturalTransformation がレジストリに存在する。"""
        assert "mp_hgk" in NATURAL_TRANSFORMATIONS

    def test_has_five_components(self):
        """η₁-η₅: 5つのコンポーネントが存在する。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert len(nt.components) == 5

    def test_eta1_s1_to_o1(self):
        """η₁: Stage 1 (理解) → O1 Noēsis。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert nt.component_at("S1") == "O1"

    def test_eta2_s2_to_a1(self):
        """η₂: Stage 2 (予備判断) → A1 Pathos。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert nt.component_at("S2") == "A1"

    def test_eta3_s3_to_a2(self):
        """η₃: Stage 3 (批判的再評価) → A2 Krisis。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert nt.component_at("S3") == "A2"

    def test_eta4_s4_to_o4(self):
        """η₄: Stage 4 (決定+説明) → O4 Energeia。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert nt.component_at("S4") == "O4"

    def test_eta5_s5_to_a4(self):
        """η₅: Stage 5 (確信度評価) → A4 Epistēmē。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert nt.component_at("S5") == "A4"

    def test_all_targets_are_valid_theorems(self):
        """全コンポーネントのターゲットが THEOREMS に存在する。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        for src, tgt in nt.components.items():
            assert tgt in THEOREMS, f"η component {src}→{tgt}: {tgt} not in THEOREMS"

    def test_source_functor_is_mp(self):
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert nt.source_functor == "MP"

    def test_target_functor_is_hgk(self):
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        assert nt.target_functor == "HGK"


# =============================================================================
# Naturality Verification
# =============================================================================


class TestNaturalityVerification:
    """verify_naturality() による可換性検証。"""

    def test_mp_hgk_verify_returns_result(self):
        """verify_naturality が NaturalityResult を返す。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        result = verify_naturality(nt)
        assert isinstance(result, NaturalityResult)

    def test_mp_hgk_all_components_valid(self):
        """mp_hgk の全コンポーネントが有効な定理を指す。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        result = verify_naturality(nt)
        # All checks should pass (components map to valid theorems)
        for check in result.checks:
            assert check["pass"], f"Check failed: {check}"

    def test_mp_hgk_is_natural(self):
        """mp_hgk は (fallback mode で) natural と判定される。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        result = verify_naturality(nt)
        assert result.is_natural

    def test_mp_hgk_with_source_functor(self):
        """MP Functor を明示的に渡して可換性チェック。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        mp_functor = FUNCTORS["mp"]
        result = verify_naturality(nt, source_functor=mp_functor)
        assert isinstance(result, NaturalityResult)
        # Should have checks for parsed morphisms
        assert len(result.checks) > 0

    def test_mp_hgk_summary_format(self):
        """summary プロパティが正しいフォーマットで返る。"""
        nt = NATURAL_TRANSFORMATIONS["mp_hgk"]
        result = verify_naturality(nt)
        assert "η_MP" in result.summary
        assert "/" in result.summary  # "N/M checks passed"

    def test_eta_boot_bye_verify(self):
        """既存の η (boot⊣bye) も verify_naturality で検証できる。"""
        nt = NATURAL_TRANSFORMATIONS["eta"]
        result = verify_naturality(nt)
        assert isinstance(result, NaturalityResult)

    def test_invalid_transformation_detected(self):
        """無効なコンポーネントが検出される。"""
        bad_nt = NaturalTransformation(
            name="bad",
            source_functor="X",
            target_functor="Y",
            components={"foo": "NONEXISTENT"},
        )
        result = verify_naturality(bad_nt)
        assert not result.is_natural
        assert len(result.violations) > 0


# =============================================================================
# Cognitive Type Classification
# =============================================================================


class TestCognitiveTypeClassification:
    """全24定理の Understanding/Reasoning 分類テスト。"""

    def test_all_24_theorems_classified(self):
        """全24定理が COGNITIVE_TYPES に含まれる。"""
        assert len(COGNITIVE_TYPES) == 24
        for tid in THEOREMS:
            assert tid in COGNITIVE_TYPES, f"{tid} not classified"

    def test_o_series_is_understanding(self):
        """O-series は全て Understanding。"""
        for i in range(1, 5):
            assert COGNITIVE_TYPES[f"O{i}"] == CognitiveType.UNDERSTANDING

    def test_s_series_is_reasoning(self):
        """S-series は全て Reasoning。"""
        for i in range(1, 5):
            assert COGNITIVE_TYPES[f"S{i}"] == CognitiveType.REASONING

    def test_h_series_is_understanding(self):
        """H-series は全て Understanding。"""
        for i in range(1, 5):
            assert COGNITIVE_TYPES[f"H{i}"] == CognitiveType.UNDERSTANDING

    def test_p_series_is_reasoning(self):
        """P-series は全て Reasoning。"""
        for i in range(1, 5):
            assert COGNITIVE_TYPES[f"P{i}"] == CognitiveType.REASONING

    def test_classify_function_works(self):
        """classify_cognitive_type() が正しく動作する。"""
        assert classify_cognitive_type("O1") == CognitiveType.UNDERSTANDING
        assert classify_cognitive_type("S2") == CognitiveType.REASONING
        assert classify_cognitive_type("A1") == CognitiveType.BRIDGE_U_TO_R

    def test_classify_invalid_raises(self):
        """存在しない定理 ID で KeyError。"""
        with pytest.raises(KeyError):
            classify_cognitive_type("Z9")


# =============================================================================
# Bridge Theorems
# =============================================================================


class TestBridgeTheorems:
    """A1 (U→R) と A3 (R→U) が Bridge 定理として正しく分類。"""

    def test_a1_is_bridge_u_to_r(self):
        """A1 Pathos は Understanding → Reasoning の橋。

        Val×Val 座標: Valence 軸が U/R 遷移点。
        """
        assert COGNITIVE_TYPES["A1"] == CognitiveType.BRIDGE_U_TO_R

    def test_a3_is_bridge_r_to_u(self):
        """A3 Gnōmē は Reasoning → Understanding の橋。

        Prec×Val 座標: Precision (R) から Valence (U) への射出。
        """
        assert COGNITIVE_TYPES["A3"] == CognitiveType.BRIDGE_R_TO_U

    def test_a2_is_reasoning(self):
        """A2 Krisis は純粋な Reasoning (批判的評価)。"""
        assert COGNITIVE_TYPES["A2"] == CognitiveType.REASONING

    def test_a4_is_reasoning(self):
        """A4 Epistēmē は純粋な Reasoning (知識確定)。"""
        assert COGNITIVE_TYPES["A4"] == CognitiveType.REASONING

    def test_k4_is_mixed(self):
        """K4 Sophia は Mixed (Understanding + Reasoning)。"""
        assert COGNITIVE_TYPES["K4"] == CognitiveType.MIXED


# =============================================================================
# Cross-Boundary Morphism Detection
# =============================================================================


class TestCrossBoundaryMorphism:
    """Understanding/Reasoning 境界越えモルフィズムの検出。"""

    def test_o1_to_s1_is_u_to_r(self):
        """O1 (U) → S1 (R) は U→R 遷移。"""
        assert is_cross_boundary_morphism("O1", "S1") == "U→R"

    def test_s1_to_h1_is_r_to_u(self):
        """S1 (R) → H1 (U) は R→U 遷移。"""
        assert is_cross_boundary_morphism("S1", "H1") == "R→U"

    def test_o1_to_o2_is_none(self):
        """O1 (U) → O2 (U) は境界越えなし。"""
        assert is_cross_boundary_morphism("O1", "O2") is None

    def test_s1_to_s2_is_none(self):
        """S1 (R) → S2 (R) は境界越えなし。"""
        assert is_cross_boundary_morphism("S1", "S2") is None

    def test_invalid_ids_return_none(self):
        """存在しない定理 ID は None。"""
        assert is_cross_boundary_morphism("Z9", "O1") is None


# =============================================================================
# Vertical Composition
# =============================================================================


class TestVerticalComposition:
    """NaturalTransformation の垂直合成テスト。"""

    def test_compose_eta_with_compatible(self):
        """互換性のある自然変換の垂直合成が成功する。

        垂直合成 β∘α: F ⇒ H (α: F⇒G, β: G⇒H)
        コンポーネントはオブジェクト X ごとに β_X ∘ α_X。
        mp_hgk の components keys = S1-S5。β も同じキーを使う。
        """
        # Create a compatible transformation: HGK ⇒ Id_Cog
        # 同じオブジェクト (S1-S5) 上で定義
        hgk_to_cog = NaturalTransformation(
            name="β",
            source_functor="HGK",
            target_functor="Id_Cog",
            components={
                "S1": "O1_final",
                "S2": "A1_final",
                "S3": "A2_final",
                "S4": "O4_final",
                "S5": "A4_final",
            },
        )
        mp_hgk = NATURAL_TRANSFORMATIONS["mp_hgk"]
        composed = mp_hgk.compose(hgk_to_cog)
        assert composed is not None
        assert composed.source_functor == "MP"
        assert composed.target_functor == "Id_Cog"
        # Should have 5 composed components
        assert len(composed.components) == 5
        # Composed component at S1 = β_S1 ∘ α_S1 = "O1_final∘O1"
        assert "O1" in composed.components["S1"]

    def test_compose_incompatible_returns_none(self):
        """非互換の自然変換の合成は None を返す。"""
        mp_hgk = NATURAL_TRANSFORMATIONS["mp_hgk"]
        eta = NATURAL_TRANSFORMATIONS["eta"]
        assert mp_hgk.compose(eta) is None  # HGK ≠ Id_Mem


# =============================================================================
# MP Functor Registry
# =============================================================================


class TestMPFunctor:
    """MP Functor がレジストリに正しく登録されている。"""

    def test_mp_functor_exists(self):
        assert "mp" in FUNCTORS

    def test_mp_source_is_mp_category(self):
        assert FUNCTORS["mp"].source_cat == "MP"

    def test_mp_target_is_cog(self):
        assert FUNCTORS["mp"].target_cat == "Cog"

    def test_mp_has_five_objects(self):
        assert len(FUNCTORS["mp"].object_map) == 5

    def test_mp_has_morphisms(self):
        """MP Functor に射のマッピングが存在する。"""
        assert len(FUNCTORS["mp"].morphism_map) > 0

    def test_mp_feedback_morphism(self):
        """AMP フィードバックループ S3→S1 が定義されている。"""
        assert "S3→S1" in FUNCTORS["mp"].morphism_map
