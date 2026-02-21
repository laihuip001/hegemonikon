# PROOF: [S2/Mekhanē] <- mekhane/ochema/tests/ A0->UnitTests
# PURPOSE: AntigravityClient ユニットテスト
"""
AntigravityClient unit tests.

Verifies:
- Session initialization
- RPC header logic (implicit vs explicit)
- Polling logic
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
import requests
from mekhane.ochema.antigravity_client import AntigravityClient, LSInfo, RPC_GET_STATUS


class TestAntigravityClient:

    @pytest.fixture
    def mock_ls_detection(self):
        """Mock subprocess to simulate LS detection."""
        with patch("subprocess.check_output") as mock_sub:
            # Step 1: ps aux
            ps_output = "user 1234 0.0 0.0 1234 5678 ? Ss 10:00 0:00 /path/to/language_server_linux --workspace /path/to/hegemonikon --csrf_token abcdef123456\n"
            # Step 2: ss -tlnp
            ss_output = 'LISTEN 0 128 127.0.0.1:8080 0.0.0.0:* users:(("language_server",pid=1234,fd=4))\n'

            mock_sub.side_effect = [ps_output, ss_output]
            yield mock_sub

    @pytest.fixture
    def mock_requests(self):
        """Mock requests.Session."""
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            # Must setup headers object behavior
            mock_session.headers = MagicMock()
            mock_session_cls.return_value = mock_session
            yield mock_session

    def test_init_initializes_session(self, mock_ls_detection, mock_requests):
        """Client initializes requests.Session with verify=False."""
        # Setup mock response for _detect_ls probing
        mock_response = MagicMock()
        mock_response.text = '{"userStatus": {}}'
        mock_response.json.return_value = {"userStatus": {}}
        mock_requests.post.return_value = mock_response

        client = AntigravityClient()

        # Check session was created
        assert client.session is mock_requests
        assert client.session.verify is False

        # Check LS detection parsed correctly
        assert client.ls.pid == 1234
        assert client.ls.port == 8080
        assert client.ls.csrf == "abcdef123456"

        # Verify session headers were updated after detection
        client.session.headers.update.assert_called_with(
            {
                "Content-Type": "application/json",
                "X-Codeium-Csrf-Token": "abcdef123456",
                "Connect-Protocol-Version": "1",
                "User-Agent": "ochema/0.1",
            }
        )

    def test_raw_rpc_uses_session_with_explicit_headers_during_detection(
        self, mock_ls_detection, mock_requests
    ):
        """During detection (before self.ls is set), use explicit headers."""
        mock_response = MagicMock()
        mock_response.text = '{"userStatus": {}}'
        mock_response.json.return_value = {"userStatus": {}}
        mock_requests.post.return_value = mock_response

        client = AntigravityClient()

        # Verify the call made during detection (the first call)
        calls = mock_requests.post.call_args_list
        assert len(calls) > 0

        # Find the call that matches the probe
        probe_call = calls[0]
        args, kwargs = probe_call

        # It should have explicit headers because self.ls was not ready
        assert "headers" in kwargs
        assert kwargs["headers"]["X-Codeium-Csrf-Token"] == "abcdef123456"
        assert kwargs["json"] == {
            "metadata": {
                "ideName": "antigravity",
                "extensionName": "antigravity",
                "locale": "en",
            }
        }

    def test_raw_rpc_uses_session_without_explicit_headers_after_init(
        self, mock_ls_detection, mock_requests
    ):
        """After init, use session headers (no headers arg in post)."""
        mock_response = MagicMock()
        mock_response.text = '{"userStatus": {}}'
        mock_response.json.return_value = {"userStatus": {}}
        mock_requests.post.return_value = mock_response

        client = AntigravityClient()

        # Reset mocks to clear initialization calls
        mock_requests.post.reset_mock()

        # Now make a normal call
        client.get_status()

        # Check the call
        args, kwargs = mock_requests.post.call_args

        # It should NOT have 'headers' because they are pre-configured in session
        assert "headers" not in kwargs
