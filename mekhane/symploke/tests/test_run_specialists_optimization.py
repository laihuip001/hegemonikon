
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Ensure the module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from mekhane.symploke.run_specialists import run_batch
from mekhane.symploke.specialist_prompts import SpecialistDefinition, Archetype

@pytest.mark.asyncio
async def test_run_batch_uses_single_session():
    # Mock data
    specialists = [
        SpecialistDefinition(id="T1", name="Test1", category="test", archetype=Archetype.PRECISION, focus="focus1"),
        SpecialistDefinition(id="T2", name="Test2", category="test", archetype=Archetype.PRECISION, focus="focus2"),
    ]
    target_file = "test_file.py"

    # Patch API_KEYS in run_specialists to ensure we don't return early
    with patch("mekhane.symploke.run_specialists.API_KEYS", ["dummy_key"]):
        # Mock aiohttp.ClientSession
        with patch("aiohttp.ClientSession") as MockSession:
            # Setup mock session context manager
            mock_session_instance = MagicMock() # Changed to MagicMock because post() is synchronous
            MockSession.return_value.__aenter__.return_value = mock_session_instance

            # Setup mock post response
            mock_response = MagicMock() # The response object itself doesn't need to be AsyncMock, but its methods might
            mock_response.status = 200

            # json() is async
            mock_response.json = AsyncMock(return_value={"id": "sess_123", "url": "http://test"})

            # Context manager for post
            post_ctx = AsyncMock()
            post_ctx.__aenter__.return_value = mock_response
            mock_session_instance.post.return_value = post_ctx

            # Run batch
            results = await run_batch(specialists, target_file)

            # Verify ClientSession was created EXACTLY once
            assert MockSession.call_count == 1, f"ClientSession created {MockSession.call_count} times, expected 1"

            # Verify post was called for each specialist
            assert mock_session_instance.post.call_count == len(specialists)

            # Verify results
            assert len(results) == 2
            assert results[0]["session_id"] == "sess_123"
