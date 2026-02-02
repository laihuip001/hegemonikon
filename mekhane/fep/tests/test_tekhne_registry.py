# PROOF: [L3/テスト] <- mekhane/fep/tests/ 対象モジュールが存在→検証が必要
"""
Tests for P4 Tekhnē Registry module

テスト項目:
1. Technique データクラス
2. TekhnēRegistry の CRUD 操作
3. 検索機能
4. 使用記録と経験的成功率
5. FEP B行列変換
"""

import pytest
import json
from mekhane.fep.tekhne_registry import (
    TechniqueQuadrant,
    ActionCategory,
    Technique,
    TekhnēRegistry,
    STANDARD_TECHNIQUES,
    encode_technique_as_b_matrix_entry,
    format_registry_markdown,
    get_registry,
    search_techniques,
)


class TestTechniqueQuadrant:
    """TechniqueQuadrant enum tests"""

    def test_all_quadrants_exist(self):
        assert TechniqueQuadrant.EXPERIMENTAL.value == "experimental"
        assert TechniqueQuadrant.INNOVATIVE.value == "innovative"
        assert TechniqueQuadrant.APPLIED.value == "applied"
        assert TechniqueQuadrant.ESTABLISHED.value == "established"


class TestActionCategory:
    """ActionCategory enum tests"""

    def test_all_categories_exist(self):
        assert ActionCategory.COGNITIVE.value == "cognitive"
        assert ActionCategory.CREATIVE.value == "creative"
        assert ActionCategory.EVALUATIVE.value == "evaluative"
        assert ActionCategory.EXECUTIVE.value == "executive"
        assert ActionCategory.TEMPORAL.value == "temporal"
        assert ActionCategory.PERSISTENCE.value == "persistence"


class TestTechnique:
    """Technique dataclass tests"""

    def test_create_technique(self):
        tech = Technique(
            id="test",
            name="Test Technique",
            description="A test technique",
            category=ActionCategory.COGNITIVE,
            quadrant=TechniqueQuadrant.ESTABLISHED,
        )
        assert tech.id == "test"
        assert tech.name == "Test Technique"
        assert tech.risk_level == 0.3  # default
        assert tech.time_cost == 3  # default

    def test_to_dict(self):
        tech = Technique(
            id="test",
            name="Test",
            description="Description",
            category=ActionCategory.COGNITIVE,
            quadrant=TechniqueQuadrant.EXPERIMENTAL,
            keywords=["keyword1", "keyword2"],
        )
        d = tech.to_dict()
        assert d["id"] == "test"
        assert d["category"] == "cognitive"
        assert d["quadrant"] == "experimental"
        assert len(d["keywords"]) == 2


class TestStandardTechniques:
    """STANDARD_TECHNIQUES registry tests"""

    def test_standard_techniques_populated(self):
        assert len(STANDARD_TECHNIQUES) >= 10

    def test_contains_core_techniques(self):
        assert "noe" in STANDARD_TECHNIQUES
        assert "bou" in STANDARD_TECHNIQUES
        assert "zet" in STANDARD_TECHNIQUES
        assert "ene" in STANDARD_TECHNIQUES
        assert "mek" in STANDARD_TECHNIQUES

    def test_all_techniques_have_required_fields(self):
        for tid, tech in STANDARD_TECHNIQUES.items():
            assert tech.id == tid
            assert tech.name
            assert tech.description
            assert isinstance(tech.category, ActionCategory)
            assert isinstance(tech.quadrant, TechniqueQuadrant)


class TestTekhnēRegistry:
    """TekhnēRegistry class tests"""

    def test_create_with_defaults(self):
        registry = TekhnēRegistry()
        assert registry.size >= 10

    def test_create_with_custom_techniques(self):
        custom = {
            "custom1": Technique(
                id="custom1",
                name="Custom",
                description="Custom technique",
                category=ActionCategory.COGNITIVE,
                quadrant=TechniqueQuadrant.EXPERIMENTAL,
            )
        }
        registry = TekhnēRegistry(custom)
        assert registry.size == 1

    def test_get_technique(self):
        registry = TekhnēRegistry()
        tech = registry.get("noe")
        assert tech is not None
        assert tech.name == "Noēsis"

    def test_get_nonexistent_returns_none(self):
        registry = TekhnēRegistry()
        assert registry.get("nonexistent") is None

    def test_register_new_technique(self):
        registry = TekhnēRegistry()
        initial_size = registry.size
        new_tech = Technique(
            id="new_tech",
            name="New",
            description="New technique",
            category=ActionCategory.CREATIVE,
            quadrant=TechniqueQuadrant.INNOVATIVE,
        )
        registry.register(new_tech)
        assert registry.size == initial_size + 1
        assert registry.get("new_tech") is not None

    def test_search_by_keyword(self):
        registry = TekhnēRegistry()
        results = registry.search(keyword="認識")
        assert len(results) >= 1
        assert any(r.id == "noe" for r in results)

    def test_search_by_category(self):
        registry = TekhnēRegistry()
        results = registry.search(category=ActionCategory.COGNITIVE)
        assert len(results) >= 3
        assert all(r.category == ActionCategory.COGNITIVE for r in results)

    def test_search_by_quadrant(self):
        registry = TekhnēRegistry()
        results = registry.search(quadrant=TechniqueQuadrant.ESTABLISHED)
        assert len(results) >= 3
        assert all(r.quadrant == TechniqueQuadrant.ESTABLISHED for r in results)

    def test_search_by_max_risk(self):
        registry = TekhnēRegistry()
        results = registry.search(max_risk=0.2)
        assert all(r.risk_level <= 0.2 for r in results)

    def test_search_by_max_time(self):
        registry = TekhnēRegistry()
        results = registry.search(max_time=2)
        assert all(r.time_cost <= 2 for r in results)

    def test_record_usage(self):
        registry = TekhnēRegistry()
        registry.record_usage("noe", True)
        registry.record_usage("noe", True)
        registry.record_usage("noe", False)
        success_rate = registry.get_empirical_success_rate("noe")
        assert success_rate == pytest.approx(2 / 3)

    def test_get_empirical_success_rate_no_history(self):
        registry = TekhnēRegistry()
        assert registry.get_empirical_success_rate("noe") is None

    def test_get_statistics(self):
        registry = TekhnēRegistry()
        stats = registry.get_statistics()
        assert "total_techniques" in stats
        assert "by_category" in stats
        assert "by_quadrant" in stats
        assert stats["total_techniques"] >= 10

    def test_to_json_and_from_json(self):
        registry = TekhnēRegistry()
        registry.record_usage("noe", True)
        json_str = registry.to_json()

        restored = TekhnēRegistry.from_json(json_str)
        assert restored.size == registry.size
        assert restored.get("noe") is not None


class TestEncodeTechniqueAsBMatrixEntry:
    """FEP B-matrix encoding tests"""

    def test_encode_high_success_low_risk(self):
        tech = Technique(
            id="test",
            name="Test",
            description="Test",
            category=ActionCategory.COGNITIVE,
            quadrant=TechniqueQuadrant.ESTABLISHED,
            success_rate=0.9,
            risk_level=0.1,
        )
        entry = encode_technique_as_b_matrix_entry(tech)
        assert entry["transition_success"] == pytest.approx(0.9 * 0.9)  # 0.81
        assert entry["transition_failure"] == pytest.approx(1 - 0.81)

    def test_encode_low_success_high_risk(self):
        tech = Technique(
            id="test",
            name="Test",
            description="Test",
            category=ActionCategory.COGNITIVE,
            quadrant=TechniqueQuadrant.EXPERIMENTAL,
            success_rate=0.5,
            risk_level=0.5,
        )
        entry = encode_technique_as_b_matrix_entry(tech)
        assert entry["transition_success"] == pytest.approx(0.25)


class TestFormatRegistryMarkdown:
    """format_registry_markdown tests"""

    def test_formats_registry(self):
        registry = TekhnēRegistry()
        markdown = format_registry_markdown(registry)
        assert "P4 Tekhnē Registry" in markdown
        assert "登録技法数" in markdown


class TestGlobalRegistry:
    """Global registry function tests"""

    def test_get_registry_returns_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_search_techniques_convenience(self):
        results = search_techniques("実行")
        assert len(results) >= 1
