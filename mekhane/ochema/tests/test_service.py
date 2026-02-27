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


# PURPOSE: OchemaService singleton pattern tests
class TestSingleton:
    """OchemaService singleton pattern tests."""

    # PURPOSE: Reset singleton before each test
    def setup_method(self):
        """Reset singleton before each test."""
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    # PURPOSE: Reset singleton after each test
    def teardown_method(self):
        """Reset singleton after each test."""
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    # PURPOSE: get() returns the same instance
    def test_singleton_identity(self):
        """get() returns the same instance."""
        from mekhane.ochema.service import OchemaService
        a = OchemaService.get()
        b = OchemaService.get()
        assert a is b

    # PURPOSE: reset() creates a fresh instance on next get()
    def test_reset_clears_singleton(self):
        """reset() creates a fresh instance on next get()."""
        from mekhane.ochema.service import OchemaService
        a = OchemaService.get()
        OchemaService.reset()
        b = OchemaService.get()
        assert a is not b


# --- Model Routing ---


# PURPOSE: Model routing logic tests
class TestModelRouting:
    """Model routing logic tests."""

    # PURPOSE: method をセットアップする
    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()
        self.svc = OchemaService.get()

    # PURPOSE: teardown_method の処理
    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    # PURPOSE: claude-sonnet should route to LS
    def test_claude_sonnet_routes_to_ls(self):
        """claude-sonnet should route to LS."""
        assert self.svc._is_claude_model("claude-sonnet") is True

    # PURPOSE: claude-opus should route to LS
    def test_claude_opus_routes_to_ls(self):
        """claude-opus should route to LS."""
        assert self.svc._is_claude_model("claude-opus") is True

    # PURPOSE: Proto enum models should route to LS
    def test_proto_model_routes_to_ls(self):
        """Proto enum models should route to LS."""
        assert self.svc._is_claude_model("MODEL_CLAUDE_4_5_SONNET_THINKING") is True
        assert self.svc._is_claude_model("MODEL_PLACEHOLDER_M26") is True

    # PURPOSE: Gemini models should NOT route to LS
    def test_gemini_routes_to_cortex(self):
        """Gemini models should NOT route to LS."""
        assert self.svc._is_claude_model("gemini-2.0-flash") is False
        assert self.svc._is_claude_model("gemini-2.5-pro") is False
        assert self.svc._is_claude_model("gemini-3-pro-preview") is False

    # PURPOSE: Friendly names resolve to model_config_id
    def test_resolve_model_config_id(self):
        """Friendly names resolve to model_config_id."""
        assert self.svc._resolve_model_config_id("claude-sonnet") == "claude-sonnet-4-5"
        assert self.svc._resolve_model_config_id("claude-opus") == "claude-opus-4-6"
        assert self.svc._resolve_model_config_id("claude-sonnet-4-5") == "claude-sonnet-4-5"

    # PURPOSE: Unknown models pass through unchanged
    def test_resolve_model_config_id_unknown_passes_through(self):
        """Unknown models pass through unchanged."""
        assert self.svc._resolve_model_config_id("custom-model") == "custom-model"

    # PURPOSE: Friendly names resolve to LS proto enums for fallback
    def test_resolve_ls_proto_model(self):
        """Friendly names resolve to LS proto enums for fallback."""
        assert self.svc._resolve_ls_proto_model("claude-sonnet") == "MODEL_CLAUDE_4_5_SONNET_THINKING"
        assert self.svc._resolve_ls_proto_model("claude-opus") == "MODEL_PLACEHOLDER_M26"
        assert self.svc._resolve_ls_proto_model("claude-sonnet-4-5") == "MODEL_CLAUDE_4_5_SONNET_THINKING"


# --- Models Registry ---


# PURPOSE: Model registry tests
class TestModelsRegistry:
    """Model registry tests."""

    # PURPOSE: method をセットアップする
    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()
        self.svc = OchemaService.get()

    # PURPOSE: teardown_method の処理
    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    # PURPOSE: models() returns expected structure
    def test_models_returns_dict(self):
        """models() returns expected structure."""
        result = self.svc.models()
        assert "models" in result
        assert "default" in result
        assert "ls_available" in result
        assert "cortex_available" in result

    # PURPOSE: Model registry includes Gemini, Cortex, and Claude models
    def test_models_contains_all_providers(self):
        """Model registry includes Gemini, Cortex, and Claude models."""
        result = self.svc.models()
        models = result["models"]
        assert "gemini-2.0-flash" in models
        assert "cortex-chat" in models
        assert "claude-sonnet" in models

    # PURPOSE: Default model is gemini-2.0-flash
    def test_default_model(self):
        """Default model is gemini-2.0-flash."""
        result = self.svc.models()
        assert result["default"] == "gemini-2.0-flash"


# --- Stream Validation ---


# PURPOSE: Streaming API validation tests
class TestStreamValidation:
    """Streaming API validation tests."""

    # PURPOSE: method をセットアップする
    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()
        self.svc = OchemaService.get()

    # PURPOSE: teardown_method の処理
    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    # PURPOSE: stream() routes Claude models to chat_stream()
    @patch("mekhane.ochema.service.OchemaService._get_cortex_client")
    def test_stream_claude_routes_to_chat_stream(self, mock_get_cortex):
        """stream() routes Claude models to chat_stream()."""
        mock_client = MagicMock()
        mock_client.chat_stream.return_value = iter(["Hello", " world"])
        mock_get_cortex.return_value = mock_client
        chunks = list(self.svc.stream("hello", model="claude-sonnet"))
        assert chunks == ["Hello", " world"]
        mock_client.chat_stream.assert_called_once_with(
            "hello", model="claude-sonnet-4-5", timeout=120.0,
            thinking_budget=None,
        )

    # PURPOSE: stream() routes proto enum Claude models to chat_stream()
    @patch("mekhane.ochema.service.OchemaService._get_cortex_client")
    def test_stream_proto_model_routes_to_chat_stream(self, mock_get_cortex):
        """stream() routes proto enum Claude models to chat_stream()."""
        mock_client = MagicMock()
        mock_client.chat_stream.return_value = iter(["Response"])
        mock_get_cortex.return_value = mock_client
        chunks = list(self.svc.stream("hello", model="MODEL_CLAUDE_4_5_SONNET_THINKING"))
        assert chunks == ["Response"]
        mock_client.chat_stream.assert_called_once()


# --- Constants ---


# PURPOSE: Verify exported constants
class TestConstants:
    """Verify exported constants."""

    # PURPOSE: available_models_keys をテストする
    def test_available_models_keys(self):
        from mekhane.ochema.service import AVAILABLE_MODELS
        expected = {
            "gemini-3-pro-preview", "gemini-3-flash-preview",
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash",
            "cortex-chat", "claude-sonnet", "claude-sonnet-4-5", "claude-opus",
        }
        assert set(AVAILABLE_MODELS.keys()) == expected

    # PURPOSE: claude_model_map_keys をテストする
    def test_claude_model_map_keys(self):
        from mekhane.ochema.service import CLAUDE_MODEL_MAP
        assert "claude-sonnet" in CLAUDE_MODEL_MAP
        assert "claude-opus" in CLAUDE_MODEL_MAP

    # PURPOSE: default_model_value をテストする
    def test_default_model_value(self):
        from mekhane.ochema.service import DEFAULT_MODEL
        assert DEFAULT_MODEL == "gemini-2.0-flash"


# --- Repr ---


# PURPOSE: OchemaService repr test
class TestRepr:
    """OchemaService repr test."""

    # PURPOSE: method をセットアップする
    def setup_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    # PURPOSE: teardown_method の処理
    def teardown_method(self):
        from mekhane.ochema.service import OchemaService
        OchemaService.reset()

    # PURPOSE: repr_format をテストする
    def test_repr_format(self):
        from mekhane.ochema.service import OchemaService
        svc = OchemaService.get()
        r = repr(svc)
        assert "OchemaService(" in r
        assert "ls=" in r
        assert "cortex=" in r
