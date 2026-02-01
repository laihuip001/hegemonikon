# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要
"""Tests for encoding.py - Text-to-Observation encoding."""

import pytest
from mekhane.fep.encoding import (
    encode_input,
    encode_structured_input,
    decode_observation,
    analyze_context,
    analyze_urgency,
    analyze_confidence,
)


class TestAnalyzeContext:
    """Test context clarity analysis."""

    def test_clear_with_code_reference(self):
        """Code/file references indicate clear context."""
        assert analyze_context("fep_agent.pyを修正して") == "clear"

    def test_clear_with_code_block(self):
        """Code blocks indicate clear context."""
        text = "```python\nprint('hello')\n```"
        assert analyze_context(text) == "clear"

    def test_ambiguous_with_vague_words(self):
        """Vague words indicate ambiguous context."""
        assert analyze_context("なんかうまくいかない") == "ambiguous"

    def test_ambiguous_default(self):
        """Short unclear text defaults to ambiguous."""
        assert analyze_context("???") == "ambiguous"


class TestAnalyzeUrgency:
    """Test urgency level analysis."""

    def test_high_with_urgent_keyword(self):
        """Urgent keywords indicate high urgency."""
        assert analyze_urgency("緊急！今すぐ対応して") == "high"

    def test_high_with_error(self):
        """Error/bug mentions indicate high urgency."""
        assert analyze_urgency("バグがあります") == "high"

    def test_medium_with_today(self):
        """Today references indicate medium urgency."""
        assert analyze_urgency("今日中にやりたい") == "medium"

    def test_low_with_explore(self):
        """Exploratory language indicates low urgency."""
        assert analyze_urgency("アイデアを検討したい") == "low"

    def test_low_default(self):
        """No urgency indicators defaults to low."""
        assert analyze_urgency("ファイルを作成して") == "low"


class TestAnalyzeConfidence:
    """Test confidence level analysis."""

    def test_high_with_yes(self):
        """Simple approval indicates high confidence."""
        assert analyze_confidence("y") == "high"
        assert analyze_confidence("はい") == "high"

    def test_high_with_execute(self):
        """Execute commands indicate high confidence."""
        assert analyze_confidence("やって") == "high"

    def test_medium_with_continue(self):
        """Continue implies medium confidence."""
        assert analyze_confidence("続けよう") == "medium"

    def test_low_with_question(self):
        """Questions indicate low confidence."""
        assert analyze_confidence("どう思う?") == "low"

    def test_medium_default(self):
        """No confidence indicators defaults to medium."""
        assert analyze_confidence("ファイルを確認した") == "medium"


class TestEncodeInput:
    """Test main encode_input function."""

    def test_urgent_code_fix(self):
        """Urgent code fix: clear, high urgency, medium confidence."""
        obs = encode_input("緊急：fep_agent.pyのバグを修正して")
        assert obs[0] == 1  # clear (code reference)
        assert obs[1] == 2  # high (緊急, バグ)

    def test_simple_approval(self):
        """Simple 'y' approval."""
        obs = encode_input("y")
        assert obs[2] == 2  # high confidence

    def test_exploratory_question(self):
        """Exploratory question: low urgency, low confidence."""
        obs = encode_input("なんかいい方法ある?")
        assert obs[0] == 0  # ambiguous (なんか)
        assert obs[2] == 0  # low (question mark)

    def test_returns_tuple(self):
        """encode_input returns 3-tuple."""
        obs = encode_input("test")
        assert isinstance(obs, tuple)
        assert len(obs) == 3


class TestEncodeStructuredInput:
    """Test explicit observation encoding."""

    def test_explicit_values(self):
        """Explicit values are encoded correctly."""
        obs = encode_structured_input(
            context="clear",
            urgency="high",
            confidence="high",
        )
        assert obs == (1, 2, 2)

    def test_defaults(self):
        """Defaults: ambiguous, low, medium."""
        obs = encode_structured_input()
        assert obs == (0, 0, 1)


class TestDecodeObservation:
    """Test observation decoding."""

    def test_decode_roundtrip(self):
        """Decode returns human-readable format."""
        obs = (1, 2, 0)
        decoded = decode_observation(obs)
        assert decoded["context"] == "clear"
        assert decoded["urgency"] == "high"
        assert decoded["confidence"] == "low"
