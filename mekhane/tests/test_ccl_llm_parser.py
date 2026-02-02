import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import logging

class TestLLMParser(unittest.TestCase):
    def setUp(self):
        # Create mocks
        self.mock_genai = MagicMock()
        self.mock_google = MagicMock()
        self.mock_google.genai = self.mock_genai
        self.mock_types = MagicMock()

        # Patch sys.modules to inject mocks
        self.modules_patcher = patch.dict(sys.modules, {
            "google": self.mock_google,
            "google.genai": self.mock_genai,
            "google.genai.types": self.mock_types,
            "google.generativeai": MagicMock()
        })
        self.modules_patcher.start()

        # Remove cached module if it exists to ensure re-import uses mocks
        if 'mekhane.ccl.llm_parser' in sys.modules:
            del sys.modules['mekhane.ccl.llm_parser']

        # Import the module under test
        from mekhane.ccl.llm_parser import LLMParser
        self.LLMParser = LLMParser

    def tearDown(self):
        self.modules_patcher.stop()

    def test_parse_logs_error_on_exception(self):
        """Test that parse method logs error and returns None on exception."""
        # Setup mock client to raise exception
        mock_client = MagicMock()
        self.mock_genai.Client.return_value = mock_client

        # MagicMock automatically creates children, but we need to ensure
        # the specific method call raises exception.
        # client.models.generate_content
        mock_models = MagicMock()
        mock_client.models = mock_models
        mock_generate_content = MagicMock()
        mock_models.generate_content = mock_generate_content
        mock_generate_content.side_effect = Exception("Simulated API Crash")

        # Instantiate parser
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "dummy_key"}):
            parser = self.LLMParser()

        # Verify logging
        with self.assertLogs('mekhane.ccl.llm_parser', level='ERROR') as cm:
            result = parser.parse("some intent")

        # Check result
        self.assertIsNone(result)

        # Check logs
        self.assertTrue(any("LLM parsing failed" in o for o in cm.output))
        self.assertTrue(any("Simulated API Crash" in o for o in cm.output))

    def test_init_logs_error_on_exception(self):
        """Test that __init__ logs error on initialization failure."""
        # Setup mock Client constructor to raise exception
        self.mock_genai.Client.side_effect = Exception("Init Failure")

        # Verify logging
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "dummy_key"}):
            with self.assertLogs('mekhane.ccl.llm_parser', level='ERROR') as cm:
                parser = self.LLMParser()

        # Check logs
        self.assertTrue(any("Failed to initialize LLM client" in o for o in cm.output))
        self.assertTrue(any("Init Failure" in o for o in cm.output))

        # Verify parser is not available
        self.assertFalse(parser.is_available())

if __name__ == "__main__":
    unittest.main()
