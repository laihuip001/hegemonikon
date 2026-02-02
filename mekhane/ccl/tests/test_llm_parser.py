import unittest
from unittest.mock import MagicMock, patch
import logging
import sys
import os

# Add repository root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from mekhane.ccl.llm_parser import LLMParser

class TestLLMParser(unittest.TestCase):
    def test_parse_exception_logging(self):
        """Test that exceptions during parsing are logged."""
        parser = LLMParser()

        # Force USE_NEW_SDK to True to test that branch
        with patch('mekhane.ccl.llm_parser.USE_NEW_SDK', True):
            # Mock the client to raise an exception
            mock_client = MagicMock()
            # The code calls self.client.models.generate_content
            mock_client.models.generate_content.side_effect = Exception("Simulated API Error")
            parser.client = mock_client

            # Verify parser is available
            self.assertTrue(parser.is_available(), "Parser should be available with mock client")

            # Assert logs are captured
            # Note: This will fail until we add logging to the code
            with self.assertLogs('mekhane.ccl.llm_parser', level='ERROR') as cm:
                result = parser.parse("test intent")

                # Result should be None on error
                self.assertIsNone(result)

                # Verify expected log message
                self.assertTrue(any("LLM parse failed" in output for output in cm.output),
                                f"Expected log message not found in {cm.output}")
                self.assertTrue(any("Simulated API Error" in output for output in cm.output),
                                f"Exception message not found in {cm.output}")

if __name__ == '__main__':
    unittest.main()
