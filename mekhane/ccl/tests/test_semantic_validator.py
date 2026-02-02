import logging
import pytest
from mekhane.ccl.semantic_validator import CCLSemanticValidator, SemanticResult

class TestCCLSemanticValidator:
    def test_parse_response_invalid_json_logs_warning_and_fallbacks(self, caplog):
        """
        Test that _parse_response logs a warning when JSON parsing fails
        and falls back to text inference.
        """
        validator = CCLSemanticValidator()

        # A response that looks like JSON but is invalid
        invalid_json_text = "Here is the result: { 'aligned': True, 'confidence': ... }" # Single quotes are not valid JSON

        with caplog.at_level(logging.WARNING):
            result = validator._parse_response(invalid_json_text)

        # Check that the fallback logic was used
        assert isinstance(result, SemanticResult)
        # Fallback logic: aligned = "不一致" not in text and "aligned.*false" not in text.lower()
        # "confidence" should be 0.5 from fallback
        assert result.confidence == 0.5

        # Check that a warning was logged
        assert "Failed to parse LLM response as JSON" in caplog.text

    def test_parse_response_value_error_logs_warning_and_fallbacks(self, caplog):
        """
        Test that _parse_response logs a warning when ValueError occurs (e.g. invalid float)
        and falls back to text inference.
        """
        validator = CCLSemanticValidator()

        # A response that is valid JSON structure but causes ValueError during processing
        # data = json.loads(json_match.group())
        # return SemanticResult(..., confidence=float(data.get("confidence", 0.5)), ...)
        # So if confidence is not convertible to float, it raises ValueError.

        invalid_value_text = '{"aligned": true, "confidence": "high"}'

        with caplog.at_level(logging.WARNING):
            result = validator._parse_response(invalid_value_text)

        assert isinstance(result, SemanticResult)
        assert result.confidence == 0.5 # Fallback

        assert "Failed to parse LLM response as JSON" in caplog.text
