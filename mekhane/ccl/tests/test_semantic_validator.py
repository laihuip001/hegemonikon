import pytest
import logging
from unittest.mock import patch, MagicMock
import sys

from mekhane.ccl.semantic_validator import CCLSemanticValidator

class TestCCLSemanticValidator:

    @patch("mekhane.ccl.semantic_validator.HAS_LLM", True)
    @patch("mekhane.ccl.semantic_validator._get_api_key", return_value="dummy_key")
    def test_client_initialization_failure_logging(self, mock_get_api_key, caplog):
        """Test that genai.Client initialization failure is logged."""

        # Patch 'mekhane.ccl.semantic_validator.genai' to simulate the client class.
        # create=True ensures it works even if genai failed to import in the actual module.
        with patch("mekhane.ccl.semantic_validator.genai", create=True) as mock_genai:
            # Configure the mock Client to raise an exception when instantiated
            mock_genai.Client.side_effect = Exception("Simulated Auth Failure")

            # Capture logs
            with caplog.at_level(logging.WARNING):
                validator = CCLSemanticValidator()

            # Verify client is None
            assert validator.client is None

            # Verify the error was logged
            # Note: We expect this to fail initially as logging is not implemented
            assert "Failed to initialize genai.Client" in caplog.text
            assert "Simulated Auth Failure" in caplog.text
