#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/ochema/tests/ テスト
# PURPOSE: OchemaService ユニットテスト
"""
OchemaService unit tests.

These tests verify the service layer's routing, singleton pattern,
and model registry without requiring actual LS or Cortex connections.
"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


# --- Singleton ---


class TestSingleton:
    """OchemaService singleton pattern tests."""

    def setup_method(self):
        """Reset singleton before each test."""
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    def teardown_method(self):
        """Reset singleton after each test."""
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    def test_singleton_identity(self):
        """get() returns the same instance."""
        from mekhane.ochema.service import OchemaService
        a = OchemaService.get()
        b = OchemaService.get()
        assert a is b

    def test_reset_clears_singleton(self):
        """reset() creates a fresh instance on next get()."""
        from mekhane.ochema.service import OchemaService
        a = OchemaService.get()
        OchemaService.reset()
        b = OchemaService.get()
        assert a is not b


# --- Model Routing ---


class TestModelRouting:
    """Model routing logic tests."""

    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()
        self.svc = OchemaService.get()

    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    def test_claude_sonnet_routes_to_ls(self):
        """claude-sonnet should route to LS."""
        assert self.svc._is_claude_model("claude-sonnet") is True

    def test_claude_opus_routes_to_ls(self):
        """claude-opus should route to LS."""
        assert self.svc._is_claude_model("claude-opus") is True

    def test_proto_model_routes_to_ls(self):
        """Proto enum models should route to LS."""
        assert self.svc._is_claude_model("MODEL_CLAUDE_4_5_SONNET_THINKING") is True
        assert self.svc._is_claude_model("MODEL_PLACEHOLDER_M26") is True

    def test_gemini_routes_to_cortex(self):
        """Gemini models should NOT route to LS."""
        assert self.svc._is_claude_model("gemini-2.0-flash") is False
        assert self.svc._is_claude_model("gemini-2.5-pro") is False
        assert self.svc._is_claude_model("gemini-3-pro-preview") is False

    def test_resolve_claude_friendly_name(self):
        """Friendly names resolve to proto enums."""
        assert self.svc._resolve_claude_model("claude-sonnet") == "MODEL_CLAUDE_4_5_SONNET_THINKING"
        assert self.svc._resolve_claude_model("claude-opus") == "MODEL_PLACEHOLDER_M26"

    def test_resolve_unknown_passes_through(self):
        """Unknown models pass through unchanged."""
        assert self.svc._resolve_claude_model("custom-model") == "custom-model"


# --- Models Registry ---


class TestModelsRegistry:
    """Model registry tests."""

    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()
        self.svc = OchemaService.get()

    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    def test_models_returns_dict(self):
        """models() returns expected structure."""
        result = self.svc.models()
        assert "models" in result
        assert "default" in result
        assert "ls_available" in result
        assert "cortex_available" in result

    def test_models_contains_all_providers(self):
        """Model registry includes Gemini, Cortex, and Claude models."""
        result = self.svc.models()
        models = result["models"]
        assert "gemini-2.0-flash" in models
        assert "cortex-gemini" in models
        assert "claude-sonnet" in models

    def test_default_model(self):
        """Default model is gemini-2.0-flash."""
        result = self.svc.models()
        assert result["default"] == "gemini-2.0-flash"


# --- Stream Validation ---


class TestStreamValidation:
    """Streaming API validation tests."""

    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()
        self.svc = OchemaService.get()

    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    def test_stream_rejects_claude_models(self):
        """stream() raises ValueError for Claude models."""
        with pytest.raises(ValueError, match="Streaming not supported"):
            list(self.svc.stream("hello", model="claude-sonnet"))

    def test_stream_rejects_proto_models(self):
        """stream() raises ValueError for proto enum models."""
        with pytest.raises(ValueError, match="Streaming not supported"):
            list(self.svc.stream("hello", model="MODEL_CLAUDE_4_5_SONNET_THINKING"))


# --- Constants ---


class TestConstants:
    """Verify exported constants."""

    def test_available_models_keys(self):
        from mekhane.ochema.service import AVAILABLE_MODELS
        expected = {
            "gemini-3-pro-preview", "gemini-3-flash-preview",
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash",
            "cortex-gemini", "claude-sonnet", "claude-opus",
        }
        assert set(AVAILABLE_MODELS.keys()) == expected

    def test_claude_model_map_keys(self):
        from mekhane.ochema.service import CLAUDE_MODEL_MAP
        assert "claude-sonnet" in CLAUDE_MODEL_MAP
        assert "claude-opus" in CLAUDE_MODEL_MAP

    def test_default_model_value(self):
        from mekhane.ochema.service import DEFAULT_MODEL
        assert DEFAULT_MODEL == "gemini-2.0-flash"


# --- Repr ---


class TestRepr:
    """OchemaService repr test."""

    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    def test_repr_format(self):
        from mekhane.ochema.service import OchemaService
        svc = OchemaService.get()
        r = repr(svc)
        assert "OchemaService(" in r
        assert "ls=" in r
        assert "cortex=" in r
