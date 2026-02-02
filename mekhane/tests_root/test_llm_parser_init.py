import pytest
import logging
from unittest.mock import patch, MagicMock
from mekhane.ccl.llm_parser import LLMParser

def test_llm_parser_init_error_logging(caplog):
    # Setup
    caplog.set_level(logging.ERROR)

    # We patch module level constants and the genai module
    # We need 'create=True' for genai because it might not be importable in the env
    with patch("mekhane.ccl.llm_parser.HAS_GENAI", True), \
         patch("mekhane.ccl.llm_parser.USE_NEW_SDK", True), \
         patch("mekhane.ccl.llm_parser.genai", create=True) as mock_genai:

        # Configure the mock to raise an exception on Client instantiation
        mock_genai.Client.side_effect = Exception("Simulated Init Error")

        # Action
        parser = LLMParser()

        # Assert
        assert parser.client is None
        # Check if the error message is in the captured logs
        # Currently, the code passes silently, so this assertion should fail
        if "Simulated Init Error" not in caplog.text:
             pytest.fail(f"Expected error log not found. Logs: {caplog.text}")
