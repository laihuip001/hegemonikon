#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/ochema/tests/ テスト
# PURPOSE: CortexClient chat API ユニットテスト
"""
CortexClient chat(), chat_stream(), ChatConversation unit tests.

Tests use mock _call_api to avoid external API calls.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

from mekhane.ochema.cortex_client import CortexClient, ChatConversation
from mekhane.ochema.types import LLMResponse


# --- Fixtures ---

def _make_client():
    """Create a CortexClient with mocked auth."""
    with patch.object(CortexClient, '_get_token', return_value='mock-token'), \
         patch.object(CortexClient, '_get_project', return_value='mock-project'):
        client = CortexClient()
    return client


def _mock_chat_response(text="Hello!", cid="abc123", tid="def456", model_config=None):
    """Create a mock generateChat response dict."""
    resp = {
        "markdown": text,
        "processingDetails": {"cid": cid, "tid": tid},
    }
    if model_config:
        resp["modelConfig"] = model_config
    return resp


# --- chat() Tests ---


# PURPOSE: CortexClient.chat() unit tests
class TestChat:
    """CortexClient.chat() unit tests."""

    # PURPOSE: chat() returns LLMResponse with text and model
    def test_chat_basic_response(self):
        """chat() returns LLMResponse with text and model."""
        client = _make_client()
        mock_resp = _mock_chat_response("56")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp):
            result = client.chat("What is 7*8?")

        assert isinstance(result, LLMResponse)
        assert result.text == "56"
        assert "abc123" in result.cascade_id

    # PURPOSE: chat() passes history to _call_api payload
    def test_chat_with_history(self):
        """chat() passes history to _call_api payload."""
        client = _make_client()
        mock_resp = _mock_chat_response("I remember")
        history = [
            {"author": 1, "content": "My name is Alice"},
            {"author": 2, "content": "Nice to meet you Alice"},
        ]

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp) as mock_call:
            result = client.chat("What is my name?", history=history)

        # Verify history was passed in the payload
        call_args = mock_call.call_args
        payload = call_args[0][1]  # second positional arg
        assert payload["history"] == history
        assert result.text == "I remember"

    # PURPOSE: chat() includes tier_id in payload when set
    def test_chat_with_tier_id(self):
        """chat() includes tier_id in payload when set."""
        client = _make_client()
        mock_resp = _mock_chat_response("Premium response")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp) as mock_call:
            client.chat("hello", tier_id="g1-ultra-tier")

        payload = mock_call.call_args[0][1]
        assert payload["tier_id"] == "g1-ultra-tier"

    # PURPOSE: chat(model=...) includes model_config_id in payload
    def test_chat_with_model_config_id(self):
        """chat(model=...) includes model_config_id in payload."""
        client = _make_client()
        mock_resp = _mock_chat_response("Claude response")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp) as mock_call:
            client.chat("hello", model="claude-sonnet-4-5")

        payload = mock_call.call_args[0][1]
        assert payload["model_config_id"] == "claude-sonnet-4-5"

    # PURPOSE: chat() without model omits model_config_id from payload
    def test_chat_without_model_no_config_id(self):
        """chat() without model omits model_config_id from payload."""
        client = _make_client()
        mock_resp = _mock_chat_response("Default response")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp) as mock_call:
            client.chat("hello")

        payload = mock_call.call_args[0][1]
        assert "model_config_id" not in payload


# --- _parse_chat_response Tests ---


# PURPOSE: _parse_chat_response unit tests
class TestParseChatResponse:
    """_parse_chat_response unit tests."""

    # PURPOSE: Basic response without modelConfig uses fallback
    def test_basic_parse(self):
        """Basic response without modelConfig uses fallback."""
        client = _make_client()
        resp = _mock_chat_response("Hello", cid="test-cid")
        result = client._parse_chat_response(resp)

        assert result.text == "Hello"
        assert "cortex-chat" in result.model
        assert "test-cid" in result.model

    # PURPOSE: modelConfig.displayName is preferred when present
    def test_model_config_display_name(self):
        """modelConfig.displayName is preferred when present."""
        client = _make_client()
        resp = _mock_chat_response(
            "Hello",
            model_config={"displayName": "Gemini 3 Pro", "id": "gemini-3-pro"},
        )
        result = client._parse_chat_response(resp)
        assert result.model == "Gemini 3 Pro"

    # PURPOSE: modelConfig.id is used when displayName is absent
    def test_model_config_id_fallback(self):
        """modelConfig.id is used when displayName is absent."""
        client = _make_client()
        resp = _mock_chat_response(
            "Hello",
            model_config={"id": "gemini-3-pro-preview"},
        )
        result = client._parse_chat_response(resp)
        assert result.model == "gemini-3-pro-preview"

    # PURPOSE: Falls back to cid-based name when no modelConfig and no request_model
    def test_no_model_config_fallback(self):
        """Falls back to cid-based name when no modelConfig and no request_model."""
        client = _make_client()
        resp = _mock_chat_response("Hello", cid="xyz")
        result = client._parse_chat_response(resp)
        assert result.model == "cortex-chat (cid=xyz)"

    # PURPOSE: request_model resolves via _MODEL_DISPLAY_NAMES when no modelConfig
    def test_request_model_display_name_mapping(self):
        """request_model resolves via _MODEL_DISPLAY_NAMES when no modelConfig."""
        client = _make_client()
        resp = _mock_chat_response("Hello", cid="abc")
        result = client._parse_chat_response(resp, request_model="claude-sonnet-4-5")
        assert result.model == "Claude Sonnet 4.5"

    # PURPOSE: request_model used as-is when not in _MODEL_DISPLAY_NAMES
    def test_request_model_raw_fallback(self):
        """request_model used as-is when not in _MODEL_DISPLAY_NAMES."""
        client = _make_client()
        resp = _mock_chat_response("Hello", cid="abc")
        result = client._parse_chat_response(resp, request_model="unknown-model-x")
        assert result.model == "unknown-model-x"

    # PURPOSE: modelConfig.displayName beats request_model
    def test_model_config_takes_priority_over_request_model(self):
        """modelConfig.displayName beats request_model."""
        client = _make_client()
        resp = _mock_chat_response(
            "Hello",
            model_config={"displayName": "Server Model Name"},
        )
        result = client._parse_chat_response(resp, request_model="claude-sonnet-4-5")
        assert result.model == "Server Model Name"


# --- ChatConversation Tests ---


# PURPOSE: ChatConversation multi-turn tests
class TestChatConversation:
    """ChatConversation multi-turn tests."""

    # PURPOSE: Each send() increments turn count
    def test_turn_count_increments(self):
        """Each send() increments turn count."""
        client = _make_client()
        mock_resp = _mock_chat_response("OK")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp):
            conv = client.start_chat()
            assert conv.turn_count == 0

            conv.send("Turn 1")
            assert conv.turn_count == 1

            conv.send("Turn 2")
            assert conv.turn_count == 2

    # PURPOSE: History grows with each send()
    def test_history_accumulates(self):
        """History grows with each send()."""
        client = _make_client()
        mock_resp = _mock_chat_response("Reply")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp):
            conv = client.start_chat()
            conv.send("Hello")
            conv.send("How are you?")

        history = conv.history
        assert len(history) == 4  # 2 user + 2 model
        assert history[0] == {"author": 1, "content": "Hello"}
        assert history[1] == {"author": 2, "content": "Reply"}
        assert history[2] == {"author": 1, "content": "How are you?"}
        assert history[3] == {"author": 2, "content": "Reply"}

    # PURPOSE: close() resets turn count and history
    def test_close_clears_state(self):
        """close() resets turn count and history."""
        client = _make_client()
        mock_resp = _mock_chat_response("Reply")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp):
            conv = client.start_chat()
            conv.send("Hello")

        conv.close()
        assert conv.turn_count == 0
        assert conv.history == []

    # PURPOSE: history property returns a copy, not internal reference
    def test_history_is_readonly_copy(self):
        """history property returns a copy, not internal reference."""
        client = _make_client()
        mock_resp = _mock_chat_response("Reply")

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch.object(client, '_call_api', return_value=mock_resp):
            conv = client.start_chat()
            conv.send("Hello")

        h1 = conv.history
        h2 = conv.history
        assert h1 is not h2  # different list objects
        assert h1 == h2  # same content


# --- chat_stream() Tests ---


# PURPOSE: CortexClient.chat_stream() unit tests
class TestChatStream:
    """CortexClient.chat_stream() unit tests."""

    # PURPOSE: chat_stream() correctly parses JSON array response
    def test_json_array_parsing(self):
        """chat_stream() correctly parses JSON array response."""
        client = _make_client()
        json_array = json.dumps([
            {"markdown": "chunk1"},
            {"markdown": "chunk2"},
            {"markdown": "chunk3"},
        ])

        mock_resp = MagicMock()
        mock_resp.read.return_value = json_array.encode("utf-8")
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch('urllib.request.urlopen', return_value=mock_resp):
            chunks = list(client.chat_stream("hello"))

        assert chunks == ["chunk1", "chunk2", "chunk3"]

    # PURPOSE: chat_stream() handles single JSON object (non-array)
    def test_single_object_parsing(self):
        """chat_stream() handles single JSON object (non-array)."""
        client = _make_client()
        json_obj = json.dumps({"markdown": "single response"})

        mock_resp = MagicMock()
        mock_resp.read.return_value = json_obj.encode("utf-8")
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch('urllib.request.urlopen', return_value=mock_resp):
            chunks = list(client.chat_stream("hello"))

        assert chunks == ["single response"]

    # PURPOSE: chat_stream() skips items with empty markdown
    def test_empty_markdown_skipped(self):
        """chat_stream() skips items with empty markdown."""
        client = _make_client()
        json_array = json.dumps([
            {"markdown": "content"},
            {"markdown": ""},
            {"markdown": "more content"},
        ])

        mock_resp = MagicMock()
        mock_resp.read.return_value = json_array.encode("utf-8")
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch.object(client, '_get_token', return_value='mock-token'), \
             patch.object(client, '_get_project', return_value='mock-project'), \
             patch('urllib.request.urlopen', return_value=mock_resp):
            chunks = list(client.chat_stream("hello"))

        assert chunks == ["content", "more content"]
