# PROOF: [L3/Test] <- mekhane/ergasterion/tekhne/tests/ A0→AutoFix→test_thinking_config
"""Tests for thinking config resolution (HGK depth -> model params)."""

import pytest
from mekhane.ergasterion.tekhne.pipeline import (
    DEPTH_TO_CLAUDE,
    DEPTH_TO_GEMINI,
    resolve_thinking_config,
)


class TestResolveThinkingConfig:
    """Test resolve_thinking_config for all depth x model combinations."""

    # --- Gemini family ---

    def test_gemini_l0(self):
        result = resolve_thinking_config("gemini-3-pro", "L0")
        assert result == {"thinkingLevel": "minimal", "verbosity": "concise"}

    def test_gemini_l1(self):
        result = resolve_thinking_config("gemini-3-flash", "L1")
        assert result == {"thinkingLevel": "low", "verbosity": "concise"}

    def test_gemini_l2(self):
        result = resolve_thinking_config("gemini-2.0-flash", "L2")
        assert result == {"thinkingLevel": "medium", "verbosity": "standard"}

    def test_gemini_l3(self):
        result = resolve_thinking_config("gemini-3-pro", "L3")
        assert result == {"thinkingLevel": "high", "verbosity": "detailed"}

    # --- Claude family ---

    def test_claude_l0(self):
        result = resolve_thinking_config("claude-opus-4.6", "L0")
        assert result == {"effort": "low", "thinking_type": "adaptive"}

    def test_claude_l1(self):
        result = resolve_thinking_config("claude-sonnet-4.5", "L1")
        assert result == {"effort": "low", "thinking_type": "adaptive"}

    def test_claude_l2(self):
        result = resolve_thinking_config("claude-opus-4.6", "L2")
        assert result == {"effort": "high", "thinking_type": "adaptive"}

    def test_claude_l3(self):
        result = resolve_thinking_config("claude-opus-4.6", "L3")
        assert result == {"effort": "max", "thinking_type": "adaptive"}

    # --- Edge cases ---

    def test_unknown_depth_defaults_to_l2(self):
        result = resolve_thinking_config("gemini-3-pro", "L5")
        assert result == DEPTH_TO_GEMINI["L2"]

    def test_lowercase_depth(self):
        result = resolve_thinking_config("gemini-3-pro", "l3")
        assert result == DEPTH_TO_GEMINI["L3"]

    def test_unknown_model_uses_gemini_fallback(self):
        result = resolve_thinking_config("gpt-4.1", "L2")
        assert result == DEPTH_TO_GEMINI["L2"]

    def test_default_depth_is_l2(self):
        result = resolve_thinking_config("gemini-3-pro")
        assert result == DEPTH_TO_GEMINI["L2"]


class TestPipelineConfigThinking:
    """Test PipelineConfig.thinking_config property."""

    def test_default_config(self):
        from mekhane.ergasterion.tekhne.pipeline import PipelineConfig
        config = PipelineConfig()
        tc = config.thinking_config
        # Default model is gemini-2.0-flash, default depth is L2
        assert tc["thinkingLevel"] == "medium"
        assert tc["verbosity"] == "standard"

    def test_claude_config(self):
        from mekhane.ergasterion.tekhne.pipeline import PipelineConfig
        config = PipelineConfig(model="claude-opus-4.6", hgk_depth="L3")
        tc = config.thinking_config
        assert tc["effort"] == "max"
        assert tc["thinking_type"] == "adaptive"
