import pytest
import logging
import sys
from unittest.mock import patch, MagicMock
from ..epoche_shield import EpocheShield

class TestEpocheErrorLogging:

    def test_mask_logs_info_on_missing_dependency(self, caplog):
        """
        Test that ImportError/ModuleNotFoundError logs an INFO message
        and continues to return masked text.
        """
        shield = EpocheShield()
        text = "Email: test@example.com"

        # Ensure regex mask still works
        with caplog.at_level(logging.INFO, logger="epoche_shield"):
            # This triggers the default path where vocab_store is missing
            # (Assuming vocab_store.py does not exist in the real file system)
            masked, mapping = shield.mask(text, use_custom_vocab=True)

        # Verify regex masking worked
        assert "test@example.com" not in masked
        assert "[EPOCHE_" in masked

        # Verify logging
        # We expect 1 record if vocab_store is missing.
        # If vocab_store magically exists, this test might fail or need adjustment,
        # but based on exploration it does not exist.
        assert len(caplog.records) > 0
        assert any("Optional component 'vocab_store' not found" in record.message for record in caplog.records)
        assert any(record.levelname == "INFO" for record in caplog.records)

    def test_mask_logs_error_on_generic_exception(self, caplog):
        """
        Test that generic Exception logs an ERROR message with exc_info
        and continues to return masked text.
        """
        shield = EpocheShield()
        text = "Email: test@example.com"

        # Setup mock module
        mock_module = MagicMock()
        mock_get_store = MagicMock()
        mock_get_store.side_effect = Exception("Database connection failed")
        mock_module.get_vocab_store = mock_get_store

        # We need to mock 'mekhane.poiema.flow.vocab_store' in sys.modules
        # so that the local import 'from .vocab_store import get_vocab_store' succeeds.
        with patch.dict(sys.modules, {"mekhane.poiema.flow.vocab_store": mock_module}):
            with caplog.at_level(logging.ERROR, logger="epoche_shield"):
                masked, mapping = shield.mask(text, use_custom_vocab=True)

        # Verify regex masking worked
        assert "test@example.com" not in masked
        assert "[EPOCHE_" in masked

        # Verify logging
        assert len(caplog.records) > 0
        assert any("Failed to apply custom vocabulary masking" in record.message for record in caplog.records)
        assert any("Database connection failed" in record.message for record in caplog.records)
        assert any(record.levelname == "ERROR" for record in caplog.records)
