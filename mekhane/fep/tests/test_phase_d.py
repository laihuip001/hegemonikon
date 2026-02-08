# PROOF: [L3/テスト] <- mekhane/fep/tests/ 対象モジュールが存在→検証が必要
"""
Tests for Phase D modules: Zētēsis, Schema, Doxa, Sophia, Krisis
"""

import pytest
from mekhane.fep.zetesis_inquirer import (
    ZetesisDerivative,
    QuestionType,
    ZetesisResult,
    inquire,
    format_zetesis_markdown,
    encode_zetesis_observation,
)
from mekhane.fep.schema_analyzer import (
    MetronDerivative,
    ScaleLevel,
    MetronResult,
    StathmosDerivative,
    CriterionPriority,
    StathmosResult,
    PraxisDerivative,
    PraxisResult,
    analyze_scale,
    define_criteria,
    plan_praxis,
    format_metron_markdown,
    format_stathmos_markdown,
    format_praxis_markdown,
    encode_schema_observation,
)
from mekhane.fep.doxa_persistence import (
    DoxaDerivative,
    BeliefStrength,
    Belief,
    DoxaResult,
    DoxaStore,
    get_store,
    format_doxa_markdown,
    encode_doxa_observation,
)
from mekhane.fep.sophia_researcher import (
    SophiaDerivative,
    ResearchDepth,
    ResearchQuery,
    SophiaResult,
    research,
    format_sophia_markdown,
    encode_sophia_observation,
)
from mekhane.fep.krisis_judge import (
    KrisisDerivative,
    VerdictType,
    Objection,
    KrisisResult,
    judge,
    epochē,
    format_krisis_markdown,
    encode_krisis_observation,
)

# =============================================================================
# O3 Zētēsis Tests
# =============================================================================


# PURPOSE: O3 Zētēsis tests
class TestZetesis:
    """O3 Zētēsis tests"""

    # PURPOSE: inquire_default をテストする
    def test_inquire_default(self):
        result = inquire("テスト対象")
        assert result.topic == "テスト対象"
        assert len(result.generated_questions) > 0

    # PURPOSE: inquire_deep_derivative をテストする
    def test_inquire_deep_derivative(self):
        result = inquire("なぜこの問題が起きるのか")
        assert result.derivative == ZetesisDerivative.DEEP

    # PURPOSE: inquire_wide_derivative をテストする
    def test_inquire_wide_derivative(self):
        result = inquire("他の代替案を探す")
        assert result.derivative == ZetesisDerivative.WIDE

    # PURPOSE: inquire_pivot_derivative をテストする
    def test_inquire_pivot_derivative(self):
        result = inquire("前提を疑う")
        assert result.derivative == ZetesisDerivative.PIVOT

    # PURPOSE: question_count をテストする
    def test_question_count(self):
        result = inquire("topic", depth=5)
        assert result.question_count >= 3

    # PURPOSE: format_zetesis_markdown をテストする
    def test_format_zetesis_markdown(self):
        result = inquire("テスト")
        md = format_zetesis_markdown(result)
        assert "O3 Zētēsis" in md

    # PURPOSE: encode_zetesis_observation をテストする
    def test_encode_zetesis_observation(self):
        result = inquire("test")
        obs = encode_zetesis_observation(result)
        assert "confidence" in obs


# =============================================================================
# S1 Metron Tests
# =============================================================================


# PURPOSE: S1 Metron tests
class TestMetron:
    """S1 Metron tests"""

    # PURPOSE: analyze_scale_default をテストする
    def test_analyze_scale_default(self):
        result = analyze_scale("テスト対象")
        assert result.subject == "テスト対象"

    # PURPOSE: analyze_scale_macro をテストする
    def test_analyze_scale_macro(self):
        result = analyze_scale("システム全体の設計")
        assert result.scale == ScaleLevel.MACRO

    # PURPOSE: analyze_scale_continuous をテストする
    def test_analyze_scale_continuous(self):
        result = analyze_scale("連続的なデータフロー")
        assert result.derivative == MetronDerivative.CONTINUOUS

    # PURPOSE: format_metron_markdown をテストする
    def test_format_metron_markdown(self):
        result = analyze_scale("test")
        md = format_metron_markdown(result)
        assert "S1 Metron" in md


# =============================================================================
# S3 Stathmos Tests
# =============================================================================


# PURPOSE: S3 Stathmos tests
class TestStathmos:
    """S3 Stathmos tests"""

    # PURPOSE: define_criteria_default をテストする
    def test_define_criteria_default(self):
        result = define_criteria("評価対象")
        assert result.subject == "評価対象"

    # PURPOSE: define_criteria_with_must をテストする
    def test_define_criteria_with_must(self):
        result = define_criteria("test", must=["A", "B"])
        assert len(result.criteria[CriterionPriority.MUST]) == 2

    # PURPOSE: define_criteria_normative をテストする
    def test_define_criteria_normative(self):
        result = define_criteria("ルールに従った評価")
        assert result.derivative == StathmosDerivative.NORMATIVE

    # PURPOSE: format_stathmos_markdown をテストする
    def test_format_stathmos_markdown(self):
        result = define_criteria("test", must=["criterion1"])
        md = format_stathmos_markdown(result)
        assert "S3 Stathmos" in md


# =============================================================================
# S4 Praxis Tests
# =============================================================================


# PURPOSE: S4 Praxis tests
class TestPraxis:
    """S4 Praxis tests"""

    # PURPOSE: plan_praxis_default をテストする
    def test_plan_praxis_default(self):
        result = plan_praxis("タスク実行")
        assert result.action == "タスク実行"

    # PURPOSE: plan_praxis_intrinsic をテストする
    def test_plan_praxis_intrinsic(self):
        result = plan_praxis("学習と成長")
        assert result.derivative == PraxisDerivative.PRAXIS
        assert result.intrinsic_value is True

    # PURPOSE: plan_praxis_poiesis をテストする
    def test_plan_praxis_poiesis(self):
        result = plan_praxis("ドキュメント作成")
        assert result.derivative == PraxisDerivative.POIESIS
        assert result.intrinsic_value is False

    # PURPOSE: format_praxis_markdown をテストする
    def test_format_praxis_markdown(self):
        result = plan_praxis("test")
        md = format_praxis_markdown(result)
        assert "S4 Praxis" in md


# PURPOSE: encode_schema_observation tests
class TestSchemaObservation:
    """encode_schema_observation tests"""

    # PURPOSE: encode_with_metron をテストする
    def test_encode_with_metron(self):
        metron = analyze_scale("test")
        obs = encode_schema_observation(metron=metron)
        assert "context_clarity" in obs


# =============================================================================
# H4 Doxa Tests
# =============================================================================


# PURPOSE: H4 Doxa tests
class TestDoxaStore:
    """H4 Doxa tests"""

    # PURPOSE: persist_belief をテストする
    def test_persist_belief(self):
        store = DoxaStore()
        result = store.persist("テスト信念", confidence=0.8)
        assert result.success is True
        assert result.derivative == DoxaDerivative.PERSIST

    # PURPOSE: evolve_belief をテストする
    def test_evolve_belief(self):
        store = DoxaStore()
        store.persist("信念", confidence=0.5)
        result = store.evolve("信念", new_confidence=0.9)
        assert result.success is True
        assert result.belief.confidence == 0.9

    # PURPOSE: archive_belief をテストする
    def test_archive_belief(self):
        store = DoxaStore()
        store.persist("アーカイブ対象")
        result = store.archive("アーカイブ対象")
        assert result.success is True
        assert store.get("アーカイブ対象") is None
        assert len(store.list_archived()) == 1

    # PURPOSE: format_doxa_markdown をテストする
    def test_format_doxa_markdown(self):
        store = DoxaStore()
        result = store.persist("test")
        md = format_doxa_markdown(result)
        assert "H4 Doxa" in md

    # PURPOSE: encode_doxa_observation をテストする
    def test_encode_doxa_observation(self):
        store = DoxaStore()
        result = store.persist("test")
        obs = encode_doxa_observation(result)
        assert "confidence" in obs


# =============================================================================
# K4 Sophia Tests
# =============================================================================


# PURPOSE: K4 Sophia tests
class TestSophia:
    """K4 Sophia tests"""

    # PURPOSE: research_default をテストする
    def test_research_default(self):
        result = research("テストトピック")
        assert result.topic == "テストトピック"
        assert len(result.query.questions) > 0

    # PURPOSE: research_academic をテストする
    def test_research_academic(self):
        result = research("論文調査")
        assert result.derivative == SophiaDerivative.ACADEMIC
        assert "arXiv" in result.query.sources

    # PURPOSE: research_technical をテストする
    def test_research_technical(self):
        result = research("API実装方法")
        assert result.derivative == SophiaDerivative.TECHNICAL

    # PURPOSE: research_deep_depth をテストする
    def test_research_deep_depth(self):
        result = research("topic", depth=ResearchDepth.DEEP)
        assert result.depth == ResearchDepth.DEEP
        assert result.estimated_time_minutes == 60

    # PURPOSE: format_sophia_markdown をテストする
    def test_format_sophia_markdown(self):
        result = research("test")
        md = format_sophia_markdown(result)
        assert "K4 Sophia" in md

    # PURPOSE: encode_sophia_observation をテストする
    def test_encode_sophia_observation(self):
        result = research("test")
        obs = encode_sophia_observation(result)
        assert "confidence" in obs


# =============================================================================
# A2 Krisis Tests
# =============================================================================


# PURPOSE: A2 Krisis tests
class TestKrisis:
    """A2 Krisis tests"""

    # PURPOSE: judge_default をテストする
    def test_judge_default(self):
        result = judge("判定対象")
        assert result.subject == "判定対象"

    # PURPOSE: judge_approve をテストする
    def test_judge_approve(self):
        result = judge("提案", evidence_for=["A", "B", "C", "D"])
        assert result.verdict == VerdictType.APPROVE

    # PURPOSE: judge_reject をテストする
    def test_judge_reject(self):
        result = judge("問題", evidence_against=["X", "Y", "Z", "W"])
        assert result.verdict in (
            VerdictType.REJECT,
            VerdictType.REVISE,
            VerdictType.SUSPEND,
        )

    # PURPOSE: judge_devil_advocate をテストする
    def test_judge_devil_advocate(self):
        result = judge("計画", devil_advocate=True)
        assert result.derivative == KrisisDerivative.ADVOCATE
        assert len(result.objections) > 0

    # PURPOSE: epochē をテストする
    def test_epochē(self):
        result = epochē("不確実な判断")
        assert result.verdict == VerdictType.SUSPEND
        assert result.confidence == 0.0

    # PURPOSE: has_critical_objection をテストする
    def test_has_critical_objection(self):
        result = judge("test", devil_advocate=True)
        # Devil's Advocate should have some objections
        assert result.objection_count > 0

    # PURPOSE: format_krisis_markdown をテストする
    def test_format_krisis_markdown(self):
        result = judge("test")
        md = format_krisis_markdown(result)
        assert "A2 Krisis" in md

    # PURPOSE: encode_krisis_observation をテストする
    def test_encode_krisis_observation(self):
        result = judge("test")
        obs = encode_krisis_observation(result)
        assert "confidence" in obs
