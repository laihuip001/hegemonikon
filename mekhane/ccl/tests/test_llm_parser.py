import logging
import pytest
from unittest.mock import MagicMock, patch
from mekhane.ccl import llm_parser

class TestLLMParserInit:
    """Tests for LLMParser initialization."""

    def test_legacy_sdk_init_failure_logging(self, caplog):
        """Test that initialization failure in legacy SDK is logged."""

        # Patch the configuration to force the legacy code path
        with patch.object(llm_parser, 'HAS_GENAI', True), \
             patch.object(llm_parser, 'USE_NEW_SDK', False):

            # Create a mock for the legacy SDK that raises an error on init
            mock_legacy = MagicMock()
            mock_legacy.GenerativeModel.side_effect = RuntimeError("Simulated Legacy SDK Failure")

            # Inject the mock as 'genai_legacy' into the module
            # create=True allows patching if the name doesn't exist (e.g. if import failed)
            with patch.object(llm_parser, 'genai_legacy', mock_legacy, create=True):
                with caplog.at_level(logging.WARNING):
                    # Initialize parser
                    parser = llm_parser.LLMParser()

                    # Assert the exception was caught and handled gracefully
                    assert parser.model is None

                    # Assert it was logged
                    # Note: This assertion is expected to fail until the fix is implemented
                    if "Failed to initialize Gemini SDK" not in caplog.text:
                         pytest.fail("Exception was not logged (Expected failure before fix)")
