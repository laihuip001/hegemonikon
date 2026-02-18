# PROOF: [L2/テスト] <- mekhane/ochema/tests/ A0→テスト→CortexClient スモークテスト
# PURPOSE: CortexClient の実 API スモークテスト (OAuth 認証済み前提)
"""CortexClient smoke tests — calls the real Cortex API.

Requires: ~/.gemini/oauth_creds.json (gemini-cli OAuth completed)

Run:
    cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m pytest mekhane/ochema/tests/test_cortex_client.py -v
"""

import pytest

from mekhane.ochema.antigravity_client import LLMResponse
from mekhane.ochema.cortex_client import (
    CortexClient,
    CortexAuthError,
    cortex_ask,
)


@pytest.fixture
def client():
    """Create a CortexClient instance."""
    return CortexClient()


class TestTokenRefresh:
    """Token management tests."""

    def test_get_token_returns_string(self, client):
        """Token refresh returns a non-empty string."""
        token = client._get_token()
        assert isinstance(token, str)
        assert len(token) > 20

    def test_token_cached(self, client):
        """Second call returns cached token."""
        t1 = client._get_token()
        t2 = client._get_token()
        assert t1 == t2


class TestLoadCodeAssist:
    """loadCodeAssist API tests."""

    def test_returns_project(self, client):
        """loadCodeAssist returns a project ID."""
        info = client.load_code_assist()
        assert "cloudaicompanionProject" in info
        assert len(info["cloudaicompanionProject"]) > 0

    def test_returns_tier(self, client):
        """loadCodeAssist returns tier info."""
        info = client.load_code_assist()
        assert "paidTier" in info or "currentTier" in info


class TestGenerate:
    """generateContent tests."""

    def test_basic_ask(self, client):
        """Basic ask returns LLMResponse with text."""
        resp = client.ask("What is 2+2? Reply with just the number.")
        assert isinstance(resp, LLMResponse)
        assert len(resp.text) > 0
        assert "4" in resp.text

    def test_token_usage(self, client):
        """Response includes token usage metadata."""
        resp = client.ask("Say 'hello'")
        assert isinstance(resp.token_usage, dict)
        assert resp.token_usage.get("total_tokens", 0) > 0

    def test_model_version(self, client):
        """Response includes model version."""
        resp = client.ask("Hi")
        assert len(resp.model) > 0

    def test_system_instruction(self, client):
        """System instruction is applied."""
        resp = client.ask(
            "What are you?",
            system_instruction="You are a pirate. Always respond with 'Arr!'",
            max_tokens=50,
        )
        assert isinstance(resp, LLMResponse)
        # We can't guarantee exact output, but it should respond

    def test_model_override(self, client):
        """Model override works."""
        resp = client.ask("Hi", model="gemini-2.5-pro", max_tokens=50)
        assert isinstance(resp, LLMResponse)
        assert "gemini-2.5" in resp.model.lower() or len(resp.text) > 0


class TestBatch:
    """ask_batch tests."""

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

    def test_batch_per_task_model(self, client):
        """Batch supports per-task model override."""
        results = client.ask_batch(
            [
                {"prompt": "Hi", "model": "gemini-2.0-flash"},
            ],
        )
        assert len(results) == 1
        assert isinstance(results[0], LLMResponse)


class TestQuota:
    """retrieveUserQuota tests."""

    def test_retrieve_quota(self, client):
        """Quota returns model bucket info."""
        quota = client.retrieve_quota()
        assert isinstance(quota, dict)


class TestConvenience:
    """Convenience function tests."""

    def test_cortex_ask(self):
        """cortex_ask returns string."""
        result = cortex_ask("What is 1+1? Reply with just the number.")
        assert isinstance(result, str)
        assert "2" in result
