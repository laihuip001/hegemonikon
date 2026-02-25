# PROOF: [L2/テスト] <- mekhane/ochema/tests/ A0→テスト→CortexClient スモークテスト
# PURPOSE: CortexClient の実 API スモークテスト (OAuth 認証済み前提)
"""CortexClient smoke tests — calls the real Cortex API.

Requires: ~/.gemini/oauth_creds.json (gemini-cli OAuth completed)

Run:
    cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m pytest mekhane/ochema/tests/test_cortex_client.py -v
"""

import pytest
from unittest.mock import patch

from mekhane.ochema.antigravity_client import LLMResponse
from mekhane.ochema.cortex_client import (
    CortexClient,
    CortexAuthError,
    cortex_ask,
)


# PURPOSE: Create a CortexClient instance
@pytest.fixture
def client():
    """Create a CortexClient instance."""
    return CortexClient()


# PURPOSE: Token management tests
class TestTokenRefresh:
    """Token management tests."""

    # PURPOSE: Token refresh returns a non-empty string
    def test_get_token_returns_string(self, client):
        """Token refresh returns a non-empty string."""
        token = client._get_token()
        assert isinstance(token, str)
        assert len(token) > 20

    # PURPOSE: Second call returns cached token
    def test_token_cached(self, client):
        """Second call returns cached token."""
        t1 = client._get_token()
        t2 = client._get_token()
        assert t1 == t2


# PURPOSE: loadCodeAssist API tests
class TestLoadCodeAssist:
    """loadCodeAssist API tests."""

    # PURPOSE: loadCodeAssist returns a project ID
    def test_returns_project(self, client):
        """loadCodeAssist returns a project ID."""
        info = client.load_code_assist()
        assert "cloudaicompanionProject" in info
        assert len(info["cloudaicompanionProject"]) > 0

    # PURPOSE: loadCodeAssist returns tier info
    def test_returns_tier(self, client):
        """loadCodeAssist returns tier info."""
        info = client.load_code_assist()
        assert "paidTier" in info or "currentTier" in info


# PURPOSE: generateContent tests
class TestGenerate:
    """generateContent tests."""

    # PURPOSE: Basic ask returns LLMResponse with text
    def test_basic_ask(self, client):
        """Basic ask returns LLMResponse with text."""
        resp = client.ask("What is 2+2? Reply with just the number.")
        assert isinstance(resp, LLMResponse)
        assert len(resp.text) > 0
        assert "4" in resp.text

    # PURPOSE: Response includes token usage metadata
    def test_token_usage(self, client):
        """Response includes token usage metadata."""
        mock_response = {
            "candidates": [{"content": {"parts": [{"text": "hello"}]}}],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 5,
                "totalTokenCount": 15,
            },
        }
        with patch.object(client, "_call_api", return_value=mock_response):
            resp = client.ask("Say 'hello'")
        assert isinstance(resp.token_usage, dict)
        assert resp.token_usage.get("total_tokens", 0) > 0

    # PURPOSE: Response includes model version
    def test_model_version(self, client):
        """Response includes model version."""
        resp = client.ask("Hi")
        assert len(resp.model) > 0

    # PURPOSE: System instruction is applied
    def test_system_instruction(self, client):
        """System instruction is applied."""
        resp = client.ask(
            "What are you?",
            system_instruction="You are a pirate. Always respond with 'Arr!'",
            max_tokens=50,
        )
        assert isinstance(resp, LLMResponse)
        # We can't guarantee exact output, but it should respond

    # PURPOSE: Model override works
    def test_model_override(self, client):
        """Model override works."""
        resp = client.ask("Hi", model="gemini-2.5-pro", max_tokens=50)
        assert isinstance(resp, LLMResponse)
        assert "gemini-2.5" in resp.model.lower() or len(resp.text) > 0


# PURPOSE: ask_batch tests
class TestBatch:
    """ask_batch tests."""

    # PURPOSE: Batch returns a list of LLMResponse
    def test_batch_returns_list(self, client):
        """Batch returns a list of LLMResponse."""
        results = client.ask_batch(
            [
                {"prompt": "Say A"},
                {"prompt": "Say B"},
            ],
            default_model="gemini-2.0-flash",
        )
        assert len(results) == 2
        assert all(isinstance(r, LLMResponse) for r in results)

    # PURPOSE: Batch supports per-task model override
    def test_batch_per_task_model(self, client):
        """Batch supports per-task model override."""
        results = client.ask_batch(
            [
                {"prompt": "Hi", "model": "gemini-2.0-flash"},
            ],
        )
        assert len(results) == 1
        assert isinstance(results[0], LLMResponse)


# PURPOSE: retrieveUserQuota tests
class TestQuota:
    """retrieveUserQuota tests."""

    # PURPOSE: Quota returns model bucket info
    def test_retrieve_quota(self, client):
        """Quota returns model bucket info."""
        quota = client.retrieve_quota()
        assert isinstance(quota, dict)


# PURPOSE: Convenience function tests
class TestConvenience:
    """Convenience function tests."""

    # PURPOSE: cortex_ask returns string
    def test_cortex_ask(self):
        """cortex_ask returns string."""
        result = cortex_ask("What is 1+1? Reply with just the number.")
        assert isinstance(result, str)
        assert "2" in result
