"""
Tests for JulesClient
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os
from mekhane.symploke.jules_client import JulesClient

class TestJulesClient:

    def test_init_with_arg(self):
        client = JulesClient(api_key="arg_key")
        assert client.api_key == "arg_key"

    def test_init_with_env(self, monkeypatch):
        monkeypatch.setenv("JULIUS_API_KEY", "test_env_key")
        client = JulesClient()
        assert client.api_key == "test_env_key"

    def test_init_missing_key(self, monkeypatch):
        monkeypatch.delenv("JULIUS_API_KEY", raising=False)
        with pytest.raises(ValueError):
            JulesClient()

    @pytest.mark.asyncio
    async def test_create_session(self):
        client = JulesClient(api_key="test")

        mock_response = {"name": "sessions/123", "state": "ACTIVE"}

        with patch("aiohttp.ClientSession.post") as mock_post:
            # Mock the context manager and response
            mock_context = mock_post.return_value.__aenter__.return_value
            mock_context.json = AsyncMock(return_value=mock_response)
            mock_context.raise_for_status = MagicMock()

            result = await client.create_session(prompt="Do work")
            assert result == mock_response

            # Verify payload
            args, kwargs = mock_post.call_args
            assert kwargs["json"]["prompt"] == "Do work"
            assert kwargs["headers"]["X-Goog-Api-Key"] == "test"

    @pytest.mark.asyncio
    async def test_list_sessions(self):
        client = JulesClient(api_key="test")
        mock_response = {"sessions": []}

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_context = mock_get.return_value.__aenter__.return_value
            mock_context.json = AsyncMock(return_value=mock_response)
            mock_context.raise_for_status = MagicMock()

            result = await client.list_sessions()
            assert result == mock_response
