import sys
import pytest
import logging
from unittest.mock import MagicMock, patch

# Mock google modules before importing the module under test
mock_genai = MagicMock()
mock_genai.types.GenerateContentConfig = MagicMock()
mock_google = MagicMock()
mock_google.genai = mock_genai  # Link attribute to module mock
sys.modules["google"] = mock_google
sys.modules["google.genai"] = mock_genai
sys.modules["google.genai.types"] = MagicMock()

# Mock yaml since it might be missing
sys.modules["yaml"] = MagicMock()

# Now we can import, but we need to reload it if it was already imported
# to ensure the module level checks run with our mocks
import mekhane.ccl.llm_parser
from importlib import reload
reload(mekhane.ccl.llm_parser)

from mekhane.ccl.llm_parser import LLMParser

def test_llm_parser_init_error_logging(caplog):
    """Test that initialization errors are logged."""
    # Ensure HAS_GENAI is True so we enter the block
    assert mekhane.ccl.llm_parser.HAS_GENAI is True

    # Configure mock to raise exception on instantiation
    # depending on USE_NEW_SDK
    if mekhane.ccl.llm_parser.USE_NEW_SDK:
        mock_genai.Client.side_effect = Exception("Simulated Init Error")
    else:
        # If legacy path was taken, we would need to mock google.generativeai
        pass

    with caplog.at_level(logging.ERROR):
        parser = LLMParser()

        # We expect error logs now.
        assert "Failed to initialize LLM client: Simulated Init Error" in caplog.text

def test_llm_parser_parse_error_logging(caplog):
    """Test that parse errors are logged."""
    # Reset side effect for Client so init succeeds
    mock_genai.Client.side_effect = None
    # We need to set the side effect on the instance returned by the constructor
    client_instance = MagicMock()
    mock_genai.Client.return_value = client_instance
    client_instance.models.generate_content.side_effect = Exception("Simulated Parse Error")

    parser = LLMParser()
    # Mock is_available to return True
    parser.is_available = lambda: True

    with caplog.at_level(logging.ERROR):
        result = parser.parse("some intent")

        # Expectation: error log present
        assert "Failed to parse intent: Simulated Parse Error" in caplog.text
        assert result is None
