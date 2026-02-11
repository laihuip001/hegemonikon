#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → Doxa → Sophia 昇格パイプラインの正しさを検証
   → promote_to_sophia() の round-trip, 二重昇格防止, KI 構造
   → test_doxa_promoter.py が担う

Q.E.D.
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from mekhane.fep.doxa_persistence import (
    Belief,
    BeliefStrength,
    DoxaStore,
)
from mekhane.symploke.doxa_boot import (
    PromotionCandidate,
    check_promotion_candidates,
)
from mekhane.symploke.doxa_promoter import (
    PromotionResult,
    format_promotion_prompt,
    promote_approved,
    promote_to_sophia,
    _slugify,
    _next_ki_number,
)


# =============================================================================
# Helpers
# =============================================================================


def _make_promotable_belief(content: str = "意志より環境", **kwargs) -> Belief:
    """昇格条件を満たす Belief を生成。"""
    defaults = dict(
        strength=BeliefStrength.STRONG,
        confidence=0.90,
        evidence=["FEP", "実践", "MP"],
        created_at=datetime.now() - timedelta(days=30),
        updated_at=datetime.now() - timedelta(days=5),
    )
    defaults.update(kwargs)
    return Belief(content=content, **defaults)


def _make_candidate(belief: Belief = None) -> PromotionCandidate:
    """PromotionCandidate を生成。"""
    if belief is None:
        belief = _make_promotable_belief()
    return PromotionCandidate(
        belief=belief,
        reasons=["strength=strong", "confidence=90%", "age=30d", "evidence=3"],
        score=1.0,
    )


# =============================================================================
# Slugify
# =============================================================================


# PURPOSE: Test suite validating slugify correctness
class TestSlugify:
    """ファイル名用スラッグ生成テスト。"""

    # PURPOSE: Verify basic japanese behaves correctly
    def test_basic_japanese(self):
        """Verify basic japanese behavior."""
        assert _slugify("意志より環境") == "意志より環境"

    # PURPOSE: Verify spaces to underscores behaves correctly
    def test_spaces_to_underscores(self):
        """Verify spaces to underscores behavior."""
        assert _slugify("hello world") == "hello_world"

    # PURPOSE: Verify dangerous chars removed behaves correctly
    def test_dangerous_chars_removed(self):
        """Verify dangerous chars removed behavior."""
        result = _slugify('test/path:name*"file')
        assert "/" not in result
        assert ":" not in result
        assert "*" not in result

    # PURPOSE: Verify max length behaves correctly
    def test_max_length(self):
        """Verify max length behavior."""
        long_text = "あ" * 100
        result = _slugify(long_text, max_len=10)
        assert len(result) == 10


# =============================================================================
# KI Number
# =============================================================================


# PURPOSE: Test suite validating next ki number correctness
class TestNextKiNumber:
    """次の DX 番号決定テスト。"""

    # PURPOSE: Verify empty directory behaves correctly
    def test_empty_directory(self, tmp_path):
        """Verify empty directory behavior."""
        assert _next_ki_number(tmp_path) == 1

    # PURPOSE: Verify nonexistent directory behaves correctly
    def test_nonexistent_directory(self, tmp_path):
        """Verify nonexistent directory behavior."""
        assert _next_ki_number(tmp_path / "nope") == 1

    # PURPOSE: Verify existing dx behaves correctly
    def test_existing_dx(self, tmp_path):
        """Verify existing dx behavior."""
        (tmp_path / "DX-003_test").mkdir()
        (tmp_path / "DX-007_another").mkdir()
        assert _next_ki_number(tmp_path) == 8

    # PURPOSE: Verify ignores non dx behaves correctly
    def test_ignores_non_dx(self, tmp_path):
        """Verify ignores non dx behavior."""
        (tmp_path / "not_a_dx").mkdir()
        (tmp_path / "DX-005_real").mkdir()
        assert _next_ki_number(tmp_path) == 6


# =============================================================================
# Promote to Sophia
# =============================================================================


# PURPOSE: Test suite validating promote to sophia correctness
class TestPromoteToSophia:
    """昇格実行テスト。"""

    # PURPOSE: Verify successful promotion behaves correctly
    def test_successful_promotion(self, tmp_path):
        """昇格成功 → KI 構造が生成される。"""
        store = DoxaStore()
        belief = _make_promotable_belief()
        store._beliefs[belief.content] = belief
        candidate = _make_candidate(belief)

        result = promote_to_sophia(candidate, store, ki_base=tmp_path)

        assert result.success is True
        assert result.ki_id == "DX-001"
        assert result.ki_dir.exists()
        assert result.metadata_path.exists()
        assert result.markdown_path.exists()

    # PURPOSE: Verify ki structure behaves correctly
    def test_ki_structure(self, tmp_path):
        """KI 構造: metadata.json + artifacts/*.md."""
        store = DoxaStore()
        belief = _make_promotable_belief()
        store._beliefs[belief.content] = belief
        candidate = _make_candidate(belief)

        result = promote_to_sophia(candidate, store, ki_base=tmp_path)

        # metadata.json が正しい
        meta = json.loads(result.metadata_path.read_text())
        assert meta["ki_id"] == "DX-001"
        assert meta["source"] == "doxa_promotion"
        assert meta["confidence"] == 0.9

        # artifacts/*.md が正しい
        md_content = result.markdown_path.read_text()
        assert "意志より環境" in md_content
        assert "PROMOTED" in md_content

    # PURPOSE: Verify belief gets promoted flag behaves correctly
    def test_belief_gets_promoted_flag(self, tmp_path):
        """昇格後、Belief に promoted_at と sophia_ki_id が設定される。"""
        store = DoxaStore()
        belief = _make_promotable_belief()
        store._beliefs[belief.content] = belief
        candidate = _make_candidate(belief)

        assert belief.is_promoted is False

        promote_to_sophia(candidate, store, ki_base=tmp_path)

        assert belief.is_promoted is True
        assert belief.sophia_ki_id == "DX-001"
        assert belief.promoted_at is not None

    # PURPOSE: Verify double promotion prevented behaves correctly
    def test_double_promotion_prevented(self, tmp_path):
        """二重昇格は失敗する。"""
        store = DoxaStore()
        belief = _make_promotable_belief()
        store._beliefs[belief.content] = belief
        candidate = _make_candidate(belief)

        # 1回目: 成功
        result1 = promote_to_sophia(candidate, store, ki_base=tmp_path)
        assert result1.success is True

        # 2回目: 失敗
        result2 = promote_to_sophia(candidate, store, ki_base=tmp_path)
        assert result2.success is False
        assert "既に昇格済み" in result2.error

    # PURPOSE: Verify sequential numbering behaves correctly
    def test_sequential_numbering(self, tmp_path):
        """複数の昇格が DX-001, DX-002... と連番になる。"""
        store = DoxaStore()

        b1 = _make_promotable_belief("信念A")
        b2 = _make_promotable_belief("信念B")
        store._beliefs["信念A"] = b1
        store._beliefs["信念B"] = b2

        r1 = promote_to_sophia(_make_candidate(b1), store, ki_base=tmp_path)
        r2 = promote_to_sophia(_make_candidate(b2), store, ki_base=tmp_path)

        assert r1.ki_id == "DX-001"
        assert r2.ki_id == "DX-002"

    # PURPOSE: Verify promoted roundtrip persistence behaves correctly
    def test_promoted_roundtrip_persistence(self, tmp_path):
        """promoted フラグが save/load で維持される。"""
        store = DoxaStore()
        belief = _make_promotable_belief()
        store._beliefs[belief.content] = belief
        candidate = _make_candidate(belief)

        promote_to_sophia(candidate, store, ki_base=tmp_path)

        # Save
        yaml_path = tmp_path / "beliefs.yaml"
        store.save_to_file(yaml_path)

        # Load
        store2 = DoxaStore()
        store2.load_from_file(yaml_path)
        loaded = store2.get("意志より環境")

        assert loaded is not None
        assert loaded.is_promoted is True
        assert loaded.sophia_ki_id == "DX-001"


# =============================================================================
# Batch Promotion
# =============================================================================


# PURPOSE: Test suite validating promote approved correctness
class TestPromoteApproved:
    """一括昇格テスト。"""

    # PURPOSE: Verify batch promotion behaves correctly
    def test_batch_promotion(self, tmp_path):
        """複数候補の一括昇格。"""
        store = DoxaStore()
        beliefs = [
            _make_promotable_belief("信念A"),
            _make_promotable_belief("信念B"),
        ]
        for b in beliefs:
            store._beliefs[b.content] = b

        candidates = [_make_candidate(b) for b in beliefs]
        results = promote_approved(candidates, store, ki_base=tmp_path)

        assert len(results) == 2
        assert all(r.success for r in results)


# =============================================================================
# Promotion Prompt
# =============================================================================


# PURPOSE: Test suite validating format promotion prompt correctness
class TestFormatPromotionPrompt:
    """Creator 承認ゲート表示テスト。"""

    # PURPOSE: Verify empty candidates behaves correctly
    def test_empty_candidates(self):
        """Verify empty candidates behavior."""
        assert format_promotion_prompt([]) == ""

    # PURPOSE: Verify prompt contents behaves correctly
    def test_prompt_contents(self):
        """Verify prompt contents behavior."""
        candidate = _make_candidate()
        prompt = format_promotion_prompt([candidate])

        assert "Sophia 昇格候補" in prompt
        assert "意志より環境" in prompt
        assert "90%" in prompt
        assert "kernel/knowledge/doxa/" in prompt

    # PURPOSE: Verify multiple candidates behaves correctly
    def test_multiple_candidates(self):
        """Verify multiple candidates behavior."""
        c1 = _make_candidate(_make_promotable_belief("信念A"))
        c2 = _make_candidate(_make_promotable_belief("信念B"))
        prompt = format_promotion_prompt([c1, c2])

        assert "1." in prompt
        assert "2." in prompt


# =============================================================================
# Integration: Boot → Detect → Promote → Persist
# =============================================================================


# PURPOSE: Test suite validating integration correctness
class TestIntegration:
    """検出 → 昇格 → 永続化の統合テスト。"""

    # PURPOSE: Verify full pipeline behaves correctly
    def test_full_pipeline(self, tmp_path):
        """信念作成 → 候補検出 → 昇格 → 保存 → 復元 → 再検出しない。"""
        # 1. 信念作成
        store = DoxaStore()
        belief = _make_promotable_belief()
        store._beliefs[belief.content] = belief

        # 2. 候補検出
        candidates = check_promotion_candidates(store)
        assert len(candidates) == 1

        # 3. 昇格実行
        result = promote_to_sophia(candidates[0], store, ki_base=tmp_path)
        assert result.success is True

        # 4. 永続化
        yaml_path = tmp_path / "beliefs.yaml"
        store.save_to_file(yaml_path)

        # 5. 復元
        store2 = DoxaStore()
        store2.load_from_file(yaml_path)

        # 6. 再検出 → 昇格済みなので候補に出ない
        candidates2 = check_promotion_candidates(store2)
        assert len(candidates2) == 0
