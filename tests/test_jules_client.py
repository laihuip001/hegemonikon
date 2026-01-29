import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
from mekhane.symploke.jules_client import JulesClient, SessionState, RateLimitError
import aiohttp

class TestJulesClient(unittest.IsolatedAsyncioTestCase):
    async def test_session_persistence(self):
        """Test that the session is reused across requests."""
        api_key = "test_key"
        async with JulesClient(api_key) as client:
            # Mock the session
            mock_session = AsyncMock(spec=aiohttp.ClientSession)
            mock_session.closed = False
            client._session = mock_session

            # Mock post response
            mock_response = AsyncMock()
            mock_response.status = 200
            # raise_for_status is sync
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {
                "id": "123", "name": "test", "state": "PLANNING"
            }
            mock_session.post.return_value.__aenter__.return_value = mock_response

            # Mock get response
            mock_get_response = AsyncMock()
            mock_get_response.status = 200
            mock_get_response.raise_for_status = MagicMock()
            mock_get_response.json.return_value = {
                "id": "123", "name": "test", "state": "COMPLETED"
            }
            mock_session.get.return_value.__aenter__.return_value = mock_get_response

            # Call create_session
            await client.create_session("prompt", "source")

            # Call get_session
            await client.get_session("123")

            # Check usage
            mock_session.post.assert_called_once()
            mock_session.get.assert_called_once()
            # Verify we are using the SAME session object
            self.assertEqual(client._session, mock_session)

    async def test_poll_retry_on_503(self):
        """Test that poll_session retries on 503 error."""
        api_key = "test_key"
        client = JulesClient(api_key)

        # Inject mock session
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.closed = False
        client._session = mock_session

        # Response 1: 503 Service Unavailable
        resp1 = AsyncMock()
        resp1.status = 503
        resp1.raise_for_status = MagicMock(side_effect=aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=503, message="Service Unavailable"
        ))

        # Response 2: 200 OK
        resp2 = AsyncMock()
        resp2.status = 200
        resp2.raise_for_status = MagicMock()
        resp2.json.return_value = {
            "id": "123", "name": "test", "state": "COMPLETED"
        }

        # Mocking context managers is tricky.
        # session.get() -> CM -> __aenter__ -> resp

        # We need side_effect on session.get to return different CMs
        cm1 = AsyncMock()
        cm1.__aenter__.return_value = resp1

        cm2 = AsyncMock()
        cm2.__aenter__.return_value = resp2

        mock_session.get.side_effect = [cm1, cm2]

        # Reduce poll interval for test
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await client.poll_session("123", timeout=10, poll_interval=0.1)

            self.assertEqual(result.state, SessionState.COMPLETED)
            self.assertEqual(mock_session.get.call_count, 2)
            # Verify sleep was called (backoff)
            mock_sleep.assert_called()

if __name__ == "__main__":
    unittest.main()
