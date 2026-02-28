#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ccl/tests/
# PURPOSE: CCL LLM Parser のテスト
"""CCL LLM Parser Tests"""

import logging
import pytest
from unittest.mock import patch, MagicMock

from mekhane.ccl.llm_parser import LLMParser

# PURPOSE: Test suite validating LLM parser error handling
class TestLLMParserErrorHandling:
    """LLMParser のエラーハンドリングのテスト"""

    # PURPOSE: Verify parser initialization error logging
    @patch("mekhane.ccl.llm_parser.HAS_GENAI", True)
    @patch("mekhane.ccl.llm_parser.USE_NEW_SDK", True)
    @patch("mekhane.ccl.llm_parser._get_api_key", return_value="fake_key")
    @patch("mekhane.ccl.llm_parser.genai.Client", side_effect=Exception("Test initialization error"))
    def test_init_error_logging(self, mock_client, mock_get_api_key, caplog):
        """Verify initialization error is properly logged."""
        with caplog.at_level(logging.ERROR):
            parser = LLMParser()
            assert parser.client is None
            assert "Failed to initialize Gemini client: Test initialization error" in caplog.text

    # PURPOSE: Verify parsing error logging
    @patch("mekhane.ccl.llm_parser.HAS_GENAI", True)
    @patch("mekhane.ccl.llm_parser.USE_NEW_SDK", True)
    @patch("mekhane.ccl.llm_parser._get_api_key", return_value="fake_key")
    @patch("mekhane.ccl.llm_parser.genai.Client")
    def test_parse_error_logging(self, mock_client, mock_get_api_key, caplog):
        """Verify parsing execution error is properly logged."""
        # Setup mock to raise an exception when generate_content is called
        mock_instance = MagicMock()
        mock_instance.models.generate_content.side_effect = Exception("Test generation error")
        mock_client.return_value = mock_instance

        # We need to recreate parser to inject the mock behavior
        parser = LLMParser()
        parser.client = mock_instance # Override properly

        with caplog.at_level(logging.ERROR):
            result = parser.parse("Test intent")
            assert result is None
            assert "Failed to parse intent to CCL expression: Test generation error" in caplog.text
