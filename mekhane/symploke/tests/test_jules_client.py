#!/usr/bin/env python3
"""
Tests for Jules Client

Run with:
    .venv/bin/python -m pytest mekhane/symploke/tests/test_jules_client.py -v
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

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

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test usage as context manager."""
        with patch('aiohttp.ClientSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value = mock_session
            mock_session.close = AsyncMock()

            async with JulesClient(api_key="test") as client:
                assert client._session is not None
                assert client._session == mock_session

            # Verify close called
            mock_session.close.assert_called_once()


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

    def test_parse_state_unknown(self):
        """Verify parse_state returns UNKNOWN for invalid input."""
        from mekhane.symploke.jules_client import parse_state
        assert parse_state("INVALID_STATE_XYZ") == SessionState.UNKNOWN
        assert parse_state("random string") == SessionState.UNKNOWN


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
    @pytest.mark.skip(reason="Requires aioresponses for proper async mocking")
    async def test_create_session_success(self):
        """Test successful session creation."""
        # TODO: Use aioresponses for proper async HTTP mocking
        pass


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

    @pytest.mark.asyncio
    async def test_cancellation_propagation(self):
        """Test that CancelledError is propagated."""
        client = JulesClient(api_key="test-key")

        with patch.object(client, 'create_and_poll', side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await client.batch_execute([{"prompt": "p", "source": "s"}])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
