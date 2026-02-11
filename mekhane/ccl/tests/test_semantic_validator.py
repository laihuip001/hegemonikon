
import pytest
from unittest.mock import MagicMock
from mekhane.ccl.semantic_validator import CCLSemanticValidator, SemanticResult

class TestCCLSemanticValidator:
    @pytest.fixture
    def validator(self):
        # Just create the validator. We don't need real LLM client for testing _parse_response
        validator = CCLSemanticValidator()
        return validator

    def test_parse_response_valid_json(self, validator):
        json_text = """
        {
            "aligned": true,
            "confidence": 0.9,
            "reasoning": "Perfect match",
            "suggestions": []
        }
        """
        result = validator._parse_response(json_text)
        assert result.aligned is True
        assert result.confidence == 0.9
        assert result.reasoning == "Perfect match"

    def test_parse_response_invalid_json_logs_error(self, validator, caplog):
        import logging

        # This text looks like JSON but is invalid
        invalid_json = """
        {
            "aligned": true,
            "confidence": 0.9,
            "reasoning": "Unterminated string
        }
        """

        # We expect this to fail JSON parsing and fall back to text inference
        with caplog.at_level(logging.WARNING):
            result = validator._parse_response(invalid_json)

        # Check that we got a result via fallback
        assert isinstance(result, SemanticResult)

        # We now expect a log message
        assert len(caplog.records) > 0
        assert "JSON decode error" in caplog.text or "Malformed JSON" in caplog.text
