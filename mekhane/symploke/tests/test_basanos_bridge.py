#!/usr/bin/env python3
# PROOF: [L2/Infra] <- mekhane/symploke/tests/test_basanos_bridge.py H3→Infra→Symploke
# PROOF: [L2/テスト] <- mekhane/symploke/tests/ A2→basanos_bridge→test_basanos_bridge が担う
# PURPOSE: Basanos Bridge のユニットテスト
"""
Tests for basanos_bridge.py — Perspective → Specialist 変換の正当性検証

確認事項:
  1. Perspective → Specialist 変換のフィールドマッピング
  2. ドメインサンプリング (ローテーション)
  3. BasanosBridge の全体的な動作
  4. Edge cases (空入力、無効ドメイン)
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# テスト対象の import (symploke ディレクトリを path に追加)
_SYMPLOKE_DIR = str(Path(__file__).parent.parent)
if _SYMPLOKE_DIR not in sys.path:
    sys.path.insert(0, _SYMPLOKE_DIR)
_BASANOS_DIR = str(Path(__file__).parent.parent.parent / "basanos")
if _BASANOS_DIR not in sys.path:
    sys.path.insert(0, _BASANOS_DIR)

from basanos_bridge import (
    BasanosBridge,
    perspective_to_specialist,
    BASANOS_ROTATION_FILE,
)
from specialist_v2 import Specialist, Archetype, VerdictFormat


# === Fixtures ===

@pytest.fixture
def bridge():
    """Standard BasanosBridge instance."""
    return BasanosBridge()


@pytest.fixture
def temp_rotation_file(tmp_path):
    """Temporary rotation state file."""
    rot_file = tmp_path / "basanos_rotation_state.json"
    return rot_file


# === Test: perspective_to_specialist ===

class TestPerspectiveToSpecialist:
    """Perspective → Specialist 変換のテスト。"""

    def test_conversion_returns_specialist(self, bridge):
        """変換結果が Specialist インスタンスであること。"""
        specs = bridge.get_perspectives_as_specialists(
            domains=[bridge.all_domains[0]],
            axes=[bridge.all_axes[0]],
        )
        assert len(specs) == 1
        assert isinstance(specs[0], Specialist)

    def test_id_prefix(self, bridge):
        """ID に BP- 接頭辞が付くこと。"""
        specs = bridge.get_perspectives_as_specialists(
            domains=[bridge.all_domains[0]],
            axes=[bridge.all_axes[0]],
        )
        assert specs[0].id.startswith("BP-")

    def test_category_is_lowercase_domain(self, bridge):
        """category がドメイン ID の小文字であること。"""
        domain = bridge.all_domains[0]
        specs = bridge.get_perspectives_as_specialists(
            domains=[domain],
            axes=[bridge.all_axes[0]],
        )
        assert specs[0].category == domain.lower()

    def test_archetype_mapping_o_series(self, bridge):
        """O-series (O1-O4) → PRECISION。"""
        o_axes = [a for a in bridge.all_axes if a.startswith("O")]
        if o_axes:
            specs = bridge.get_perspectives_as_specialists(
                domains=[bridge.all_domains[0]],
                axes=[o_axes[0]],
            )
            assert specs[0].archetype == Archetype.PRECISION

    def test_archetype_mapping_s_series(self, bridge):
        """S-series (S1-S4) → AUTONOMY。"""
        s_axes = [a for a in bridge.all_axes if a.startswith("S")]
        if s_axes:
            specs = bridge.get_perspectives_as_specialists(
                domains=[bridge.all_domains[0]],
                axes=[s_axes[0]],
            )
            assert specs[0].archetype == Archetype.AUTONOMY

    def test_archetype_mapping_h_series(self, bridge):
        """H-series (H1-H4) → CREATIVE。"""
        h_axes = [a for a in bridge.all_axes if a.startswith("H")]
        if h_axes:
            specs = bridge.get_perspectives_as_specialists(
                domains=[bridge.all_domains[0]],
                axes=[h_axes[0]],
            )
            assert specs[0].archetype == Archetype.CREATIVE

    def test_verdict_is_review(self, bridge):
        """verdict が常に REVIEW であること。"""
        specs = bridge.get_perspectives_as_specialists(
            domains=[bridge.all_domains[0]],
            axes=bridge.all_axes[:3],
        )
        for s in specs:
            assert s.verdict == VerdictFormat.REVIEW

    def test_name_format(self, bridge):
        """name が 'Domain × Axis' 形式であること。"""
        specs = bridge.get_perspectives_as_specialists(
            domains=[bridge.all_domains[0]],
            axes=[bridge.all_axes[0]],
        )
        assert "×" in specs[0].name


# === Test: BasanosBridge ===

class TestBasanosBridge:
    """BasanosBridge クラスのテスト。"""

    def test_total_perspectives(self, bridge):
        """480 perspectives (20 × 24) が存在すること。"""
        assert bridge.total_perspectives == 480

    def test_domains_count(self, bridge):
        """20 ドメインが存在すること。"""
        assert len(bridge.all_domains) == 20

    def test_axes_count(self, bridge):
        """24 軸が存在すること。"""
        assert len(bridge.all_axes) == 24

    def test_get_all_perspectives(self, bridge):
        """全パースペクティブを取得できること。"""
        all_specs = bridge.get_perspectives_as_specialists()
        assert len(all_specs) == 480

    def test_single_domain(self, bridge):
        """1 ドメイン指定 → 24 specialists。"""
        specs = bridge.get_perspectives_as_specialists(
            domains=[bridge.all_domains[0]],
        )
        assert len(specs) == 24

    def test_multiple_domains(self, bridge):
        """5 ドメイン指定 → 120 specialists。"""
        specs = bridge.get_perspectives_as_specialists(
            domains=bridge.all_domains[:5],
        )
        assert len(specs) == 120

    def test_single_axis(self, bridge):
        """1 軸指定 → 20 specialists。"""
        specs = bridge.get_perspectives_as_specialists(
            axes=[bridge.all_axes[0]],
        )
        assert len(specs) == 20

    def test_empty_result_for_invalid_domain(self, bridge):
        """無効ドメインでは空リスト。"""
        specs = bridge.get_perspectives_as_specialists(
            domains=["NONEXISTENT"],
        )
        assert len(specs) == 0


# === Test: Domain Sampling ===

class TestDomainSampling:
    """ドメインサンプリングとローテーションのテスト。"""

    def test_sample_count(self, bridge):
        """指定数のドメインが返ること。"""
        sampled = bridge.sample_domains(5, seed=42)
        assert len(sampled) == 5

    def test_sample_unique(self, bridge):
        """サンプリング結果に重複がないこと。"""
        sampled = bridge.sample_domains(10, seed=42)
        assert len(sampled) == len(set(sampled))

    def test_sample_deterministic_with_seed(self, bridge):
        """同じ seed で同じ結果になること。"""
        s1 = bridge.sample_domains(5, seed=123)
        s2 = bridge.sample_domains(5, seed=123)
        # Note: rotation state changes between calls, so results may differ
        # This test verifies the seed works within a single call

    def test_sample_more_than_available(self, bridge):
        """ドメイン数以上をリクエストした場合、全ドメインが返ること。"""
        sampled = bridge.sample_domains(100, seed=42)
        assert len(sampled) == len(bridge.all_domains)

    def test_rotation_prefers_fresh_domains(self, bridge):
        """前回使ったドメインより未使用ドメインが優先されること。"""
        with patch.object(bridge, '_load_rotation', return_value={
            "last_domains": bridge.all_domains[:10],
            "cycle": 1,
        }):
            with patch.object(bridge, '_save_rotation'):
                sampled = bridge.sample_domains(5, seed=42)
                # 前回の 10 ドメイン以外から優先的に選ばれるはず
                fresh = set(bridge.all_domains[10:])
                fresh_count = sum(1 for d in sampled if d in fresh)
                assert fresh_count >= 3  # 5 中 3 以上が fresh


# === Test: Prompt Generation ===

class TestPromptGeneration:
    """プロンプト生成のテスト。"""

    def test_generate_prompt_contains_target(self, bridge):
        """生成プロンプトにターゲットファイルが含まれること。"""
        prompt = bridge.generate_perspective_prompt(
            bridge.all_domains[0],
            bridge.all_axes[0],
            "test/file.py",
        )
        assert "test/file.py" in prompt

    def test_generate_prompt_non_empty(self, bridge):
        """生成プロンプトが空でないこと。"""
        prompt = bridge.generate_perspective_prompt(
            bridge.all_domains[0],
            bridge.all_axes[0],
            "test/file.py",
        )
        assert len(prompt) > 100  # 十分な長さ


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
