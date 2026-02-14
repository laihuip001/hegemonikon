# PROOF: [L2/インフラ] <- mekhane/pks/
# PURPOSE: SelfAdvocate のテスト

import pytest
from unittest.mock import MagicMock, patch
from mekhane.pks.self_advocate import SelfAdvocate, Advocacy
from mekhane.pks.pks_engine import KnowledgeNugget, SessionContext

class TestSelfAdvocate:
    @pytest.fixture
    def mock_llm_client(self):
        with patch("mekhane.pks.self_advocate.PKSLLMClient") as MockClient:
            client_instance = MockClient.return_value
            # Set default behavior
            client_instance.available = True
            client_instance.generate.return_value = "This is a test message."
            yield client_instance

    @pytest.fixture
    def sample_nugget(self):
        return KnowledgeNugget(
            title="Test Nugget",
            abstract="Abstract",
            source="test",
            relevance_score=0.9,
        )

    @pytest.fixture
    def sample_context(self):
        return SessionContext(topics=["Topic A"], recent_queries=["Query 1"])

    def test_init(self, mock_llm_client):
        advocate = SelfAdvocate()
        assert advocate.llm_available

    def test_generate_batch(self, mock_llm_client, sample_nugget, sample_context):
        advocate = SelfAdvocate()
        advocacies = advocate.generate_batch([sample_nugget], sample_context)
        assert len(advocacies) == 1
        assert advocacies[0].message == "This is a test message."
        assert advocacies[0].nugget_title == "Test Nugget"

    def test_generate_batch_unavailable(self, mock_llm_client, sample_nugget, sample_context):
        # Setup the mock to be unavailable
        mock_llm_client.available = False

        advocate = SelfAdvocate()
        assert not advocate.llm_available

        advocacies = advocate.generate_batch([sample_nugget], sample_context)
        assert len(advocacies) == 0

    def test_format_report(self):
        with patch("mekhane.pks.self_advocate.PKSLLMClient"):
            advocate = SelfAdvocate()
            advocacies = [
                Advocacy(nugget_title="Title 1", message="Msg 1", confidence=0.9),
                Advocacy(nugget_title="Title 2", message="Msg 2", confidence=0.8)
            ]
            report = advocate.format_report(advocacies)
            assert "Title 1" in report
            assert "Msg 1" in report
            assert "Title 2" in report
            assert "## 🗣️ Autophōnos Messages" in report
