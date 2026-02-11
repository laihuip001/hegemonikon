#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → Doxa 永続化と /boot 統合の正しさを検証
   → save/load round-trip + Sophia 昇格判定 + ブートサマリー
   → test_doxa_boot.py が担う

Q.E.D.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from mekhane.fep.doxa_persistence import (
    Belief,
    BeliefStrength,
    DoxaStore,
)
from mekhane.symploke.doxa_boot import (
    PROMOTION_MIN_AGE_DAYS,
    PROMOTION_MIN_CONFIDENCE,
    PromotionCandidate,
    check_promotion_candidates,
    format_doxa_summary,
    load_doxa_for_boot,
)


# =============================================================================
# DoxaStore File Persistence
# =============================================================================


# PURPOSE: Test suite validating doxa file persistence correctness
class TestDoxaFilePersistence:
    """DoxaStore のファイル永続化テスト。"""

    # PURPOSE: Verify save load roundtrip behaves correctly
    def test_save_load_roundtrip(self, tmp_path):
        """信念を保存→読込で完全復元。"""
        store = DoxaStore()
        store.persist("意志より環境", BeliefStrength.CORE, 0.95, ["FEP", "MP"])
        store.persist("確信度は正直に", BeliefStrength.STRONG, 0.88, ["経験"])

        path = tmp_path / "beliefs.yaml"
        store.save_to_file(path)

        # 新しいストアで読込
        store2 = DoxaStore()
        loaded = store2.load_from_file(path)

        assert loaded == 2
        b1 = store2.get("意志より環境")
        assert b1 is not None
        assert b1.strength == BeliefStrength.CORE
        assert b1.confidence == 0.95
        assert b1.evidence == ["FEP", "MP"]

    # PURPOSE: Verify save load with archive behaves correctly
    def test_save_load_with_archive(self, tmp_path):
        """アーカイブも含めて round-trip。"""
        store = DoxaStore()
        store.persist("temporary", BeliefStrength.WEAK, 0.3)
        store.archive("temporary")

        path = tmp_path / "beliefs.yaml"
        store.save_to_file(path)

        store2 = DoxaStore()
        store2.load_from_file(path)
        assert len(store2.list_all()) == 0
        assert len(store2.list_archived()) == 1
        assert store2.list_archived()[0].content == "temporary"

    # PURPOSE: Verify load nonexistent file behaves correctly
    def test_load_nonexistent_file(self, tmp_path):
        """存在しないファイル → 0 件。"""
        store = DoxaStore()
        loaded = store.load_from_file(tmp_path / "nope.yaml")
        assert loaded == 0

    # PURPOSE: Verify save creates directory behaves correctly
    def test_save_creates_directory(self, tmp_path):
        """ディレクトリが存在しなくても作成。"""
        store = DoxaStore()
        store.persist("test", BeliefStrength.MODERATE, 0.7)

        path = tmp_path / "deep" / "nested" / "beliefs.yaml"
        store.save_to_file(path)
        assert path.exists()

    # PURPOSE: Verify datetime roundtrip behaves correctly
    def test_datetime_roundtrip(self, tmp_path):
        """日時が正確に round-trip。"""
        store = DoxaStore()
        now = datetime.now()
        store.persist("time test", BeliefStrength.MODERATE, 0.5)

        path = tmp_path / "beliefs.yaml"
        store.save_to_file(path)

        store2 = DoxaStore()
        store2.load_from_file(path)
        b = store2.get("time test")
        assert b is not None
        # Microsecond precision may vary, check within 1 second
        assert abs((b.created_at - now).total_seconds()) < 1

    # PURPOSE: Verify evolve then save behaves correctly
    def test_evolve_then_save(self, tmp_path):
        """進化後の状態も保存される。"""
        store = DoxaStore()
        store.persist("growable", BeliefStrength.WEAK, 0.3)
        store.evolve("growable", 0.92, ["new evidence"])

        path = tmp_path / "beliefs.yaml"
        store.save_to_file(path)

        store2 = DoxaStore()
        store2.load_from_file(path)
        b = store2.get("growable")
        assert b is not None
        assert b.confidence == 0.92
        assert b.strength == BeliefStrength.STRONG  # Auto-promoted
        assert "new evidence" in b.evidence

    # PURPOSE: Verify yaml is readable behaves correctly
    def test_yaml_is_readable(self, tmp_path):
        """保存されたYAMLが人間が読める形式。"""
        store = DoxaStore()
        store.persist("日本語テスト", BeliefStrength.MODERATE, 0.7)

        path = tmp_path / "beliefs.yaml"
        store.save_to_file(path)

        content = path.read_text(encoding="utf-8")
        assert "日本語テスト" in content
        assert "moderate" in content


# =============================================================================
# Sophia Promotion Candidates
# =============================================================================


# PURPOSE: Test suite validating promotion candidates correctness
class TestPromotionCandidates:
    """Sophia 昇格候補検出テスト。"""

    def _make_old_belief(
        self, content: str, days_old: float, **kwargs
    ) -> Belief:
        """指定日数前に作成された Belief を生成。"""
        created = datetime.now() - timedelta(days=days_old)
        return Belief(
            content=content,
            created_at=created,
            updated_at=created,
            **kwargs,
        )

    # PURPOSE: Verify promotable belief behaves correctly
    def test_promotable_belief(self):
        """全条件を満たす信念 → 昇格候補。"""
        store = DoxaStore()
        old_belief = self._make_old_belief(
            "意志より環境",
            days_old=30,
            strength=BeliefStrength.STRONG,
            confidence=0.90,
            evidence=["FEP", "MP", "実践"],
        )
        store._beliefs["意志より環境"] = old_belief

        candidates = check_promotion_candidates(store)
        assert len(candidates) == 1
        assert candidates[0].belief.content == "意志より環境"
        assert candidates[0].score == 1.0

    # PURPOSE: Verify weak belief not promoted behaves correctly
    def test_weak_belief_not_promoted(self):
        """strength < STRONG → 昇格しない。"""
        store = DoxaStore()
        old_belief = self._make_old_belief(
            "仮説",
            days_old=30,
            strength=BeliefStrength.MODERATE,
            confidence=0.90,
            evidence=["e1", "e2"],
        )
        store._beliefs["仮説"] = old_belief

        candidates = check_promotion_candidates(store)
        assert len(candidates) == 0

    # PURPOSE: Verify young belief not promoted behaves correctly
    def test_young_belief_not_promoted(self):
        """age < 14 → 昇格しない。"""
        store = DoxaStore()
        young_belief = self._make_old_belief(
            "新しい学び",
            days_old=3,
            strength=BeliefStrength.STRONG,
            confidence=0.90,
            evidence=["e1", "e2"],
        )
        store._beliefs["新しい学び"] = young_belief

        candidates = check_promotion_candidates(store)
        assert len(candidates) == 0

    # PURPOSE: Verify low confidence not promoted behaves correctly
    def test_low_confidence_not_promoted(self):
        """confidence < 0.85 → 昇格しない。"""
        store = DoxaStore()
        low_conf = self._make_old_belief(
            "まだ確信なし",
            days_old=30,
            strength=BeliefStrength.STRONG,
            confidence=0.60,
            evidence=["e1", "e2"],
        )
        store._beliefs["まだ確信なし"] = low_conf

        candidates = check_promotion_candidates(store)
        assert len(candidates) == 0

    # PURPOSE: Verify no evidence not promoted behaves correctly
    def test_no_evidence_not_promoted(self):
        """evidence < 2 → 昇格しない。"""
        store = DoxaStore()
        no_ev = self._make_old_belief(
            "根拠不足",
            days_old=30,
            strength=BeliefStrength.STRONG,
            confidence=0.90,
            evidence=["only one"],
        )
        store._beliefs["根拠不足"] = no_ev

        candidates = check_promotion_candidates(store)
        assert len(candidates) == 0

    # PURPOSE: Verify core belief promotable behaves correctly
    def test_core_belief_promotable(self):
        """CORE strength も昇格対象。"""
        store = DoxaStore()
        core = self._make_old_belief(
            "核心信念",
            days_old=60,
            strength=BeliefStrength.CORE,
            confidence=0.95,
            evidence=["a", "b", "c"],
        )
        store._beliefs["核心信念"] = core

        candidates = check_promotion_candidates(store)
        assert len(candidates) == 1

    # PURPOSE: Verify empty store no candidates behaves correctly
    def test_empty_store_no_candidates(self):
        """空ストア → 候補なし。"""
        store = DoxaStore()
        candidates = check_promotion_candidates(store)
        assert len(candidates) == 0


# =============================================================================
# Boot Integration
# =============================================================================


# PURPOSE: Test suite validating doxa boot correctness
class TestDoxaBoot:
    """/boot Phase 3 Doxa 統合テスト。"""

    # PURPOSE: Verify load doxa for boot behaves correctly
    def test_load_doxa_for_boot(self, tmp_path):
        """beliefs.yaml → DoxaBootResult。"""
        # Create and save beliefs
        store = DoxaStore()
        store.persist("テスト信念", BeliefStrength.MODERATE, 0.7, ["evidence"])
        path = tmp_path / "beliefs.yaml"
        store.save_to_file(path)

        # Load in boot
        result = load_doxa_for_boot(store_path=path)
        assert result.beliefs_loaded == 1
        assert result.active_count == 1
        assert result.summary != ""

    # PURPOSE: Verify boot with no file behaves correctly
    def test_boot_with_no_file(self, tmp_path):
        """ファイルなし → 0 件、エラーなし。"""
        result = load_doxa_for_boot(store_path=tmp_path / "nope.yaml")
        assert result.beliefs_loaded == 0
        assert result.active_count == 0

    # PURPOSE: Verify summary format behaves correctly
    def test_summary_format(self, tmp_path):
        """サマリーに H4 Doxa ヘッダーがある。"""
        store = DoxaStore()
        store.persist("信念A", BeliefStrength.STRONG, 0.9)
        path = tmp_path / "beliefs.yaml"
        store.save_to_file(path)

        result = load_doxa_for_boot(store_path=path)
        assert "H4 Doxa" in result.summary
        assert "Active" in result.summary


# =============================================================================
# Summary Formatting
# =============================================================================


# PURPOSE: Test suite validating doxa summary correctness
class TestDoxaSummary:
    """Creator 向けサマリーテスト。"""

    # PURPOSE: Verify empty store summary behaves correctly
    def test_empty_store_summary(self):
        """空ストア → 基本テーブルのみ。"""
        store = DoxaStore()
        summary = format_doxa_summary(store, [])
        assert "Active | 0" in summary

    # PURPOSE: Verify summary with promotion behaves correctly
    def test_summary_with_promotion(self):
        """昇格候補があればセクションが追加される。"""
        store = DoxaStore()
        belief = Belief(
            content="テスト",
            strength=BeliefStrength.STRONG,
            confidence=0.9,
        )
        candidate = PromotionCandidate(
            belief=belief,
            reasons=["strength=strong", "confidence=90%"],
            score=1.0,
        )
        summary = format_doxa_summary(store, [candidate])
        assert "Sophia 昇格候補" in summary
        assert "テスト" in summary
