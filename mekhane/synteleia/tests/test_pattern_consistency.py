# PROOF: [L1/テスト] <- mekhane/synteleia/tests/ YAML ⇔ _FALLBACK 一致性テスト
# PURPOSE: YAML パターンと _FALLBACK ハードコード値のドリフトを検出
"""
Pattern Consistency Tests

YAML ファイルのパターン数/コード値が
各 Agent の _FALLBACK_* と一致するかを検証する。
"""

import pytest
from pathlib import Path

from mekhane.synteleia.pattern_loader import load_patterns, clear_cache


_POIESIS_YAML = Path(__file__).parent.parent / "poiesis" / "patterns.yaml"
_DOKIMASIA_YAML = Path(__file__).parent.parent / "dokimasia" / "patterns.yaml"


@pytest.fixture(autouse=True)
def _fresh_cache():
    """各テスト前にキャッシュをクリア。"""
    clear_cache()
    yield
    clear_cache()


# --- Poiēsis Agents ---


# PURPOSE: Test ousia consistency の実装
class TestOusiaConsistency:
    # PURPOSE: vague_patterns_count をテストする
    def test_vague_patterns_count(self):
        from mekhane.synteleia.poiesis.ousia_agent import OusiaAgent
        yaml_data = load_patterns(_POIESIS_YAML, "ousia")
        assert len(yaml_data["vague_patterns"]) == len(OusiaAgent._FALLBACK_VAGUE)

    # PURPOSE: undefined_patterns_count をテストする
    def test_undefined_patterns_count(self):
        from mekhane.synteleia.poiesis.ousia_agent import OusiaAgent
        yaml_data = load_patterns(_POIESIS_YAML, "ousia")
        assert len(yaml_data["undefined_patterns"]) == len(OusiaAgent._FALLBACK_UNDEFINED)

    # PURPOSE: vague_codes_match をテストする
    def test_vague_codes_match(self):
        from mekhane.synteleia.poiesis.ousia_agent import OusiaAgent
        yaml_data = load_patterns(_POIESIS_YAML, "ousia")
        yaml_codes = {p["code"] for p in yaml_data["vague_patterns"] if p.get("code")}
        fallback_codes = {t[1] for t in OusiaAgent._FALLBACK_VAGUE if t[1]}
        assert yaml_codes == fallback_codes


# PURPOSE: Test schema consistency の実装
class TestSchemaConsistency:
    # PURPOSE: structure_count をテストする
    def test_structure_count(self):
        from mekhane.synteleia.poiesis.schema_agent import SchemaAgent
        yaml_data = load_patterns(_POIESIS_YAML, "schema")
        assert len(yaml_data["structure_problems"]) == len(SchemaAgent._FALLBACK_STRUCTURE)

    # PURPOSE: hierarchy_count をテストする
    def test_hierarchy_count(self):
        from mekhane.synteleia.poiesis.schema_agent import SchemaAgent
        yaml_data = load_patterns(_POIESIS_YAML, "schema")
        assert len(yaml_data["hierarchy_problems"]) == len(SchemaAgent._FALLBACK_HIERARCHY)


# PURPOSE: Test horme consistency の実装
class TestHormeConsistency:
    # PURPOSE: keywords_count をテストする
    def test_keywords_count(self):
        from mekhane.synteleia.poiesis.horme_agent import HormeAgent
        yaml_data = load_patterns(_POIESIS_YAML, "horme")
        assert len(yaml_data["purpose_keywords"]) == len(HormeAgent._FALLBACK_KEYWORDS)

    # PURPOSE: patterns_count をテストする
    def test_patterns_count(self):
        from mekhane.synteleia.poiesis.horme_agent import HormeAgent
        yaml_data = load_patterns(_POIESIS_YAML, "horme")
        assert len(yaml_data["unclear_motivation_patterns"]) == len(HormeAgent._FALLBACK_PATTERNS)


# --- Dokimasia Agents ---


# PURPOSE: Test operator consistency の実装
class TestOperatorConsistency:
    # PURPOSE: ccl_operators_count をテストする
    def test_ccl_operators_count(self):
        from mekhane.synteleia.dokimasia.operator_agent import OperatorAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "operator")
        assert len(yaml_data["ccl_operators"]) == len(OperatorAgent._FALLBACK_CCL_OPERATORS)

    # PURPOSE: misuse_count をテストする
    def test_misuse_count(self):
        from mekhane.synteleia.dokimasia.operator_agent import OperatorAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "operator")
        assert len(yaml_data["misuse_patterns"]) == len(OperatorAgent._FALLBACK_MISUSE)


# PURPOSE: Test logic consistency の実装
class TestLogicConsistency:
    # PURPOSE: contradiction_count をテストする
    def test_contradiction_count(self):
        from mekhane.synteleia.dokimasia.logic_agent import LogicAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "logic")
        assert len(yaml_data["contradiction_pairs"]) == len(LogicAgent._FALLBACK_CONTRADICTIONS)

    # PURPOSE: logic_count をテストする
    def test_logic_count(self):
        from mekhane.synteleia.dokimasia.logic_agent import LogicAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "logic")
        assert len(yaml_data["logic_patterns"]) == len(LogicAgent._FALLBACK_LOGIC)


# PURPOSE: Test perigraphe consistency の実装
class TestPerigrapheConsistency:
    # PURPOSE: scope_count をテストする
    def test_scope_count(self):
        from mekhane.synteleia.dokimasia.perigraphe_agent import PerigrapheAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "perigraphe")
        assert len(yaml_data["scope_creep_patterns"]) == len(PerigrapheAgent._FALLBACK_SCOPE_CREEP)

    # PURPOSE: boundary_count をテストする
    def test_boundary_count(self):
        from mekhane.synteleia.dokimasia.perigraphe_agent import PerigrapheAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "perigraphe")
        assert len(yaml_data["boundary_keywords"]) == len(PerigrapheAgent._FALLBACK_BOUNDARY_KEYWORDS)


# PURPOSE: Test kairos consistency の実装
class TestKairosConsistency:
    # PURPOSE: timing_count をテストする
    def test_timing_count(self):
        from mekhane.synteleia.dokimasia.kairos_agent import KairosAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "kairos")
        assert len(yaml_data["timing_problems"]) == len(KairosAgent._FALLBACK_TIMING)

    # PURPOSE: temporal_count をテストする
    def test_temporal_count(self):
        from mekhane.synteleia.dokimasia.kairos_agent import KairosAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "kairos")
        assert len(yaml_data["temporal_keywords"]) == len(KairosAgent._FALLBACK_TEMPORAL_KEYWORDS)

    # PURPOSE: premature_count をテストする
    def test_premature_count(self):
        from mekhane.synteleia.dokimasia.kairos_agent import KairosAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "kairos")
        assert len(yaml_data["premature_patterns"]) == len(KairosAgent._FALLBACK_PREMATURE)


# PURPOSE: Test completeness consistency の実装
class TestCompletenessConsistency:
    # PURPOSE: incomplete_count をテストする
    def test_incomplete_count(self):
        from mekhane.synteleia.dokimasia.completeness_agent import CompletenessAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "completeness")
        assert len(yaml_data["incomplete_markers"]) == len(CompletenessAgent._FALLBACK_INCOMPLETE)

    # PURPOSE: empty_count をテストする
    def test_empty_count(self):
        from mekhane.synteleia.dokimasia.completeness_agent import CompletenessAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "completeness")
        assert len(yaml_data["empty_patterns"]) == len(CompletenessAgent._FALLBACK_EMPTY)

    # PURPOSE: required_count をテストする
    def test_required_count(self):
        from mekhane.synteleia.dokimasia.completeness_agent import CompletenessAgent
        yaml_data = load_patterns(_DOKIMASIA_YAML, "completeness")
        assert len(yaml_data["required_elements"]) == len(CompletenessAgent._FALLBACK_REQUIRED)


# --- F1: Exclude Patterns ---


# PURPOSE: Test exclude patterns の実装
class TestExcludePatterns:
    # PURPOSE: exclude_by_glob をテストする
    def test_exclude_by_glob(self):
        from mekhane.synteleia.orchestrator import SynteleiaOrchestrator
        from mekhane.synteleia.base import AuditTarget, AuditTargetType

        target = AuditTarget(
            content="eval() is dangerous",
            source="mekhane/synteleia/dokimasia/patterns.yaml",
            target_type=AuditTargetType.CODE,
            exclude_patterns=["**/patterns.yaml"],
        )
        orch = SynteleiaOrchestrator()
        result = orch.audit(target)
        assert result.passed is True
        assert "Excluded" in result.summary

    # PURPOSE: no_exclude_when_no_patterns をテストする
    def test_no_exclude_when_no_patterns(self):
        from mekhane.synteleia.orchestrator import SynteleiaOrchestrator
        from mekhane.synteleia.base import AuditTarget, AuditTargetType

        target = AuditTarget(
            content="this is a test",
            source="mekhane/synteleia/poiesis/ousia_agent.py",
            target_type=AuditTargetType.CODE,
        )
        orch = SynteleiaOrchestrator()
        result = orch.audit(target)
        # Should not be excluded; should go through normal audit
        assert result.summary != ""
