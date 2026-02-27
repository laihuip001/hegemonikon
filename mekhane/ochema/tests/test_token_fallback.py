#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/ochema/tests/test_token_fallback.py S2→Mekhane→Ochema
# PROOF: [L2/テスト] <- mekhane/ochema/tests/ テスト
# PURPOSE: _get_token() のフォールバック順序を検証するユニットテスト
"""Token fallback order tests — verifies "Trust the runtime, not the config".

Design principle: LS OAuth (runtime) should be tried before TokenVault and
gemini-cli (config-based) to avoid dependency on external config files.

Run:
    cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m pytest \
        mekhane/ochema/tests/test_token_fallback.py -v
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def fresh_client():
    """Create a CortexClient with no cached token."""
    from mekhane.ochema.cortex_client import CortexClient
    client = CortexClient()
    client._token = None
    return client


class TestTokenFallbackOrder:
    """Verify _get_token() tries sources in the correct order.

    Expected order:
        1. Instance cache
        2. File cache (/tmp)
        3. LS OAuth (state.vscdb)  ← most reliable in IDE
        4. TokenVault
        5. gemini-cli OAuth (last resort)
    """

    def test_ls_oauth_tried_before_vault(self, fresh_client):
        """LS OAuth should be attempted before TokenVault."""
        call_order = []

        def mock_ls_token(self_):
            call_order.append("ls_oauth")
            return "ya29.ls_token_value"

        def mock_vault_get(account):
            call_order.append("vault")
            raise Exception("vault not configured")

        with patch.object(type(fresh_client), '_get_ls_token', mock_ls_token), \
             patch.object(fresh_client.vault, 'get_token', mock_vault_get), \
             patch('mekhane.ochema.cortex_client._TOKEN_CACHE', MagicMock(exists=lambda: False)):
            token = fresh_client._get_token()

        assert token == "ya29.ls_token_value"
        assert call_order == ["ls_oauth"], f"Expected LS first, got: {call_order}"

    def test_vault_tried_after_ls_fails(self, fresh_client):
        """TokenVault should be tried when LS OAuth returns None."""
        call_order = []

        def mock_ls_token(self_):
            call_order.append("ls_oauth")
            return None

        def mock_vault_get(account):
            call_order.append("vault")
            return "vault_token_value"

        with patch.object(type(fresh_client), '_get_ls_token', mock_ls_token), \
             patch.object(fresh_client.vault, 'get_token', mock_vault_get), \
             patch('mekhane.ochema.cortex_client._TOKEN_CACHE', MagicMock(exists=lambda: False)):
            token = fresh_client._get_token()

        assert token == "vault_token_value"
        assert call_order == ["ls_oauth", "vault"]

    def test_gemini_cli_is_last_resort(self, fresh_client):
        """gemini-cli OAuth should only be tried after LS and vault fail."""
        call_order = []

        def mock_ls_token(self_):
            call_order.append("ls_oauth")
            return None

        def mock_vault_get(account):
            call_order.append("vault")
            raise Exception("vault fail")

        def mock_refresh(self_):
            call_order.append("gemini_cli")
            return "gemini_cli_token"

        mock_creds = MagicMock()
        mock_creds.exists.return_value = True

        with patch.object(type(fresh_client), '_get_ls_token', mock_ls_token), \
             patch.object(fresh_client.vault, 'get_token', mock_vault_get), \
             patch.object(type(fresh_client), '_refresh_gemini_cli_token', mock_refresh), \
             patch('mekhane.ochema.cortex_client._CREDS_FILE', mock_creds), \
             patch('mekhane.ochema.cortex_client._TOKEN_CACHE', MagicMock(exists=lambda: False)):
            token = fresh_client._get_token()

        assert token == "gemini_cli_token"
        assert call_order == ["ls_oauth", "vault", "gemini_cli"]

    def test_cache_hit_skips_all(self, fresh_client):
        """File cache hit should skip LS, vault, and gemini-cli."""
        fresh_client._token = "cached_token"

        mock_cache = MagicMock()
        mock_cache.exists.return_value = True
        mock_cache.stat.return_value = MagicMock(st_mtime=time.time())

        with patch('mekhane.ochema.cortex_client._TOKEN_CACHE', mock_cache):
            token = fresh_client._get_token()

        assert token == "cached_token"

    def test_ls_token_cached_to_file(self, fresh_client):
        """LS OAuth token should be written to file cache for performance."""
        mock_cache = MagicMock()
        mock_cache.exists.return_value = False

        def mock_ls_token(self_):
            return "ya29.fresh_ls_token"

        with patch.object(type(fresh_client), '_get_ls_token', mock_ls_token), \
             patch('mekhane.ochema.cortex_client._TOKEN_CACHE', mock_cache):
            fresh_client._account = "default"
            token = fresh_client._get_token()

        assert token == "ya29.fresh_ls_token"
        mock_cache.write_text.assert_called_once_with("ya29.fresh_ls_token")
        mock_cache.chmod.assert_called_once_with(0o600)

    def test_all_fail_raises_auth_error(self, fresh_client):
        """CortexAuthError should mention LS first in error message."""
        from mekhane.ochema.cortex_client import CortexAuthError

        def mock_ls_token(self_):
            return None

        def mock_vault_get(account):
            raise Exception("vault fail")

        mock_creds = MagicMock()
        mock_creds.exists.return_value = False

        with patch.object(type(fresh_client), '_get_ls_token', mock_ls_token), \
             patch.object(fresh_client.vault, 'get_token', mock_vault_get), \
             patch('mekhane.ochema.cortex_client._CREDS_FILE', mock_creds), \
             patch('mekhane.ochema.cortex_client._TOKEN_CACHE', MagicMock(exists=lambda: False)):
            with pytest.raises(CortexAuthError, match="Antigravity IDE"):
                fresh_client._get_token()
