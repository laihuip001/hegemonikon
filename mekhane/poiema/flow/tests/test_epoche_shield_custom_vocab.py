
import pytest
import logging
import sys
from unittest.mock import MagicMock, patch
from ..epoche_shield import EpocheShield

def test_mask_custom_vocab_missing_module(caplog):
    """
    Test that masking logs INFO when custom vocab module is missing (ImportError).
    """
    shield = EpocheShield()
    text = "Some text with sensitive info."

    # Enable logging capture
    with caplog.at_level(logging.INFO, logger="epoche_shield"):
        # Default use_custom_vocab is True.
        # Since .vocab_store is missing in the repo, this should trigger ImportError.
        masked, mapping = shield.mask(text, use_custom_vocab=True)

    # Verify functionality is not broken
    assert masked == text

    # Verify log message
    assert "Custom vocabulary store not available" in caplog.text
    assert "Skipping" in caplog.text

def test_mask_custom_vocab_runtime_error(caplog):
    """
    Test that masking logs ERROR when a runtime error occurs during custom vocab masking.
    """
    shield = EpocheShield()
    text = "Some text."

    # Mock the module and function
    mock_store_module = MagicMock()
    mock_get_store = MagicMock()
    mock_get_store.side_effect = RuntimeError("Boom")
    mock_store_module.get_vocab_store = mock_get_store

    # Inject the mock module into sys.modules
    # We mock 'mekhane.poiema.flow.vocab_store' because that's what 'from .vocab_store' resolves to
    # relative to 'mekhane.poiema.flow.epoche_shield'.
    with patch.dict(sys.modules, {'mekhane.poiema.flow.vocab_store': mock_store_module}):
        with caplog.at_level(logging.ERROR, logger="epoche_shield"):
            masked, mapping = shield.mask(text, use_custom_vocab=True)

    # Verify functionality is not broken (should return partial result from regex mask)
    assert masked == text

    # Verify log message
    assert "Error applying custom vocabulary mask" in caplog.text
    assert "Boom" in caplog.text
