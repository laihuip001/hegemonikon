import pytest
import logging
from unittest.mock import patch
import sys
from pathlib import Path

# Ensure the package is in python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mekhane.symploke.factory import _register_adapters

def test_register_adapters_logging(caplog):
    """Test that ImportError during adapter registration is logged."""
    # Set logging level to capture warnings
    caplog.set_level(logging.WARNING)

    # Mock the module to be None to trigger ImportError
    # We use ModuleNotFoundError as it is a subclass of ImportError
    with patch.dict(sys.modules, {'mekhane.symploke.adapters.hnswlib_adapter': None}):
        _register_adapters()

    # Assert that a warning was logged
    assert "Failed to register adapter 'hnswlib'" in caplog.text
