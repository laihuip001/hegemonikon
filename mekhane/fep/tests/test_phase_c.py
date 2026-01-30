# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要
"""
Tests for Phase C modules: Perigraphē, Hormē, Akribeia
"""

import pytest
from mekhane.fep.perigraphe_engine import (
    KhoraDerivative, ScopeScale, KhoraResult,
    HodosDerivative, HodosResult,
    TrokhiaDerivative, TrokhiaResult,
    define_scope, define_path, define_trajectory,
    format_khora_markdown, format_hodos_markdown, format_trokhia_markdown,
    encode_perigraphe_observation,
)
from mekhane.fep.horme_evaluator import (
    PropatheiaDerivative, PropatheiaResult,
    PistisDerivative, PistisResult,
    OrexisDerivative, OrexisResult,
    evaluate_propatheia, evaluate_pistis, evaluate_orexis,
    format_propatheia_markdown, format_pistis_markdown, format_orexis_markdown,
    encode_horme_observation,
)
from mekhane.fep.akribeia_evaluator import (
    PathosDerivative, PathosResult,
    GnomeDerivative, GnomeResult,
    EpistemeDerivative, EpistemeResult,
    evaluate_pathos, extract_gnome, evaluate_episteme,
    format_pathos_markdown, format_gnome_markdown, format_episteme_markdown,
    encode_akribeia_observation,
)


# =============================================================================
# P-series (Perigraphē) Tests
# =============================================================================

class TestKhora:
    """P1 Khōra tests"""
    
    def test_define_scope_default(self):
        result = define_scope("テスト対象")
        assert result.target == "テスト対象"
        assert result.x_scale == ScopeScale.MICRO
        assert result.y_scale == ScopeScale.MICRO
    
    def test_define_scope_relational_inference(self):
        result = define_scope("チームの関係性")
        assert result.derivative == KhoraDerivative.RELATIONAL
    
    def test_define_scope_conceptual_inference(self):
        result = define_scope("アーキテクチャ設計")
        assert result.derivative == KhoraDerivative.CONCEPTUAL
    
    def test_scope_label(self):
        result = define_scope("test", x_scale=ScopeScale.MACRO, y_scale=ScopeScale.MICRO)
        assert result.scope_label == "Macro×Micro"
    
    def test_format_khora_markdown(self):
        result = define_scope("対象")
        md = format_khora_markdown(result)
        assert "P1 Khōra" in md


class TestHodos:
    """P2 Hodos tests"""
    
    def test_define_path_direct(self):
        result = define_path("実装経路", "設計", "完了")
        assert result.derivative == HodosDerivative.DIRECT
        assert result.start == "設計"
        assert result.end == "完了"
    
    def test_define_path_with_waypoints(self):
        result = define_path("実装経路", "A", "D", waypoints=["B", "C"])
        assert result.total_nodes == 4
    
    def test_define_path_iterate(self):
        result = define_path("反復経路", "A", "A")
        assert result.derivative == HodosDerivative.ITERATE
    
    def test_format_hodos_markdown(self):
        result = define_path("経路", "開始", "終了")
        md = format_hodos_markdown(result)
        assert "P2 Hodos" in md


class TestTrokhia:
    """P3 Trokhia tests"""
    
    def test_define_trajectory_cycle(self):
        result = define_trajectory("開発サイクル", ["Plan", "Do", "Check", "Act"])
        assert result.derivative == TrokhiaDerivative.CYCLE
        assert len(result.phases) == 4
    
    def test_define_trajectory_spiral(self):
        result = define_trajectory("スプリント", ["設計", "実装", "レビュー"], max_iterations=5)
        assert result.derivative == TrokhiaDerivative.SPIRAL
        assert result.max_iterations == 5
    
    def test_current_phase_name(self):
        result = define_trajectory("軌道", ["A", "B", "C"])
        result.current_phase = 1
        assert result.current_phase_name == "B"
    
    def test_format_trokhia_markdown(self):
        result = define_trajectory("軌道", ["フェーズ1", "フェーズ2"])
        md = format_trokhia_markdown(result)
        assert "P3 Trokhia" in md


class TestPerigrapheObservation:
    """encode_perigraphe_observation tests"""
    
    def test_encode_with_khora(self):
        khora = define_scope("test", x_scale=ScopeScale.MICRO, y_scale=ScopeScale.MICRO)
        obs = encode_perigraphe_observation(khora=khora)
        assert obs["context_clarity"] == 0.9


# =============================================================================
# H-series (Hormē) Tests
# =============================================================================

class TestPropatheia:
    """H1 Propatheia tests"""
    
    def test_evaluate_propatheia_default(self):
        result = evaluate_propatheia("新機能の提案")
        assert result.stimulus == "新機能の提案"
    
    def test_evaluate_propatheia_warn(self):
        result = evaluate_propatheia("リスクのある変更")
        assert result.derivative == PropatheiaDerivative.WARN
        assert result.valence < 0
    
    def test_evaluate_propatheia_draw(self):
        result = evaluate_propatheia("興味深い可能性")
        assert result.derivative == PropatheiaDerivative.DRAW
        assert result.valence > 0
    
    def test_format_propatheia_markdown(self):
        result = evaluate_propatheia("刺激")
        md = format_propatheia_markdown(result)
        assert "H1 Propatheia" in md


class TestPistis:
    """H2 Pistis tests"""
    
    def test_evaluate_pistis_no_evidence(self):
        result = evaluate_pistis("仮説")
        assert result.derivative == PistisDerivative.MEDIUM
        assert result.confidence == pytest.approx(0.5)
    
    def test_evaluate_pistis_strong_evidence(self):
        result = evaluate_pistis("結論", evidence=["A", "B", "C", "D"])
        assert result.derivative == PistisDerivative.HIGH
        assert result.should_trust is True
    
    def test_evaluate_pistis_counter_evidence(self):
        result = evaluate_pistis("疑問", counter_evidence=["反証1", "反証2", "反証3"])
        assert result.derivative == PistisDerivative.LOW
        assert result.should_trust is False
    
    def test_format_pistis_markdown(self):
        result = evaluate_pistis("信念")
        md = format_pistis_markdown(result)
        assert "H2 Pistis" in md


class TestOrexis:
    """H3 Orexis tests"""
    
    def test_evaluate_orexis_approach(self):
        result = evaluate_orexis("新技術", benefits=["効率向上", "品質向上", "学習機会"])
        assert result.derivative == OrexisDerivative.APPROACH
        assert result.should_pursue is True
    
    def test_evaluate_orexis_avoid(self):
        result = evaluate_orexis("リスク", costs=["時間", "コスト", "複雑性", "リスク"])
        assert result.derivative == OrexisDerivative.AVOID
        assert result.should_pursue is False
    
    def test_evaluate_orexis_neutral(self):
        result = evaluate_orexis("オプション", benefits=["A"], costs=["B"])
        assert result.derivative == OrexisDerivative.NEUTRAL
    
    def test_format_orexis_markdown(self):
        result = evaluate_orexis("対象")
        md = format_orexis_markdown(result)
        assert "H3 Orexis" in md


class TestHormeObservation:
    """encode_horme_observation tests"""
    
    def test_encode_with_pistis(self):
        pistis = evaluate_pistis("test", evidence=["A", "B"])
        obs = encode_horme_observation(pistis=pistis)
        assert obs["confidence"] > 0.5


# =============================================================================
# A-series (Akribeia) Tests
# =============================================================================

class TestPathos:
    """A1 Pathos tests"""
    
    def test_evaluate_pathos_default(self):
        result = evaluate_pathos("日常の出来事")
        assert result.experience == "日常の出来事"
    
    def test_evaluate_pathos_somatic(self):
        result = evaluate_pathos("体の緊張を感じる")
        assert result.derivative == PathosDerivative.SOMATIC
    
    def test_evaluate_pathos_cognitive(self):
        result = evaluate_pathos("この状況について考える")
        assert result.derivative == PathosDerivative.COGNITIVE
    
    def test_evaluate_pathos_needs_regulation(self):
        result = evaluate_pathos("強い不安を感じる")
        assert result.needs_regulation is True
    
    def test_format_pathos_markdown(self):
        result = evaluate_pathos("経験")
        md = format_pathos_markdown(result)
        assert "A1 Pathos" in md


class TestGnome:
    """A3 Gnōmē tests"""
    
    def test_extract_gnome_default(self):
        result = extract_gnome("この経験から学んだこと")
        assert result.source == "この経験から学んだこと"
    
    def test_extract_gnome_universal(self):
        result = extract_gnome("常に確認すべき原則")
        assert result.derivative == GnomeDerivative.UNIVERSAL
        assert result.generalizability > 0.8
    
    def test_extract_gnome_domain(self):
        result = extract_gnome("この場合の特定のルール")
        assert result.derivative == GnomeDerivative.DOMAIN
    
    def test_format_gnome_markdown(self):
        result = extract_gnome("出所")
        md = format_gnome_markdown(result)
        assert "A3 Gnōmē" in md


class TestEpisteme:
    """A4 Epistēmē tests"""
    
    def test_evaluate_episteme_believed_only(self):
        result = evaluate_episteme("仮説")
        assert result.is_believed is True
        assert result.is_justified is False
        assert result.is_knowledge is False
    
    def test_evaluate_episteme_justified(self):
        result = evaluate_episteme("結論", justification="根拠あり")
        assert result.is_justified is True
    
    def test_evaluate_episteme_full_jtb(self):
        result = evaluate_episteme(
            "確立された知識",
            evidence=["証拠1", "証拠2", "証拠3"],
            believed=True
        )
        assert result.is_justified is True
        assert result.is_true is True
        assert result.is_believed is True
        assert result.is_knowledge is True
    
    def test_jtb_score(self):
        result = evaluate_episteme("test", evidence=["A"])
        assert 0 <= result.jtb_score <= 1
    
    def test_format_episteme_markdown(self):
        result = evaluate_episteme("命題")
        md = format_episteme_markdown(result)
        assert "A4 Epistēmē" in md


class TestAkribeiaObservation:
    """encode_akribeia_observation tests"""
    
    def test_encode_with_episteme(self):
        episteme = evaluate_episteme("test", evidence=["A", "B", "C"])
        obs = encode_akribeia_observation(episteme=episteme)
        assert obs["confidence"] == episteme.jtb_score
