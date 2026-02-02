import unittest
import logging
from unittest.mock import MagicMock, patch
import sys

# Ensure google.genai is importable so HAS_LLM becomes True
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()

# Import the module
import mekhane.ccl.semantic_validator as mod
from mekhane.ccl.semantic_validator import CCLSemanticValidator, HAS_LLM

class TestCCLSemanticValidatorError(unittest.TestCase):
    def test_init_error_logging(self):
        # Verify HAS_LLM is True
        self.assertTrue(HAS_LLM)

        # Create a controlled mock for genai
        mock_genai = MagicMock()
        mock_genai.Client.side_effect = Exception("Simulated API Error")

        # Replace the genai object in the module with our mock
        # We need to patch it where it is used.
        # Since 'CCLSemanticValidator' uses 'self.client = genai.Client(...)',
        # it looks up 'genai' in the module globals.
        with patch("mekhane.ccl.semantic_validator.genai", mock_genai):
            with patch("mekhane.ccl.semantic_validator._get_api_key", return_value="fake_key"):

                # Assert that a warning is logged
                with self.assertLogs("mekhane.ccl.semantic_validator", level="WARNING") as cm:
                    validator = CCLSemanticValidator()

                    # Verify graceful degradation
                    self.assertIsNone(validator.client)

                    # Verify the log message
                    self.assertTrue(any("Failed to initialize GenAI client" in o for o in cm.output))
                    self.assertTrue(any("Simulated API Error" in o for o in cm.output))

if __name__ == "__main__":
    unittest.main()
