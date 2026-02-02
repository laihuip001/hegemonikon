
import pytest
import logging
import sys
from unittest.mock import MagicMock, patch
from ..epoche_shield import EpocheShield

def test_mask_custom_vocab_missing_module(caplog):
    """
    Test that masking logs info when custom vocab module is missing.
    """
    shield = EpocheShield()
    text = "Some text."

    # Make sure the module is not in sys.modules
    with patch.dict(sys.modules):
        if 'mekhane.poiema.flow.vocab_store' in sys.modules:
            del sys.modules['mekhane.poiema.flow.vocab_store']

        with caplog.at_level(logging.INFO):
            masked, mapping = shield.mask(text, use_custom_vocab=True)

    assert masked == text
    assert "Custom vocab store not found" in caplog.text


def test_mask_custom_vocab_exception(caplog):
    """
    Test that masking logs error when custom vocab raises exception.
    """
    shield = EpocheShield()
    text = "Some text."

    # Mock the module
    mock_vocab_store = MagicMock()
    mock_get_vocab_store = MagicMock()
    mock_vocab_store.get_vocab_store = mock_get_vocab_store

    # Make get_vocab_store raise an exception
    mock_get_vocab_store.side_effect = RuntimeError("Something went wrong")

    # We need to patch the import. Since it's a relative import 'from .vocab_store',
    # it resolves to 'mekhane.poiema.flow.vocab_store'.

    with patch.dict(sys.modules, {'mekhane.poiema.flow.vocab_store': mock_vocab_store}):
        with caplog.at_level(logging.ERROR):
            masked, mapping = shield.mask(text, use_custom_vocab=True)

    assert masked == text
    assert "Error during custom vocabulary masking: Something went wrong" in caplog.text
