import sys
from unittest.mock import MagicMock, patch
import pytest
import importlib

def test_semantic_validator_init_error(caplog):
    """
    Test that CCLSemanticValidator handles exceptions during client initialization
    gracefully by logging an error.
    """
    # Save original modules to restore later
    original_semantic_validator = sys.modules.get("mekhane.ccl.semantic_validator")
    original_google = sys.modules.get("google")
    original_genai = sys.modules.get("google.genai")

    try:
        # Mock google.genai
        mock_google = MagicMock()
        sys.modules["google"] = mock_google
        mock_genai = MagicMock()
        sys.modules["google.genai"] = mock_genai
        mock_google.genai = mock_genai

        # Configure mock client to raise exception
        mock_genai.Client.side_effect = Exception("Simulated API Error")

        # Remove from sys.modules so we can import a fresh one with the mocks in place
        if "mekhane.ccl.semantic_validator" in sys.modules:
            del sys.modules["mekhane.ccl.semantic_validator"]

        from mekhane.ccl import semantic_validator

        # Ensure correct state in the new module
        if not hasattr(semantic_validator, "genai"):
             semantic_validator.genai = mock_genai
        semantic_validator.HAS_LLM = True

        # Mock environment variable for API key
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"}):
            # Set logging level to ERROR to capture error logs
            caplog.set_level("ERROR")

            # Initialize the validator using the class from the NEW module
            validator = semantic_validator.CCLSemanticValidator()

            # Assertions
            assert validator.client is None
            assert validator.is_available() is False

            error_logs = [record for record in caplog.records if record.levelname == "ERROR"]

            if not error_logs:
                pytest.fail("No error logs captured!")

            assert len(error_logs) == 1
            assert "Failed to initialize GenAI client" in error_logs[0].message
            assert "Simulated API Error" in str(error_logs[0].exc_info) or "Simulated API Error" in error_logs[0].message

    finally:
        # Restore original modules
        if original_semantic_validator:
            sys.modules["mekhane.ccl.semantic_validator"] = original_semantic_validator
        else:
            sys.modules.pop("mekhane.ccl.semantic_validator", None)

        if original_google:
            sys.modules["google"] = original_google
        else:
            sys.modules.pop("google", None)

        if original_genai:
             sys.modules["google.genai"] = original_genai
        else:
             sys.modules.pop("google.genai", None)
