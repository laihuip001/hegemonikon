
import pytest
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from mekhane.symploke.jules_client import JulesClient

@pytest.mark.asyncio
async def test_session_persistence():
    """Verify that _request creates and reuses an owned session."""

    # Mock aiohttp.ClientSession to verify it's instantiated only once
    with patch("aiohttp.ClientSession") as MockSession:
        # Mock request context manager
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"id": "test"}
        mock_response.ok = True
        # raise_for_status is synchronous in aiohttp
        mock_response.raise_for_status = MagicMock()

        mock_session_instance = MockSession.return_value
        # close() is async
        mock_session_instance.close = AsyncMock()
        mock_session_instance.request.return_value.__aenter__.return_value = mock_response

        client = JulesClient(api_key="test-key")

        # Verify initial state
        assert client._owned_session is None

        # First request
        await client._request("GET", "test")

        # Verify session created
        assert client._owned_session is not None
        assert client._owned_session is mock_session_instance
        assert MockSession.call_count == 1

        # Second request
        await client._request("GET", "test")

        # Verify session reused (call count shouldn't increase)
        assert MockSession.call_count == 1
        assert client._owned_session is mock_session_instance

        # Cleanup
        await client.close()
        mock_session_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_explicit_close():
    """Verify that close() cleans up the session."""
    with patch("aiohttp.ClientSession") as MockSession:
        mock_session_instance = MockSession.return_value
        mock_session_instance.close = AsyncMock()
        # Mock request stuff so _request doesn't fail
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"id": "test"}
        mock_response.ok = True
        mock_response.raise_for_status = MagicMock()
        mock_session_instance.request.return_value.__aenter__.return_value = mock_response

        client = JulesClient(api_key="test-key")

        # Trigger session creation
        await client._request("GET", "test")
        assert client._owned_session is not None

        # Close
        await client.close()
        assert client._owned_session is None
        mock_session_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_context_manager_uses_ensure_session():
    """Verify that context manager uses the new _ensure_session logic."""
    with patch("aiohttp.ClientSession") as MockSession:
        mock_session_instance = MockSession.return_value
        mock_session_instance.close = AsyncMock()

        client = JulesClient(api_key="test-key")

        async with client:
            assert client._owned_session is not None
            assert MockSession.call_count == 1

        assert client._owned_session is None
        mock_session_instance.close.assert_called_once()
