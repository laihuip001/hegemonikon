import unittest
import logging
import sys
from unittest.mock import MagicMock, patch

# Mock google.genai before importing the module under test
# This ensures that HAS_LLM is set to True and 'genai' is available as a mock
mock_genai_module = MagicMock()
mock_google = MagicMock()
mock_google.genai = mock_genai_module
sys.modules["google"] = mock_google
sys.modules["google.genai"] = mock_genai_module

# Now import the module
# We need to ensure we import it from the correct path relative to repo root
# Assuming PYTHONPATH includes the repo root or we are running from it
from mekhane.ccl.semantic_validator import CCLSemanticValidator

class TestCCLSemanticValidatorError(unittest.TestCase):
    def test_init_error_logging(self):
        """Test that errors during genai.Client initialization are logged."""

        # Ensure the logger is configured to capture logs for the test
        # The logger name in the module will be 'mekhane.ccl.semantic_validator' (derived from __name__)
        logger_name = "mekhane.ccl.semantic_validator"

        # Mock _get_api_key to return a valid key so the init logic proceeds
        with patch("mekhane.ccl.semantic_validator._get_api_key", return_value="fake_key"):
            # Mock genai.Client to raise an exception
            mock_genai_module.Client.side_effect = Exception("Simulated API Initialization Error")

            # Use assertLogs to verify that an error is logged
            # If the code swallows the error (current state), this context manager will raise an AssertionError
            try:
                with self.assertLogs(logger_name, level="ERROR") as cm:
                    validator = CCLSemanticValidator()

                    # Verify that client is None (graceful degradation)
                    self.assertIsNone(validator.client)

                    # Verify that the log message contains the exception details
                    self.assertTrue(any("Simulated API Initialization Error" in output for output in cm.output),
                                    f"Expected error message not found in logs: {cm.output}")
            except AssertionError as e:
                # If assertLogs fails because no logs were emitted, we are in the "reproduced" state.
                if "no logs of level ERROR" in str(e):
                    print("Test reproduced issue: No ERROR logs were emitted as expected (before fix).")
                    # We re-raise to confirm failure if we were running strictly,
                    # but for this step I want to confirm the file is created.
                    # I will let it fail when I run it in verification step.
                    raise e
                raise e

if __name__ == "__main__":
    unittest.main()
