import sys
import logging
from unittest.mock import MagicMock, patch
import pytest

def test_init_error_handling(caplog):
    """Test that exceptions during initialization are logged."""

    # create mocks
    mock_google = MagicMock()
    mock_genai = MagicMock()
    mock_google.genai = mock_genai

    # Configure the mock to raise an exception when Client is instantiated
    mock_genai.Client.side_effect = Exception("Simulated API Error during init")

    modules = {
        "google": mock_google,
        "google.genai": mock_genai,
        "google.genai.types": MagicMock(),
    }

    # Apply the mocks to sys.modules
    with patch.dict(sys.modules, modules):
        # Remove the module if it was already imported so it re-imports with our mocks
        if "mekhane.ccl.llm_parser" in sys.modules:
            del sys.modules["mekhane.ccl.llm_parser"]

        from mekhane.ccl.llm_parser import LLMParser, HAS_GENAI

        # Verify our mock setup worked and we are in the "new SDK" path
        assert HAS_GENAI is True

        with caplog.at_level(logging.ERROR):
            parser = LLMParser()

            # Check if the error was logged
            assert "Failed to initialize LLM model: Simulated API Error during init" in caplog.text

            # Verify parser is not available
            assert not parser.is_available()
