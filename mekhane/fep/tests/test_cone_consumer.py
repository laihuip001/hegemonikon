# PROOF: [L3/テスト] <- mekhane/fep/tests/
# PURPOSE: cone_consumer (advise + devil_attack) のテスト
"""Tests for mekhane.fep.cone_consumer."""

import pytest

from mekhane.fep.category import Series
from mekhane.fep.cone_builder import converge
from mekhane.fep.cone_consumer import (
    ConeAdvice,
    ContradictionPair,
    DevilAttack,
    advise,
    devil_attack,
)


# PURPOSE: advise() のテスト — Active inference action selection
class TestAdvise:
    """advise() のテスト — Active inference action selection."""

    # PURPOSE: V > 0.3 → devil action
    def test_high_dispersion_returns_devil(self):
        """V > 0.3 → devil action."""
        cone = converge(
            Series.O,
            outputs={
                "O1": "中止すべき。品質が不十分",
                "O2": "即座に実行を開始する",
                "O3": "再設計が必要",
                "O4": "現計画を継続",
            },
        )
        advice = advise(cone)
        assert advice.action == "devil"
        assert advice.suggested_wf == "/dia devil"
        assert advice.urgency > 0.3

    # PURPOSE: V ≤ 0.1 + high confidence → proceed
    def test_low_dispersion_returns_proceed(self):
        """V ≤ 0.1 + high confidence → proceed."""
        cone = converge(
            Series.O,
            outputs={
                "O1": "統合的に進める方向",
                "O2": "統合的に進める方向で",
                "O3": "統合的に進める方向を問う",
                "O4": "統合的に進める方向を実行",
            },
            confidence=80.0,
        )
        advice = advise(cone)
        assert advice.action == "proceed"

    # PURPOSE: S-series + V > 0.2 → devil (stricter threshold)
    def test_s_series_moderate_dispersion_returns_devil(self):
        """S-series + V > 0.2 → devil (stricter threshold)."""
        cone = converge(
            Series.S,
            outputs={
                "S1": "マクロスケールで",
                "S2": "マイクロスケールで段階的に",
                "S3": "中規模の基準",
                "S4": "マクロスケールで実行",
            },
        )
        if cone.dispersion > 0.2:
            advice = advise(cone)
            assert advice.action == "devil"


# PURPOSE: devil_attack() のテスト — Cocone adversarial analysis
class TestDevilAttack:
    """devil_attack() のテスト — Cocone adversarial analysis."""

    # PURPOSE: 矛盾する出力 → 高 severity
    def test_contradictory_outputs_high_severity(self):
        """矛盾する出力 → 高 severity."""
        cone = converge(
            Series.O,
            outputs={
                "O1": "実装を中止すべき",
                "O2": "即座に実行を開始する",
                "O3": "根本的な再設計が必要",
                "O4": "現在の計画を継続する",
            },
        )
        attack = devil_attack(cone)
        assert isinstance(attack, DevilAttack)
        assert attack.severity > 0.5
        assert len(attack.contradictions) == 6  # C(4,2)
        assert len(attack.counterarguments) > 0
        assert len(attack.resolution_paths) == 3

    # PURPOSE: 整合する出力 → 低 severity
    def test_consistent_outputs_low_severity(self):
        """整合する出力 → 低 severity."""
        cone = converge(
            Series.O,
            outputs={
                "O1": "認識を深める",
                "O2": "認識を深めたい",
                "O3": "認識の深化を問う",
                "O4": "認識を深く実行",
            },
        )
        attack = devil_attack(cone)
        assert attack.severity <= 0.7

    # PURPOSE: worst_pair は最低類似度のペアを返す
    def test_worst_pair_is_least_similar(self):
        """worst_pair は最低類似度のペアを返す."""
        cone = converge(
            Series.S,
            outputs={
                "S1": "大きく",
                "S2": "小さく",
                "S3": "速く進める",
                "S4": "遅く止める",
            },
        )
        attack = devil_attack(cone)
        worst = attack.worst_pair
        assert worst is not None
        assert worst.similarity <= attack.contradictions[-1].similarity

    # PURPOSE: O-series → /noe+, /zet, PW の解消パスを提案
    def test_o_series_resolution_paths(self):
        """O-series → /noe+, /zet, PW の解消パスを提案."""
        cone = converge(
            Series.O,
            outputs={
                "O1": "中止",
                "O2": "実行",
                "O3": "再設計",
                "O4": "継続",
            },
        )
        attack = devil_attack(cone)
        assert any("/noe" in rp for rp in attack.resolution_paths)
        assert any("/zet" in rp for rp in attack.resolution_paths)

    # PURPOSE: S-series → /dia devil, PW の解消パスを提案
    def test_s_series_resolution_paths(self):
        """S-series → /dia devil, PW の解消パスを提案."""
        cone = converge(
            Series.S,
            outputs={
                "S1": "中止",
                "S2": "実行",
                "S3": "再設計",
                "S4": "継続",
            },
        )
        attack = devil_attack(cone)
        assert any("/dia" in rp for rp in attack.resolution_paths)

    # PURPOSE: 否定矛盾が検出される
    def test_negation_contradiction_detected(self):
        """否定矛盾が検出される."""
        cone = converge(
            Series.O,
            outputs={
                "O1": "実行しない",
                "O2": "実行する",
                "O3": "問題ない",
                "O4": "問題がある",
            },
        )
        attack = devil_attack(cone)
        neg_pairs = [c for c in attack.contradictions if "否定" in c.diagnosis]
        assert len(neg_pairs) > 0

    # PURPOSE: projection が1つの場合でもエラーにならない
    def test_empty_cone_graceful(self):
        """projection が1つの場合でもエラーにならない."""
        cone = converge(
            Series.O,
            outputs={"O1": "のみ"},
        )
        attack = devil_attack(cone)
        assert attack.severity == 0.0
        assert len(attack.contradictions) == 0

    # PURPOSE: DevilAttack の repr が読める
    def test_attack_repr(self):
        """DevilAttack の repr が読める."""
        cone = converge(
            Series.O,
            outputs={
                "O1": "a",
                "O2": "b",
                "O3": "c",
                "O4": "d",
            },
        )
        attack = devil_attack(cone)
        assert "DevilAttack" in repr(attack)
        assert "severity" in repr(attack)


# PURPOSE: ContradictionPair のテスト
class TestContradictionPair:
    """ContradictionPair のテスト."""

    # PURPOSE: repr をテストする
    def test_repr(self):
        """Verify repr behavior."""
        pair = ContradictionPair(
            theorem_a="O1",
            theorem_b="O2",
            similarity=0.25,
            output_a="test a",
            output_b="test b",
            diagnosis="テスト",
        )
        assert "O1↔O2" in repr(pair)
        assert "0.25" in repr(pair)
