# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要
"""
Tests for Phase D modules: Zētēsis, Schema, Doxa, Sophia, Krisis
"""

import pytest
from mekhane.fep.zetesis_inquirer import (
    ZetesisDerivative, QuestionType, ZetesisResult,
    inquire, format_zetesis_markdown, encode_zetesis_observation,
)
from mekhane.fep.schema_analyzer import (
    MetronDerivative, ScaleLevel, MetronResult,
    StathmosDerivative, CriterionPriority, StathmosResult,
    PraxisDerivative, PraxisResult,
    analyze_scale, define_criteria, plan_praxis,
    format_metron_markdown, format_stathmos_markdown, format_praxis_markdown,
    encode_schema_observation,
)
from mekhane.fep.doxa_persistence import (
    DoxaDerivative, BeliefStrength, Belief, DoxaResult, DoxaStore,
    get_store, format_doxa_markdown, encode_doxa_observation,
)
from mekhane.fep.sophia_researcher import (
    SophiaDerivative, ResearchDepth, ResearchQuery, SophiaResult,
    research, format_sophia_markdown, encode_sophia_observation,
)
from mekhane.fep.krisis_judge import (
    KrisisDerivative, VerdictType, Objection, KrisisResult,
    judge, epochē, format_krisis_markdown, encode_krisis_observation,
)


# =============================================================================
# O3 Zētēsis Tests
# =============================================================================

class TestZetesis:
    """O3 Zētēsis tests"""
    
    def test_inquire_default(self):
        result = inquire("テスト対象")
        assert result.topic == "テスト対象"
        assert len(result.generated_questions) > 0
    
    def test_inquire_deep_derivative(self):
        result = inquire("なぜこの問題が起きるのか")
        assert result.derivative == ZetesisDerivative.DEEP
    
    def test_inquire_wide_derivative(self):
        result = inquire("他の代替案を探す")
        assert result.derivative == ZetesisDerivative.WIDE
    
    def test_inquire_pivot_derivative(self):
        result = inquire("前提を疑う")
        assert result.derivative == ZetesisDerivative.PIVOT
    
    def test_question_count(self):
        result = inquire("topic", depth=5)
        assert result.question_count >= 3
    
    def test_format_zetesis_markdown(self):
        result = inquire("テスト")
        md = format_zetesis_markdown(result)
        assert "O3 Zētēsis" in md
    
    def test_encode_zetesis_observation(self):
        result = inquire("test")
        obs = encode_zetesis_observation(result)
        assert "confidence" in obs


# =============================================================================
# S1 Metron Tests
# =============================================================================

class TestMetron:
    """S1 Metron tests"""
    
    def test_analyze_scale_default(self):
        result = analyze_scale("テスト対象")
        assert result.subject == "テスト対象"
    
    def test_analyze_scale_macro(self):
        result = analyze_scale("システム全体の設計")
        assert result.scale == ScaleLevel.MACRO
    
    def test_analyze_scale_continuous(self):
        result = analyze_scale("連続的なデータフロー")
        assert result.derivative == MetronDerivative.CONTINUOUS
    
    def test_format_metron_markdown(self):
        result = analyze_scale("test")
        md = format_metron_markdown(result)
        assert "S1 Metron" in md


# =============================================================================
# S3 Stathmos Tests
# =============================================================================

class TestStathmos:
    """S3 Stathmos tests"""
    
    def test_define_criteria_default(self):
        result = define_criteria("評価対象")
        assert result.subject == "評価対象"
    
    def test_define_criteria_with_must(self):
        result = define_criteria("test", must=["A", "B"])
        assert len(result.criteria[CriterionPriority.MUST]) == 2
    
    def test_define_criteria_normative(self):
        result = define_criteria("ルールに従った評価")
        assert result.derivative == StathmosDerivative.NORMATIVE
    
    def test_format_stathmos_markdown(self):
        result = define_criteria("test", must=["criterion1"])
        md = format_stathmos_markdown(result)
        assert "S3 Stathmos" in md


# =============================================================================
# S4 Praxis Tests
# =============================================================================

class TestPraxis:
    """S4 Praxis tests"""
    
    def test_plan_praxis_default(self):
        result = plan_praxis("タスク実行")
        assert result.action == "タスク実行"
    
    def test_plan_praxis_intrinsic(self):
        result = plan_praxis("学習と成長")
        assert result.derivative == PraxisDerivative.PRAXIS
        assert result.intrinsic_value is True
    
    def test_plan_praxis_poiesis(self):
        result = plan_praxis("ドキュメント作成")
        assert result.derivative == PraxisDerivative.POIESIS
        assert result.intrinsic_value is False
    
    def test_format_praxis_markdown(self):
        result = plan_praxis("test")
        md = format_praxis_markdown(result)
        assert "S4 Praxis" in md


class TestSchemaObservation:
    """encode_schema_observation tests"""
    
    def test_encode_with_metron(self):
        metron = analyze_scale("test")
        obs = encode_schema_observation(metron=metron)
        assert "context_clarity" in obs


# =============================================================================
# H4 Doxa Tests
# =============================================================================

class TestDoxaStore:
    """H4 Doxa tests"""
    
    def test_persist_belief(self):
        store = DoxaStore()
        result = store.persist("テスト信念", confidence=0.8)
        assert result.success is True
        assert result.derivative == DoxaDerivative.PERSIST
    
    def test_evolve_belief(self):
        store = DoxaStore()
        store.persist("信念", confidence=0.5)
        result = store.evolve("信念", new_confidence=0.9)
        assert result.success is True
        assert result.belief.confidence == 0.9
    
    def test_archive_belief(self):
        store = DoxaStore()
        store.persist("アーカイブ対象")
        result = store.archive("アーカイブ対象")
        assert result.success is True
        assert store.get("アーカイブ対象") is None
        assert len(store.list_archived()) == 1
    
    def test_format_doxa_markdown(self):
        store = DoxaStore()
        result = store.persist("test")
        md = format_doxa_markdown(result)
        assert "H4 Doxa" in md
    
    def test_encode_doxa_observation(self):
        store = DoxaStore()
        result = store.persist("test")
        obs = encode_doxa_observation(result)
        assert "confidence" in obs


# =============================================================================
# K4 Sophia Tests
# =============================================================================

class TestSophia:
    """K4 Sophia tests"""
    
    def test_research_default(self):
        result = research("テストトピック")
        assert result.topic == "テストトピック"
        assert len(result.query.questions) > 0
    
    def test_research_academic(self):
        result = research("論文調査")
        assert result.derivative == SophiaDerivative.ACADEMIC
        assert "arXiv" in result.query.sources
    
    def test_research_technical(self):
        result = research("API実装方法")
        assert result.derivative == SophiaDerivative.TECHNICAL
    
    def test_research_deep_depth(self):
        result = research("topic", depth=ResearchDepth.DEEP)
        assert result.depth == ResearchDepth.DEEP
        assert result.estimated_time_minutes == 60
    
    def test_format_sophia_markdown(self):
        result = research("test")
        md = format_sophia_markdown(result)
        assert "K4 Sophia" in md
    
    def test_encode_sophia_observation(self):
        result = research("test")
        obs = encode_sophia_observation(result)
        assert "confidence" in obs


# =============================================================================
# A2 Krisis Tests
# =============================================================================

class TestKrisis:
    """A2 Krisis tests"""
    
    def test_judge_default(self):
        result = judge("判定対象")
        assert result.subject == "判定対象"
    
    def test_judge_approve(self):
        result = judge("提案", evidence_for=["A", "B", "C", "D"])
        assert result.verdict == VerdictType.APPROVE
    
    def test_judge_reject(self):
        result = judge("問題", evidence_against=["X", "Y", "Z", "W"])
        assert result.verdict in (VerdictType.REJECT, VerdictType.REVISE, VerdictType.SUSPEND)
    
    def test_judge_devil_advocate(self):
        result = judge("計画", devil_advocate=True)
        assert result.derivative == KrisisDerivative.ADVOCATE
        assert len(result.objections) > 0
    
    def test_epochē(self):
        result = epochē("不確実な判断")
        assert result.verdict == VerdictType.SUSPEND
        assert result.confidence == 0.0
    
    def test_has_critical_objection(self):
        result = judge("test", devil_advocate=True)
        # Devil's Advocate should have some objections
        assert result.objection_count > 0
    
    def test_format_krisis_markdown(self):
        result = judge("test")
        md = format_krisis_markdown(result)
        assert "A2 Krisis" in md
    
    def test_encode_krisis_observation(self):
        result = judge("test")
        obs = encode_krisis_observation(result)
        assert "confidence" in obs
