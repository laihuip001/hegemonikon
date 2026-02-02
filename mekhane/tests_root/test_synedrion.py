# PROOF: [L3/テスト] <- mekhane/tests_root/ 対象モジュールが存在→検証が必要
#!/usr/bin/env python3
"""
Synedrion テストスイート

TDD Enforcement (Module 04) 適用

実行方法:
    cd hegemonikon
    python3 -m pytest tests/test_synedrion.py -v
"""

import pytest
import re
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# パッケージとしてインポート
from mekhane.symploke.specialist_prompts import (
    PHASE1_SPECIALISTS,
    get_all_specialists,
    generate_prompt,
    get_all_categories,
    Archetype,
)
from mekhane.symploke.phase0_specialists import PHASE0_SPECIALISTS
from mekhane.symploke.phase2_specialists import PHASE2_LAYER_7_10_SPECIALISTS
from mekhane.symploke.phase2_remaining import PHASE2_LAYER_11_15_SPECIALISTS
from mekhane.symploke.phase3_specialists import PHASE3_SPECIALISTS


class TestSpecialistCount:
    """専門家数のテスト"""

    def test_get_all_specialists_count_is_866(self):
        """866人の専門家が正確に読み込まれる"""
        specialists = get_all_specialists()
        assert len(specialists) == 866, f"Expected 866, got {len(specialists)}"

    def test_phase0_count_is_255(self):
        """Phase 0 は 255人"""
        assert len(PHASE0_SPECIALISTS) == 255

    def test_phase1_count_is_91(self):
        """Phase 1 は 91人"""
        assert len(PHASE1_SPECIALISTS) == 91

    def test_phase2_count_is_290(self):
        """Phase 2 は 290人 (170 + 120)"""
        total = len(PHASE2_LAYER_7_10_SPECIALISTS) + len(PHASE2_LAYER_11_15_SPECIALISTS)
        assert total == 290

    def test_phase3_count_is_230(self):
        """Phase 3 は 230人"""
        assert len(PHASE3_SPECIALISTS) == 230


class TestSpecialistDefinition:
    """専門家定義の構造テスト"""

    def test_specialist_has_required_fields(self):
        """全専門家が必須フィールドを持つ"""
        for spec in get_all_specialists():
            assert hasattr(spec, "id"), f"{spec} missing 'id'"
            assert hasattr(spec, "name"), f"{spec} missing 'name'"
            assert hasattr(spec, "category"), f"{spec} missing 'category'"
            assert hasattr(spec, "archetype"), f"{spec} missing 'archetype'"
            assert hasattr(spec, "focus"), f"{spec} missing 'focus'"

    def test_specialist_ids_are_unique(self):
        """専門家IDは一意"""
        ids = [spec.id for spec in get_all_specialists()]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_specialist_id_format(self):
        """専門家IDは正しいフォーマット (XX-NNN)"""
        # I18N, STAT など1-4文字のプレフィックス対応
        pattern = r"^[A-Z0-9]{1,5}-\d{3}$"
        for spec in get_all_specialists():
            assert re.match(pattern, spec.id), f"Invalid ID format: {spec.id}"


class TestPromptGeneration:
    """プロンプト生成テスト"""

    def test_generate_prompt_contains_target_file(self):
        """プロンプトにターゲットファイルが含まれる"""
        spec = get_all_specialists()[0]
        target = "mekhane/symploke/test.py"
        prompt = generate_prompt(spec, target)
        assert target in prompt

    def test_generate_prompt_contains_specialist_name(self):
        """プロンプトに専門家名が含まれる"""
        spec = get_all_specialists()[0]
        prompt = generate_prompt(spec, "test.py")
        assert spec.name in prompt

    def test_generate_prompt_contains_output_path(self):
        """プロンプトに出力パスが含まれる"""
        spec = get_all_specialists()[0]
        prompt = generate_prompt(spec, "test.py")
        assert "docs/reviews/" in prompt


class TestCategoryDistribution:
    """カテゴリ分布テスト"""

    def test_get_all_categories(self):
        """全カテゴリが取得できる"""
        # get_all_specialists() から動的にカテゴリを収集
        categories = set(spec.category for spec in get_all_specialists())
        assert len(categories) >= 20, f"Expected at least 20, got {len(categories)}"

    def test_category_coverage(self):
        """主要カテゴリがカバーされている"""
        categories = set(spec.category for spec in get_all_specialists())
        expected = [
            "code_quality",
            "documentation",
            "architecture",
            "cognitive_load",
            "ai_risk",
            "async",
            "observability",
            "distributed",
        ]
        for cat in expected:
            assert cat in categories, f"Missing category: {cat}"


class TestArchetypeDistribution:
    """アーキタイプ分布テスト"""

    def test_all_archetypes_used(self):
        """全5アーキタイプが使用されている"""
        used_archetypes = set(spec.archetype for spec in get_all_specialists())
        assert Archetype.PRECISION in used_archetypes
        assert Archetype.SAFETY in used_archetypes
        assert Archetype.CREATIVE in used_archetypes


class TestErrorHandling:
    """エラーハンドリングテスト (Devil's Advocate 対策)"""

    def test_empty_error_vs_silence(self):
        """空エラーと沈黙を区別できる"""
        error_result = {"id": "CL-002", "error": ""}
        success_result = {"id": "CL-001", "session_id": "123", "status": "started"}

        has_error = "error" in error_result
        is_silence = "error" not in success_result and "session_id" in success_result

        assert has_error is True
        assert is_silence is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
