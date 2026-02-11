import unittest
from unittest.mock import patch, MagicMock
import logging
import sys
from pathlib import Path

# Ensure mekhane is in path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import mekhane.ccl.semantic_validator as validator_module
from mekhane.ccl.semantic_validator import CCLSemanticValidator

class TestCCLSemanticValidator(unittest.TestCase):
    def setUp(self):
        # Inject genai into the module if it doesn't exist
        if not hasattr(validator_module, 'genai'):
            self.mock_genai = MagicMock()
            validator_module.genai = self.mock_genai
            self.genai_injected = True
        else:
            self.mock_genai = validator_module.genai
            self.genai_injected = False

    def tearDown(self):
        if self.genai_injected:
            del validator_module.genai

    @patch("mekhane.ccl.semantic_validator._get_api_key")
    @patch("mekhane.ccl.semantic_validator.HAS_LLM", True)
    def test_init_logs_error_on_failure(self, mock_get_api_key):
        # Setup
        mock_get_api_key.return_value = "dummy_key"

        # Configure the mock to raise exception
        self.mock_genai.Client.side_effect = Exception("Test API Error")

        # Capture logs
        with self.assertLogs("mekhane.ccl.semantic_validator", level="WARNING") as cm:
            validator = CCLSemanticValidator()

        # Verify log message
        self.assertTrue(any("Failed to initialize Gemini client" in log for log in cm.output))
        self.assertTrue(any("Test API Error" in log for log in cm.output))

if __name__ == "__main__":
    unittest.main()
