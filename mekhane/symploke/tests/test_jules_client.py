#!/usr/bin/env python3
"""
Tests for Jules Client

Run with:
    .venv/bin/python -m pytest mekhane/symploke/tests/test_jules_client.py -v
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
import os

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mekhane.symploke.jules_client import (
    JulesClient,
    JulesSession,
    SessionState,
    RateLimitError
)


class TestJulesClient:
    """Test suite for JulesClient."""
    
    def test_init_with_key(self):
        """Test client initialization with API key."""
        client = JulesClient(api_key="test-key-123")
        assert client.api_key == "test-key-123"
        assert "X-Goog-Api-Key" in client._headers
        assert client._session is None
    
    def test_init_without_key_raises(self):
        """Test that init without key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                JulesClient()
    
    def test_init_from_env(self):
        """Test client initialization from environment variable."""
        with patch.dict('os.environ', {'JULES_API_KEY': 'env-key-456'}):
            client = JulesClient()
            assert client.api_key == 'env-key-456'


class TestSessionState:
    """Test session state enum."""
    
    def test_all_states_defined(self):
        """Verify all expected states are defined."""
        states = [s.value for s in SessionState]
        assert 'PLANNING' in states
        assert 'IMPLEMENTING' in states
        assert 'TESTING' in states
        assert 'COMPLETED' in states
        assert 'FAILED' in states
        assert 'UNKNOWN' in states


class TestJulesSession:
    """Test JulesSession dataclass."""
    
    def test_session_creation(self):
        """Test creating a session object."""
        session = JulesSession(
            id="test-123",
            name="sessions/test-123",
            state=SessionState.PLANNING,
            prompt="Fix bug",
            source="sources/github/owner/repo"
        )
        assert session.id == "test-123"
        assert session.state == SessionState.PLANNING
        assert session.pull_request_url is None
    
    def test_session_with_pr(self):
        """Test session with PR URL."""
        session = JulesSession(
            id="test-456",
            name="sessions/test-456",
            state=SessionState.COMPLETED,
            prompt="Add feature",
            source="sources/github/owner/repo",
            pull_request_url="https://github.com/owner/repo/pull/123"
        )
        assert session.pull_request_url == "https://github.com/owner/repo/pull/123"


class TestCreateSession:
    """Test create_session method with mocks."""
    
    @pytest.mark.asyncio
    async def test_create_session_success(self):
        """Test successful session creation."""
        client = JulesClient(api_key="test-key")

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json.return_value = {
            "id": "sess-123",
            "name": "sessions/sess-123",
            "state": "PLANNING"
        }
        mock_resp.raise_for_status = MagicMock()

        # Mock aiohttp.ClientSession
        mock_session = AsyncMock()
        # session.post() returns a context manager, not a coroutine
        mock_session.post = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = mock_resp
        mock_session.post.return_value.__aexit__.return_value = None

        # Setup context manager mocks for the session itself
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        with patch("aiohttp.ClientSession", return_value=mock_session):
            session = await client.create_session("prompt", "source")

            assert session.id == "sess-123"
            assert session.state == SessionState.PLANNING
            mock_session.post.assert_called_once()


class TestContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self):
        client = JulesClient(api_key="test")
        assert client._session is None

        with patch("aiohttp.ClientSession") as mock_cls:
            mock_instance = AsyncMock()
            mock_instance.closed = False
            mock_cls.return_value = mock_instance

            async with client as c:
                assert c._session == mock_instance
                mock_cls.assert_called_once()

            assert c._session is None
            mock_instance.close.assert_called_once()


class TestPollSession:
    """Test poll_session method."""

    @pytest.mark.asyncio
    async def test_poll_session_retry_on_network_error(self):
        """Test that poll_session retries on ClientError."""
        client = JulesClient(api_key="test")

        completed_session = JulesSession(
            id="1",
            name="1",
            state=SessionState.COMPLETED,
            prompt="",
            source=""
        )

        with patch.object(client, 'get_session', new_callable=AsyncMock) as mock_get:
            # Fail once with network error, then succeed
            mock_get.side_effect = [
                aiohttp.ClientError("Network error"),
                completed_session
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                result = await client.poll_session("1", timeout=10)

                assert result.state == SessionState.COMPLETED
                assert mock_get.call_count == 2
                # Verify sleep was called (backoff)
                assert mock_sleep.call_count >= 1

    @pytest.mark.asyncio
    async def test_poll_session_unknown_state_warning(self):
        """Test that unknown state logs warning and continues."""
        client = JulesClient(api_key="test")

        unknown_session = JulesSession(id="1", name="1", state=SessionState.UNKNOWN, prompt="", source="")
        completed_session = JulesSession(id="1", name="1", state=SessionState.COMPLETED, prompt="", source="")

        with patch.object(client, 'get_session', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [unknown_session, completed_session]

            with patch("builtins.print") as mock_print:
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    await client.poll_session("1", timeout=10)

                    # Verify warning was printed
                    args, _ = mock_print.call_args_list[0]
                    assert "Warning: Unknown session state" in args[0]


class TestBatchExecute:
    """Test batch_execute method."""
    
    @pytest.mark.asyncio
    async def test_empty_tasks_list(self):
        """Test batch execute with empty list."""
        client = JulesClient(api_key="test-key")
        
        with patch.object(client, 'create_and_poll', new_callable=AsyncMock) as mock:
            results = await client.batch_execute([])
            assert results == []
            mock.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
