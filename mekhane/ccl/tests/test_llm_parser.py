import unittest
from unittest.mock import patch, MagicMock
import logging
import mekhane.ccl.llm_parser as llm_parser_module
from mekhane.ccl.llm_parser import LLMParser

class TestLLMParser(unittest.TestCase):
    def setUp(self):
        # Ensure we capture logs
        logging.basicConfig(level=logging.ERROR)

    def test_init_exception_logging(self):
        """Test that exceptions during initialization are logged."""
        # Patch HAS_GENAI and USE_NEW_SDK to force entering the initialization block
        with patch.object(llm_parser_module, 'HAS_GENAI', True), \
             patch.object(llm_parser_module, 'USE_NEW_SDK', True):

            # Mock genai module
            mock_genai = MagicMock()
            mock_genai.Client.side_effect = Exception("Simulated Init Error")

            with patch.object(llm_parser_module, 'genai', mock_genai, create=True):
                 # Expect an error log
                 with self.assertLogs('mekhane.ccl.llm_parser', level='ERROR') as cm:
                    parser = LLMParser()

                    # Verify logs contain the expected message
                    self.assertTrue(any("Failed to initialize LLM client" in log for log in cm.output))
                    self.assertTrue(any("Simulated Init Error" in log for log in cm.output))

                    # Verify parser state is correctly handled (graceful failure)
                    self.assertFalse(parser.is_available())

    def test_parse_exception_logging(self):
        """Test that exceptions during parsing are logged."""
        parser = LLMParser()
        # Manually setup the parser to look "initialized"
        parser.client = MagicMock()

        with patch.object(llm_parser_module, 'USE_NEW_SDK', True):
             # Mock the client's generate_content to raise exception
             parser.client.models.generate_content.side_effect = Exception("Simulated Parse Error")

             with self.assertLogs('mekhane.ccl.llm_parser', level='ERROR') as cm:
                 result = parser.parse("test intent")

                 self.assertIsNone(result)
                 self.assertTrue(any("LLM parsing failed" in log for log in cm.output))
                 self.assertTrue(any("Simulated Parse Error" in log for log in cm.output))
