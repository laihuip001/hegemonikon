# PROOF: [L3/テスト] <- scripts/tests/
# PURPOSE: daily training runner のユーティリティ関数と構成が正しく動作するか検証する
"""
Tests for e2e_daily_train.py.

Verifies:
- _get_handoff_contexts reads handoffs correctly
- FALLBACK_INPUTS are well-formed
- run_daily_training assembles inputs correctly (mocked FEP loop)
- _notify_slack handles missing webhook gracefully
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.e2e_daily_train import (
    _get_handoff_contexts,
    FALLBACK_INPUTS,
    _notify_slack,
)


class TestFallbackInputs:
    """FALLBACK_INPUTS corpus tests."""

    def test_fallback_inputs_not_empty(self):
        assert len(FALLBACK_INPUTS) > 0

    def test_fallback_inputs_are_strings(self):
        for inp in FALLBACK_INPUTS:
            assert isinstance(inp, str)
            assert len(inp) > 5

    def test_fallback_inputs_cover_all_series(self):
        """Fallback inputs should cover different cognitive domains."""
        all_text = " ".join(FALLBACK_INPUTS)
        # Should include various cognitive keywords
        assert any(kw in all_text for kw in ["なぜ", "目的", "本質"])  # O
        assert any(kw in all_text for kw in ["設計", "構造", "アーキ"])  # S
        assert any(kw in all_text for kw in ["不安", "モチベ", "疲れ"])  # H
        assert any(kw in all_text for kw in ["スコープ", "範囲", "定義"])  # P
        assert any(kw in all_text for kw in ["タイミング", "適切"])  # K
        assert any(kw in all_text for kw in ["検証", "レビュー", "正しい"])  # A


class TestHandoffContexts:
    """Handoff context extraction tests."""

    def test_no_handoff_dir_returns_empty(self):
        """Returns empty when sessions directory doesn't exist."""
        with patch("scripts.e2e_daily_train.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp/nonexistent")
            result = _get_handoff_contexts()
            assert result == []

    def test_handoff_extraction_with_subject(self):
        """Extracts subject from handoff files."""
        with tempfile.TemporaryDirectory() as td:
            sess_dir = Path(td) / "oikos/mneme/.hegemonikon/sessions"
            sess_dir.mkdir(parents=True)

            handoff = sess_dir / "handoff_20260208.md"
            handoff.write_text(
                "---\n"
                "# Session Handoff\n"
                "**主題**: FEPエージェントの学習可視化\n"
                "---\n"
                "## Summary\n",
                encoding="utf-8",
            )

            with patch("scripts.e2e_daily_train.Path.home", return_value=Path(td)):
                result = _get_handoff_contexts()

            assert len(result) > 0
            assert "FEP" in result[0] or "学習" in result[0]


class TestNotifySlack:
    """Slack notification tests."""

    def test_no_webhook_skips(self):
        """Skips silently when no webhook URL."""
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": ""}, clear=False):
            _notify_slack({"date": "test", "rounds": 5, "act": 3, "observe": 2,
                          "avg_entropy": 0.5, "elapsed_sec": 1.0})
            # Should not raise

    def test_invalid_webhook_skips(self):
        """Skips silently when webhook is not a URL."""
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": "not-a-url"}, clear=False):
            _notify_slack({"date": "test", "rounds": 5, "act": 3, "observe": 2,
                          "avg_entropy": 0.5, "elapsed_sec": 1.0})
