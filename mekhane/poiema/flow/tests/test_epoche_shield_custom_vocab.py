
import pytest
import logging
import sys
from unittest.mock import MagicMock
from ..epoche_shield import EpocheShield

def test_mask_custom_vocab_missing_module(caplog):
    """
    Test that masking works even if custom vocab module is missing.
    It should log a INFO message instead of silently passing.
    """
    shield = EpocheShield()
    text = "Some text with sensitive info."

    # Make sure the module is NOT in sys.modules (clean state)
    if "mekhane.poiema.flow.vocab_store" in sys.modules:
        del sys.modules["mekhane.poiema.flow.vocab_store"]

    # Enable logging capture
    with caplog.at_level(logging.INFO, logger="epoche_shield"):
        # Default use_custom_vocab is True
        masked, mapping = shield.mask(text, use_custom_vocab=True)

    # Ensure basics still work
    assert masked == text

    # Assert that we logged the expected message
    assert "Custom vocabulary store not available" in caplog.text
    assert "Skipping custom vocabulary masking" in caplog.text


def test_mask_custom_vocab_generic_exception(caplog, monkeypatch):
    """
    Test that generic exceptions during custom vocab masking are logged as ERROR.
    """
    # Mock vocab_store module
    mock_store_module = MagicMock()
    # Configure it to raise exception when used
    mock_store_instance = MagicMock()
    mock_store_instance.find_in_text.side_effect = ValueError("Simulated runtime error")
    mock_store_module.get_vocab_store.return_value = mock_store_instance

    # Inject into sys.modules
    module_name = "mekhane.poiema.flow.vocab_store"
    monkeypatch.setitem(sys.modules, module_name, mock_store_module)

    shield = EpocheShield()
    text = "test"

    with caplog.at_level(logging.ERROR, logger="epoche_shield"):
         masked, mapping = shield.mask(text, use_custom_vocab=True)

    assert "Error during custom vocabulary masking" in caplog.text
    assert "Simulated runtime error" in caplog.text
