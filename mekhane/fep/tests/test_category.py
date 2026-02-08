# PROOF: [L2/テスト] <- mekhane/fep/tests/
"""
PROOF: [L2/テスト] このファイルは存在しなければならない

A0 → category.py の型と関数は正しく動作する必要がある
   → 24定理/射の合成/Cone構築/随伴Driftを検証
   → test_category.py が担う

Q.E.D.
"""

import pytest
from mekhane.fep.category import (
    FUNCTORS,
    MORPHISMS,
    NATURAL_TRANSFORMATIONS,
    THEOREMS,
    Adjunction,
    Cone,
    ConeProjection,
    Functor,
    Monad,
    Morphism,
    NaturalTransformation,
    Series,
    Theorem,
    build_cone,
    hom_set,
    hom_sources,
)
from mekhane.fep.cone_builder import (
    compute_dispersion,
    compute_pw_table,
    converge,
    describe_cone,
    is_uniform_pw,
    normalize_pw,
    resolve_method,
)


# =============================================================================
# Theorem Tests
# =============================================================================


class TestTheorem:
    """Theorem (Cog の対象) の検証"""

    # PURPOSE: 全24定理が定義されていること
    def test_all_24_theorems_defined(self):
        assert len(THEOREMS) == 24

    # PURPOSE: 各 Series に4定理ずつ
    @pytest.mark.parametrize("series", list(Series))
    def test_four_per_series(self, series: Series):
        count = sum(1 for t in THEOREMS.values() if t.series == series)
        assert count == 4, f"{series.name}: expected 4, got {count}"

    # PURPOSE: theorem id が正規形 (1文字 + 数字)
    def test_theorem_id_format(self):
        for tid, thm in THEOREMS.items():
            assert tid == thm.id
            assert len(tid) == 2
            assert tid[0] in "OSHPKA"
            assert tid[1] in "1234"

    # PURPOSE: series_index が 1-4
    def test_series_index(self):
        for thm in THEOREMS.values():
            assert 1 <= thm.series_index <= 4

    # PURPOSE: frozen=True が保証されていること
    def test_theorem_is_frozen(self):
        with pytest.raises(AttributeError):
            THEOREMS["O1"].name = "changed"  # type: ignore


# =============================================================================
# Morphism Tests
# =============================================================================


class TestMorphism:
    """Morphism (Cog の射 / X-series) の検証"""

    # PURPOSE: 射の合成が正しく動作すること
    def test_composition(self):
        f = Morphism("X-OS1", "O1", "S1", 0.9)
        g = Morphism("X-SH1", "S1", "H1", 0.8)
        h = f.compose(g)
        assert h is not None
        assert h.source == "O1"
        assert h.target == "H1"
        assert abs(h.strength - 0.72) < 1e-6

    # PURPOSE: 合成不可の場合 None を返すこと
    def test_non_composable(self):
        f = Morphism("X-OS1", "O1", "S1")
        g = Morphism("X-HA1", "H1", "A1")
        assert f.compose(g) is None

    # PURPOSE: 恒等射の判定
    def test_identity(self):
        id_o1 = Morphism("id_O1", "O1", "O1")
        assert id_o1.is_identity is True

        f = Morphism("X-OS1", "O1", "S1")
        assert f.is_identity is False

    # PURPOSE: 恒等射との合成 = 元の射
    def test_identity_composition(self):
        f = Morphism("X-OS1", "O1", "S1", 0.9)
        id_o1 = Morphism("id_O1", "O1", "O1", 1.0)
        id_s1 = Morphism("id_S1", "S1", "S1", 1.0)

        # id ∘ f = f
        left = id_o1.compose(f)
        assert left is not None
        assert left.target == "S1"
        assert abs(left.strength - 0.9) < 1e-6

        # f ∘ id = f
        right = f.compose(id_s1)
        assert right is not None
        assert right.source == "O1"
        assert abs(right.strength - 0.9) < 1e-6


# =============================================================================
# Cone Tests
# =============================================================================


class TestCone:
    """Cone (@converge 構造) の検証"""

    # PURPOSE: build_cone が正しく 4 projection 生成すること
    def test_build_cone_projections(self):
        outputs = {
            "O1": "深い認識",
            "O2": "強い意志",
            "O3": "鋭い問い",
            "O4": "確実な行動",
        }
        cone = build_cone(Series.O, outputs)
        assert len(cone.projections) == 4
        assert cone.projections[0].theorem_id == "O1"
        assert cone.projections[0].output == "深い認識"
        assert cone.projections[0].hom_label == "認識の射"

    # PURPOSE: 全 Series の hom_label が正しいこと
    @pytest.mark.parametrize("series", list(Series))
    def test_build_cone_all_series(self, series: Series):
        cone = build_cone(series, {})
        assert len(cone.projections) == 4
        # hom_label は空でないこと
        for proj in cone.projections:
            assert proj.hom_label != ""

    # PURPOSE: is_consistent の閾値判定
    def test_consistency_threshold(self):
        cone = Cone(series=Series.O, projections=[], dispersion=0.05)
        assert cone.is_consistent is True
        assert cone.needs_devil is False

        cone.dispersion = 0.15
        assert cone.is_consistent is False
        assert cone.needs_devil is False

        cone.dispersion = 0.35
        assert cone.is_consistent is False
        assert cone.needs_devil is True


# =============================================================================
# Adjunction Tests
# =============================================================================


class TestAdjunction:
    """Adjunction (L⊣R = /boot⊣/bye) の検証"""

    # PURPOSE: Drift = 1 - ε
    def test_drift_formula(self):
        adj = Adjunction(epsilon_precision=0.85)
        assert abs(adj.drift - 0.15) < 1e-6

    # PURPOSE: 完全復元時 drift = 0
    def test_perfect_restoration(self):
        adj = Adjunction(epsilon_precision=1.0)
        assert adj.drift == 0.0

    # PURPOSE: faithful 判定 (η > 0.8)
    def test_faithful(self):
        assert Adjunction(eta_quality=0.9).is_faithful is True
        assert Adjunction(eta_quality=0.7).is_faithful is False
        assert Adjunction(eta_quality=0.8).is_faithful is False  # boundary


# =============================================================================
# Monad Tests
# =============================================================================


class TestMonad:
    """Monad (T:Cog→Cog = /zet) の検証"""

    # PURPOSE: unit (η) が問いを生成すること
    def test_unit(self):
        m = Monad()
        qs = m.unit("FEP")
        assert len(qs) > 0
        assert "FEP" in qs[0]

    # PURPOSE: join (μ) が平坦化すること
    def test_join_flattens(self):
        m = Monad()
        nested = [["Q1", "Q2"], ["Q3"]]
        flat = m.join(nested)
        assert flat == ["Q1", "Q2", "Q3"]

    # PURPOSE: join の空入力
    def test_join_empty(self):
        m = Monad()
        assert m.join([]) == []
        assert m.join([[]]) == []


# =============================================================================
# Yoneda (hom_set) Tests
# =============================================================================


class TestYoneda:
    """hom_set (Yoneda 表現) の検証"""

    # PURPOSE: 72 morphisms total
    def test_total_morphisms(self):
        assert len(MORPHISMS) == 72

    # PURPOSE: 9 groups × 8 morphisms each
    def test_morphism_groups(self):
        groups = {"OS", "OH", "SH", "SP", "SK", "PK", "HA", "HK", "KA"}
        for g in groups:
            count = sum(1 for mid in MORPHISMS if mid.startswith(f"X-{g}"))
            assert count == 8, f"X-{g}: expected 8, got {count}"

    # PURPOSE: Hom(-, S1) = {X-OS1, X-OS3} (O1→S1, O2→S1)
    def test_hom_s1(self):
        hom = hom_set("S1")
        assert "X-OS1" in hom  # O1 → S1
        assert "X-OS3" in hom  # O2 → S1

    # PURPOSE: hom_sources returns source theorem IDs
    def test_hom_sources_s1(self):
        sources = hom_sources("S1")
        assert "O1" in sources
        assert "O2" in sources

    # PURPOSE: Hom(-, O1) は空 (O-series は最初)
    def test_hom_o1_empty(self):
        hom = hom_set("O1")
        assert len(hom) == 0

    # PURPOSE: A-series has most incoming morphisms (from H, K, and potentially others)
    def test_a_series_richest_hom_set(self):
        for i in range(1, 5):
            hom = hom_set(f"A{i}")
            assert len(hom) > 0, f"A{i} should have incoming morphisms"

    # PURPOSE: frozenset を返すこと (immutable)
    def test_returns_frozenset(self):
        hom = hom_set("H1")
        assert isinstance(hom, frozenset)


# =============================================================================
# Precision Weighting (PW) Tests
# =============================================================================


class TestPrecisionWeighting:
    """C0: Precision Weighting の検証"""

    _outputs = {
        "O1": "認識", "O2": "意志", "O3": "問い", "O4": "行動",
    }

    # PURPOSE: normalize_pw: pw=0 → weight=1.0
    def test_normalize_neutral(self):
        w = normalize_pw(self._outputs)
        assert all(abs(v - 1.0) < 1e-9 for v in w.values())

    # PURPOSE: normalize_pw: pw=+1 → weight=2.0
    def test_normalize_emphasize(self):
        w = normalize_pw(self._outputs, {"O1": 1.0})
        assert abs(w["O1"] - 2.0) < 1e-9
        assert abs(w["O2"] - 1.0) < 1e-9

    # PURPOSE: normalize_pw: pw=-1 → weight=0.0
    def test_normalize_suppress(self):
        w = normalize_pw(self._outputs, {"O3": -1.0})
        assert abs(w["O3"] - 0.0) < 1e-9

    # PURPOSE: normalize_pw: 値は [-1, +1] にクランプされる
    def test_normalize_clamp(self):
        w = normalize_pw(self._outputs, {"O1": 5.0, "O2": -3.0})
        assert abs(w["O1"] - 2.0) < 1e-9  # clamped to +1 → 2.0
        assert abs(w["O2"] - 0.0) < 1e-9  # clamped to -1 → 0.0

    # PURPOSE: is_uniform_pw: None or empty = uniform
    def test_uniform_none(self):
        assert is_uniform_pw(None) is True
        assert is_uniform_pw({}) is True

    # PURPOSE: is_uniform_pw: all-zero = uniform
    def test_uniform_all_zero(self):
        assert is_uniform_pw({"O1": 0.0, "O2": 0.0}) is True

    # PURPOSE: is_uniform_pw: non-zero = not uniform
    def test_non_uniform(self):
        assert is_uniform_pw({"O1": 0.5}) is False

    # PURPOSE: resolve_method: low V + pw≠0 → pw_weighted (not simple)
    def test_resolve_pw_forces_weighted(self):
        assert resolve_method(0.05) == "simple"
        assert resolve_method(0.05, {"O1": 0.5}) == "pw_weighted"

    # PURPOSE: resolve_method: high V → root regardless of pw
    def test_resolve_high_v_is_root(self):
        assert resolve_method(0.5) == "root"
        assert resolve_method(0.5, {"O1": 1.0}) == "root"

    # PURPOSE: converge() with pw stores weights in Cone
    def test_converge_stores_pw(self):
        cone = converge(Series.O, self._outputs, pw={"O1": 0.8, "O3": -0.5})
        assert abs(cone.pw["O1"] - 0.8) < 1e-9
        assert abs(cone.pw["O3"] - (-0.5)) < 1e-9

    # PURPOSE: converge() without pw → uniform (all zero or empty)
    def test_converge_no_pw(self):
        cone = converge(Series.O, self._outputs)
        assert is_uniform_pw(cone.pw)

    # PURPOSE: compute_pw_table returns correct structure
    def test_pw_table_structure(self):
        table = compute_pw_table(self._outputs, {"O1": 1.0})
        assert len(table) == 4
        o1_row = next(r for r in table if r["theorem_id"] == "O1")
        assert abs(o1_row["pw_raw"] - 1.0) < 1e-9
        assert abs(o1_row["weight"] - 2.0) < 1e-9
        assert o1_row["weight_pct"] > 25.0  # more than uniform share

    # PURPOSE: describe_cone shows PW section when non-uniform
    def test_describe_with_pw(self):
        cone = converge(Series.O, self._outputs, pw={"O1": 1.0})
        desc = describe_cone(cone)
        assert "Precision Weighting" in desc
        assert "+1.0" in desc

    # PURPOSE: describe_cone hides PW section when uniform
    def test_describe_without_pw(self):
        cone = converge(Series.O, self._outputs)
        desc = describe_cone(cone)
        assert "Precision Weighting" not in desc


# =============================================================================
# Functor Tests
# =============================================================================


class TestFunctor:
    """Functor (関手: 圏→圏) の検証"""

    # PURPOSE: /eat functor maps external content to Cog objects
    def test_eat_functor(self):
        eat = Functor(
            name="eat",
            source_cat="Ext",
            target_cat="Cog",
            object_map={"paper": "O1", "tutorial": "S2"},
            morphism_map={"ref": "X-OS1"},
        )
        assert eat.map_object("paper") == "O1"
        assert eat.map_object("unknown") is None
        assert eat.map_morphism("ref") == "X-OS1"

    # PURPOSE: endofunctor has same source and target
    def test_endofunctor(self):
        zet = Functor(
            name="zet",
            source_cat="Cog",
            target_cat="Cog",
            is_endofunctor=True,
        )
        assert zet.is_endofunctor is True

    # PURPOSE: is_faithful — injective on morphisms
    def test_faithful(self):
        f = Functor(
            name="test",
            source_cat="A",
            target_cat="B",
            morphism_map={"f1": "g1", "f2": "g2"},
        )
        assert f.is_faithful is True

        # Non-faithful: two morphisms map to same target
        g = Functor(
            name="test",
            source_cat="A",
            target_cat="B",
            morphism_map={"f1": "g1", "f2": "g1"},
        )
        assert g.is_faithful is False

    # PURPOSE: empty morphism map is vacuously faithful
    def test_empty_faithful(self):
        f = Functor(name="empty", source_cat="A", target_cat="B")
        assert f.is_faithful is True


# =============================================================================
# Natural Transformation Tests
# =============================================================================


class TestNaturalTransformation:
    """NaturalTransformation (自然変換: F⇒G) の検証"""

    # PURPOSE: basic component access
    def test_component_at(self):
        alpha = NaturalTransformation(
            name="η",
            source_functor="Id",
            target_functor="RL",
            components={"O1": "restore_O1", "O2": "restore_O2"},
        )
        assert alpha.component_at("O1") == "restore_O1"
        assert alpha.component_at("O3") is None

    # PURPOSE: vertical composition β∘α
    def test_vertical_composition(self):
        alpha = NaturalTransformation(
            name="α",
            source_functor="F",
            target_functor="G",
            components={"X": "α_X", "Y": "α_Y"},
        )
        beta = NaturalTransformation(
            name="β",
            source_functor="G",
            target_functor="H",
            components={"X": "β_X", "Y": "β_Y"},
        )
        composed = alpha.compose(beta)
        assert composed is not None
        assert composed.name == "β∘α"
        assert composed.source_functor == "F"
        assert composed.target_functor == "H"
        assert composed.components["X"] == "β_X∘α_X"

    # PURPOSE: non-composable natural transformations
    def test_non_composable(self):
        alpha = NaturalTransformation(
            name="α", source_functor="F", target_functor="G",
            components={"X": "a"},
        )
        gamma = NaturalTransformation(
            name="γ", source_functor="H", target_functor="K",
            components={"X": "g"},
        )
        assert alpha.compose(gamma) is None

    # PURPOSE: natural isomorphism (all components non-empty)
    def test_natural_isomorphism(self):
        iso = NaturalTransformation(
            name="η",
            source_functor="F",
            target_functor="G",
            components={"X": "η_X", "Y": "η_Y"},
        )
        assert iso.is_natural_isomorphism is True

        # Empty component = not an isomorphism
        non_iso = NaturalTransformation(
            name="α",
            source_functor="F",
            target_functor="G",
            components={"X": "α_X", "Y": ""},
        )
        assert non_iso.is_natural_isomorphism is False

    # PURPOSE: empty components = not isomorphism
    def test_empty_not_isomorphism(self):
        empty = NaturalTransformation(
            name="ε", source_functor="F", target_functor="G",
        )
        assert empty.is_natural_isomorphism is False


# =============================================================================
# Registry Tests (FUNCTORS / NATURAL_TRANSFORMATIONS)
# =============================================================================


class TestFunctorRegistry:
    """FUNCTORS レジストリの検証"""

    # PURPOSE: 4 concrete functors defined
    def test_registry_count(self):
        assert len(FUNCTORS) == 4
        assert set(FUNCTORS.keys()) == {"boot", "bye", "zet", "eat"}

    # PURPOSE: boot ⊣ bye adjunction consistency
    def test_boot_bye_adjunction(self):
        boot = FUNCTORS["boot"]
        bye = FUNCTORS["bye"]
        assert boot.source_cat == bye.target_cat  # Mem
        assert boot.target_cat == bye.source_cat  # Ses

    # PURPOSE: boot maps mem objects to session objects
    def test_boot_maps(self):
        boot = FUNCTORS["boot"]
        assert boot.map_object("handoff") == "session_context"
        assert boot.map_object("ki") == "knowledge_items"

    # PURPOSE: bye is inverse direction of boot
    def test_bye_inverse(self):
        boot = FUNCTORS["boot"]
        bye = FUNCTORS["bye"]
        # Every boot target should be a bye source
        for src, tgt in boot.object_map.items():
            assert bye.map_object(tgt) == src

    # PURPOSE: zet is an endofunctor
    def test_zet_endofunctor(self):
        zet = FUNCTORS["zet"]
        assert zet.is_endofunctor is True
        assert zet.source_cat == zet.target_cat == "Cog"

    # PURPOSE: eat maps external content to Cog theorems
    def test_eat_targets_are_theorems(self):
        eat = FUNCTORS["eat"]
        for tgt in eat.object_map.values():
            assert tgt in THEOREMS

    # PURPOSE: all functors are faithful (injective on morphisms)
    def test_all_faithful(self):
        for name, f in FUNCTORS.items():
            assert f.is_faithful is True, f"{name} is not faithful"


class TestNaturalTransformationRegistry:
    """NATURAL_TRANSFORMATIONS レジストリの検証"""

    # PURPOSE: η and ε defined
    def test_registry_count(self):
        assert len(NATURAL_TRANSFORMATIONS) == 2
        assert set(NATURAL_TRANSFORMATIONS.keys()) == {"eta", "epsilon"}

    # PURPOSE: η and ε form adjunction pair
    def test_adjunction_pair(self):
        eta = NATURAL_TRANSFORMATIONS["eta"]
        eps = NATURAL_TRANSFORMATIONS["epsilon"]
        # η: Id_Mem ⇒ R∘L, ε: L∘R ⇒ Id_Ses
        assert eta.source_functor == "Id_Mem"
        assert eps.target_functor == "Id_Ses"

    # PURPOSE: both are natural isomorphisms (all components non-empty)
    def test_both_are_isomorphisms(self):
        for name, nt in NATURAL_TRANSFORMATIONS.items():
            assert nt.is_natural_isomorphism is True, f"{name} not an isomorphism"

    # PURPOSE: η components match boot object map domain
    def test_eta_components_match_boot(self):
        eta = NATURAL_TRANSFORMATIONS["eta"]
        boot = FUNCTORS["boot"]
        assert set(eta.components.keys()) == set(boot.object_map.keys())


# =============================================================================
# /dia+ Fix Tests
# =============================================================================


class TestDiaPlusFix2ParsePw:
    """Fix #2: _parse_pw() ValueError 防御"""

    def test_valid_pw(self):
        from mekhane.fep.cone_builder import _parse_pw
        result = _parse_pw("O1:0.5,O3:-0.5")
        assert result == {"O1": 0.5, "O3": -0.5}

    def test_invalid_value_skipped(self):
        from mekhane.fep.cone_builder import _parse_pw
        result = _parse_pw("O1:abc,O3:0.5")
        assert result == {"O3": 0.5}  # O1 skipped

    def test_empty_string(self):
        from mekhane.fep.cone_builder import _parse_pw
        assert _parse_pw("") == {}

    def test_mixed_valid_invalid(self):
        from mekhane.fep.cone_builder import _parse_pw
        result = _parse_pw("O1:1.0, O2:, O3:0.5")
        assert "O1" in result
        assert "O3" in result
        assert "O2" not in result  # empty value → ValueError


class TestDiaPlusFix3ComposeStrict:
    """Fix #3: NatTrans compose() 部分合成 warning + strict mode"""

    def _make_alpha(self):
        return NaturalTransformation(
            name="α", source_functor="F", target_functor="G",
            components={"X": "α_X", "Y": "α_Y"},
        )

    def _make_beta_partial(self):
        """β has X and Z but not Y"""
        return NaturalTransformation(
            name="β", source_functor="G", target_functor="H",
            components={"X": "β_X", "Z": "β_Z"},
        )

    def _make_beta_full(self):
        """β has X and Y (matching α)"""
        return NaturalTransformation(
            name="β", source_functor="G", target_functor="H",
            components={"X": "β_X", "Y": "β_Y"},
        )

    def test_strict_raises_on_mismatch(self):
        alpha = self._make_alpha()
        beta = self._make_beta_partial()
        with pytest.raises(ValueError, match="Object mismatch"):
            alpha.compose(beta, strict=True)

    def test_nonstrict_warns_on_mismatch(self):
        import warnings
        alpha = self._make_alpha()
        beta = self._make_beta_partial()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = alpha.compose(beta)
            assert result is not None
            assert len(w) == 1
            assert "Partial composition" in str(w[0].message)

    def test_full_match_no_warning(self):
        import warnings
        alpha = self._make_alpha()
        beta = self._make_beta_full()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = alpha.compose(beta)
            assert result is not None
            assert len(w) == 0
            assert set(result.components.keys()) == {"X", "Y"}

    def test_strict_ok_with_full_match(self):
        alpha = self._make_alpha()
        beta = self._make_beta_full()
        result = alpha.compose(beta, strict=True)
        assert result is not None
        assert result.name == "β∘α"


class TestDiaPlusFix4IsFull:
    """Fix #4: Functor.is_full → NotImplementedError"""

    def test_is_full_raises(self):
        f = Functor(name="test", source_cat="C", target_cat="D")
        with pytest.raises(NotImplementedError, match="full category knowledge"):
            _ = f.is_full

    def test_registry_is_full_raises(self):
        for name, f in FUNCTORS.items():
            with pytest.raises(NotImplementedError):
                _ = f.is_full


# =============================================================================
# Functor Composition Tests
# =============================================================================


class TestFunctorCompose:
    """Functor.compose() の検証"""

    # PURPOSE: bye∘boot: Mem → Mem (round-trip via session)
    def test_bye_compose_boot(self):
        boot = FUNCTORS["boot"]
        bye = FUNCTORS["bye"]
        # F=boot, G=bye → G∘F = bye∘boot: Mem → Mem
        composed = boot.compose(bye)
        assert composed.name == "bye∘boot"
        assert composed.source_cat == "Mem"
        assert composed.target_cat == "Mem"
        assert composed.is_endofunctor is True

    # PURPOSE: bye∘boot maps handoff → handoff (identity on objects)
    def test_bye_boot_identity(self):
        boot = FUNCTORS["boot"]
        bye = FUNCTORS["bye"]
        composed = boot.compose(bye)
        # handoff → session_context → handoff
        assert composed.map_object("handoff") == "handoff"
        assert composed.map_object("ki") == "ki"

    # PURPOSE: boot∘bye: Ses → Ses (session round-trip)
    def test_boot_compose_bye(self):
        boot = FUNCTORS["boot"]
        bye = FUNCTORS["bye"]
        composed = bye.compose(boot)
        assert composed.name == "boot∘bye"
        assert composed.source_cat == "Ses"
        assert composed.target_cat == "Ses"
        assert composed.is_endofunctor is True

    # PURPOSE: incompatible functors → ValueError
    def test_incompatible_raises(self):
        boot = FUNCTORS["boot"]
        eat = FUNCTORS["eat"]
        with pytest.raises(ValueError, match="Cannot compose"):
            boot.compose(eat)  # boot: Mem→Ses, eat: Ext→Cog

    # PURPOSE: compose preserves morphism map
    def test_morphism_compose(self):
        boot = FUNCTORS["boot"]
        bye = FUNCTORS["bye"]
        composed = boot.compose(bye)
        # restore → expand → compress → ...
        # Morphism composition tracks through both maps
        assert composed.is_faithful is True


# =============================================================================
# Cone Consumer Tests
# =============================================================================


class TestConeConsumer:
    """cone_consumer.advise() の検証"""

    def _make_cone(self, series=Series.O, dispersion=0.0,
                   confidence=80.0, is_universal=True,
                   resolution_method="simple", pw=None):
        cone = build_cone(series, {
            f"{series.name}1": "出力1",
            f"{series.name}2": "出力2",
            f"{series.name}3": "出力3",
            f"{series.name}4": "出力4",
        })
        cone.dispersion = dispersion
        cone.confidence = confidence
        cone.is_universal = is_universal
        cone.resolution_method = resolution_method
        cone.pw = pw or {}
        return cone

    # PURPOSE: is_universal → proceed
    def test_universal_proceed(self):
        from mekhane.fep.cone_consumer import advise
        cone = self._make_cone(dispersion=0.05, confidence=85.0, is_universal=True)
        advice = advise(cone)
        assert advice.action == "proceed"
        assert advice.urgency == 0.0
        assert "Limit" in advice.reason

    # PURPOSE: needs_devil (V > 0.3) → devil
    def test_high_dispersion_devil(self):
        from mekhane.fep.cone_consumer import advise
        cone = self._make_cone(dispersion=0.5, confidence=40.0, is_universal=False)
        advice = advise(cone)
        assert advice.action == "devil"
        assert advice.suggested_wf == "/dia devil"
        assert advice.urgency >= 0.5

    # PURPOSE: S-series + V > 0.2 → devil (strategy risk)
    def test_s_series_risk(self):
        from mekhane.fep.cone_consumer import advise
        cone = self._make_cone(series=Series.S, dispersion=0.25,
                               confidence=60.0, is_universal=False)
        advice = advise(cone)
        assert advice.action == "devil"
        assert "戦略" in advice.reason

    # PURPOSE: low confidence + moderate V → investigate
    def test_low_confidence_investigate(self):
        from mekhane.fep.cone_consumer import advise
        cone = self._make_cone(dispersion=0.15, confidence=40.0, is_universal=False)
        advice = advise(cone)
        assert advice.action == "investigate"
        assert advice.suggested_wf in ("/zet", "/sop")

    # PURPOSE: K-series investigate → /sop
    def test_k_series_investigate_sop(self):
        from mekhane.fep.cone_consumer import advise
        cone = self._make_cone(series=Series.K, dispersion=0.15,
                               confidence=40.0, is_universal=False)
        advice = advise(cone)
        assert advice.suggested_wf == "/sop"

    # PURPOSE: extreme PW → reweight
    def test_extreme_pw_reweight(self):
        from mekhane.fep.cone_consumer import advise
        cone = self._make_cone(
            dispersion=0.05, confidence=75.0, is_universal=False,
            resolution_method="pw_weighted",
            pw={"O1": 0.9, "O2": 0.0, "O3": -0.8, "O4": 0.0},
        )
        advice = advise(cone)
        assert advice.action == "reweight"
        assert advice.suggested_wf == "/dia epo"

    # PURPOSE: default → proceed (moderate dispersion)
    def test_default_proceed(self):
        from mekhane.fep.cone_consumer import advise
        cone = self._make_cone(dispersion=0.08, confidence=65.0, is_universal=False)
        advice = advise(cone)
        assert advice.action == "proceed"
        assert advice.urgency < 0.5


# =============================================================================
# Japanese Dispersion Tests (Creator's bigram Jaccard ensemble)
# =============================================================================


class TestJapaneseDispersion:
    """Creator の bigram Jaccard ensemble が日本語で正しく動作するか検証"""

    # PURPOSE: _char_bigrams basic behavior
    def test_char_bigrams_basic(self):
        from mekhane.fep.cone_builder import _char_bigrams
        result = _char_bigrams("認識")
        assert result == ["認識"]

    def test_char_bigrams_longer(self):
        from mekhane.fep.cone_builder import _char_bigrams
        result = _char_bigrams("深い認識")
        assert len(result) == 3  # 深い, い認, 認識

    def test_char_bigrams_whitespace(self):
        from mekhane.fep.cone_builder import _char_bigrams
        result = _char_bigrams("深い 認識")
        assert result == ["深い", "い認", "認識"]  # whitespace removed

    # PURPOSE: 同義的日本語出力 → V < 0.7 (ensemble で改善)
    # NOTE: pure SequenceMatcher gives ~0.8+ for Japanese, ensemble brings to ~0.58
    def test_synonymous_japanese_low_dispersion(self):
        from mekhane.fep.cone_builder import compute_dispersion
        outputs = {
            "O1": "認識は意識の基盤であり、思考の出発点となる",
            "O2": "認識こそが意識の土台であり、思考の起点となるものだ",
            "O3": "意識の基盤は認識であって、思考はそこから始まる",
            "O4": "思考の出発は認識にあり、それが意識を形作る基盤だ",
        }
        v = compute_dispersion(outputs)
        assert v < 0.7, f"Synonymous Japanese V={v:.3f} should be < 0.7"

    # PURPOSE: 矛盾する日本語出力 → V > 0.3
    def test_contradictory_japanese_high_dispersion(self):
        from mekhane.fep.cone_builder import compute_dispersion
        outputs = {
            "O1": "実行すべきだ。リスクは低い",
            "O2": "中止すべきだ。リスクが高すぎる",
            "O3": "賛成。進めるべき状況だ",
            "O4": "反対。止めるべき状況だ",
        }
        v = compute_dispersion(outputs)
        assert v > 0.3, f"Contradictory Japanese V={v:.3f} should be > 0.3"

    # PURPOSE: 完全に同じ出力 → V = 0.0
    def test_identical_japanese_zero(self):
        from mekhane.fep.cone_builder import compute_dispersion
        same = "同じ認識に到達した"
        outputs = {"O1": same, "O2": same, "O3": same, "O4": same}
        assert compute_dispersion(outputs) == 0.0

