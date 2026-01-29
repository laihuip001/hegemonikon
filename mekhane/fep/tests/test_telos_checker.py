"""
Tests for K3 Telos Checker module

テスト項目:
1. AlignmentStatus の正常動作
2. check_alignment() の各状態テスト
3. ドリフトパターン検出
4. FEP 観察エンコード
"""

import pytest
from mekhane.fep.telos_checker import (
    AlignmentStatus,
    TelосResult,
    check_alignment,
    format_telos_markdown,
    encode_telos_observation,
    DRIFT_PATTERNS,
)


class TestAlignmentStatus:
    """AlignmentStatus enum tests"""
    
    def test_all_statuses_exist(self):
        assert AlignmentStatus.ALIGNED.value == "aligned"
        assert AlignmentStatus.DRIFTING.value == "drifting"
        assert AlignmentStatus.MISALIGNED.value == "misaligned"
        assert AlignmentStatus.INVERTED.value == "inverted"


class TestTelosResult:
    """TelосResult dataclass tests"""
    
    def test_is_aligned_for_aligned_status(self):
        result = TelосResult(
            status=AlignmentStatus.ALIGNED,
            alignment_score=0.9,
            goal="test goal",
            action="test action",
            rationale="test",
        )
        assert result.is_aligned is True
        assert result.needs_correction is False
    
    def test_is_aligned_for_drifting_status(self):
        result = TelосResult(
            status=AlignmentStatus.DRIFTING,
            alignment_score=0.6,
            goal="test goal",
            action="test action",
            rationale="test",
        )
        assert result.is_aligned is True  # Drifting is still considered aligned
        assert result.needs_correction is False
    
    def test_needs_correction_for_misaligned(self):
        result = TelосResult(
            status=AlignmentStatus.MISALIGNED,
            alignment_score=0.3,
            goal="test goal",
            action="test action",
            rationale="test",
        )
        assert result.is_aligned is False
        assert result.needs_correction is True
    
    def test_needs_correction_for_inverted(self):
        result = TelосResult(
            status=AlignmentStatus.INVERTED,
            alignment_score=0.1,
            goal="test goal",
            action="test action",
            rationale="test",
        )
        assert result.is_aligned is False
        assert result.needs_correction is True


class TestCheckAlignment:
    """check_alignment function tests"""
    
    def test_aligned_when_goal_and_action_match(self):
        result = check_alignment(
            goal="K3 Telos モジュールを実装する",
            action="telos_checker.py を作成する"
        )
        assert result.status == AlignmentStatus.ALIGNED
        assert result.alignment_score >= 0.7
        assert result.is_aligned
    
    def test_drifting_when_optimization_keyword_present(self):
        result = check_alignment(
            goal="ユーザー認証を実装する",
            action="認証コードを最適化してリファクタする"
        )
        # Should detect "最適化" and "リファクタ" as drift indicators
        assert len(result.drift_indicators) >= 1
    
    def test_detects_scope_creep_keywords(self):
        result = check_alignment(
            goal="ログイン機能を作る",
            action="ついでにダッシュボードも改善する"
        )
        # Should detect "ついでに" as scope creep
        assert any("ついでに" in ind for ind in result.drift_indicators)
    
    def test_detects_perfectionism_keywords(self):
        result = check_alignment(
            goal="基本的なCRUDを実装",
            action="完璧なエラーハンドリングを全てのケースで実装"
        )
        # Should detect perfectionism patterns
        assert len(result.drift_indicators) >= 1
    
    def test_returns_suggestions(self):
        result = check_alignment(
            goal="シンプルな機能を追加",
            action="完璧に最適化された実装を作る"
        )
        assert len(result.suggestions) > 0


class TestFormatTelosMarkdown:
    """format_telos_markdown tests"""
    
    def test_formats_aligned_result(self):
        result = TelосResult(
            status=AlignmentStatus.ALIGNED,
            alignment_score=0.9,
            goal="テスト目的",
            action="テスト行為",
            rationale="整合している",
            suggestions=["✅ このまま継続"],
        )
        markdown = format_telos_markdown(result)
        assert "✅" in markdown
        assert "ALIGNED" in markdown
        assert "90%" in markdown
    
    def test_formats_inverted_result(self):
        result = TelосResult(
            status=AlignmentStatus.INVERTED,
            alignment_score=0.1,
            goal="元の目的",
            action="手段化した行為",
            rationale="手段と目的が入れ替わっている",
            drift_indicators=["⚠️ 手段が目的化している"],
            suggestions=["🛑 手段と目的が入れ替わっています"],
        )
        markdown = format_telos_markdown(result)
        assert "🛑" in markdown
        assert "INVERTED" in markdown


class TestEncodeTelосObservation:
    """encode_telos_observation tests"""
    
    def test_encodes_aligned_result(self):
        result = TelосResult(
            status=AlignmentStatus.ALIGNED,
            alignment_score=0.9,
            goal="test",
            action="test",
            rationale="test",
        )
        obs = encode_telos_observation(result)
        assert obs["context_clarity"] == 0.9
        assert obs["urgency"] == 0.0  # No drift indicators
        assert obs["confidence"] == 0.9
    
    def test_encodes_drifting_result(self):
        result = TelосResult(
            status=AlignmentStatus.DRIFTING,
            alignment_score=0.6,
            goal="test",
            action="test",
            rationale="test",
            drift_indicators=["indicator1", "indicator2"],
        )
        obs = encode_telos_observation(result)
        assert obs["context_clarity"] == 0.6
        assert obs["urgency"] == 0.6  # 2 indicators * 0.3
        assert obs["confidence"] == 0.6
    
    def test_encodes_inverted_result(self):
        result = TelосResult(
            status=AlignmentStatus.INVERTED,
            alignment_score=0.1,
            goal="test",
            action="test",
            rationale="test",
            drift_indicators=["i1", "i2", "i3", "i4"],
        )
        obs = encode_telos_observation(result)
        assert obs["context_clarity"] == 0.1
        assert obs["urgency"] == 1.0  # Capped at 1.0
        assert obs["confidence"] == 0.1


class TestDriftPatterns:
    """DRIFT_PATTERNS configuration tests"""
    
    def test_all_patterns_have_required_fields(self):
        for pattern_id, pattern in DRIFT_PATTERNS.items():
            assert "description" in pattern
            assert "examples" in pattern
            assert "keywords" in pattern
            assert len(pattern["keywords"]) > 0
