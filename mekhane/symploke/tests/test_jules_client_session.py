import pytest
import aiohttp
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock
from mekhane.symploke.jules_client import JulesClient

@pytest.mark.asyncio
async def test_context_manager_usage():
    """Test using JulesClient as a context manager."""
    with patch("aiohttp.ClientSession") as MockSession:
        # ClientSession instance should be MagicMock so methods aren't auto-async
        mock_session_instance = MagicMock()
        mock_session_instance.close = AsyncMock()

        # Context manager support
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)

        MockSession.return_value = mock_session_instance

        async with JulesClient(api_key="test-key") as client:
            assert client._session is not None
            assert client._session is mock_session_instance

            # Verify session was created
            MockSession.assert_called_once()

        # Verify session was closed
        mock_session_instance.close.assert_called_once()
        assert client._session is None

@pytest.mark.asyncio
async def test_persistent_session_reuse():
    """Test that requests reuse the session when in context manager."""
    with patch("aiohttp.ClientSession") as MockSession:
        mock_session_instance = MagicMock()
        mock_session_instance.close = AsyncMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        # Ensure 'closed' property is False so the check passes
        mock_session_instance.closed = False

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        # json() is a coroutine
        mock_response.json = AsyncMock(return_value={"id": "123", "name": "test-session", "state": "PLANNING"})
        mock_response.raise_for_status = MagicMock()

        # request() returns an async context manager
        mock_request_ctx = MagicMock()
        mock_request_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_request_ctx.__aexit__ = AsyncMock(return_value=None)

        # session.request is synchronous, returning the context manager
        mock_session_instance.request.return_value = mock_request_ctx

        MockSession.return_value = mock_session_instance

        async with JulesClient(api_key="test-key") as client:
            # First request
            await client.create_session("prompt", "source")

            # Second request
            await client.get_session("123")

            # Should have created session only once (JulesClient instantiation)
            MockSession.assert_called_once()

            # Should have called request 2 times on the same session
            assert mock_session_instance.request.call_count == 2

@pytest.mark.asyncio
async def test_backward_compatibility():
    """Test that requests create new session when NOT in context manager."""
    with patch("aiohttp.ClientSession") as MockSession:
        mock_session_instance = MagicMock()
        mock_session_instance.close = AsyncMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.closed = False

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"id": "123", "name": "test-session", "state": "PLANNING"})
        mock_response.raise_for_status = MagicMock()

        mock_request_ctx = MagicMock()
        mock_request_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_request_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance.request.return_value = mock_request_ctx

        MockSession.return_value = mock_session_instance

        client = JulesClient(api_key="test-key")

        # First request
        await client.create_session("prompt", "source")

        # Second request
        await client.get_session("123")

        # Should have created session 2 times (once per request)
        assert MockSession.call_count == 2
