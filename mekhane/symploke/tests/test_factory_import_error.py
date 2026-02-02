# PROOF: [L3/テスト] <- mekhane/symploke/tests/test_factory_import_error.py
"""
Test for error handling in factory.py during adapter registration.
"""

import sys
import logging
import pytest
from unittest.mock import patch

def test_factory_import_error_logging(caplog):
    """
    Test that an ImportError during adapter registration is logged as a warning.
    """
    # Target module to simulate failure for
    adapter_module = "mekhane.symploke.adapters.hnswlib_adapter"
    factory_module = "mekhane.symploke.factory"

    # Remove modules if they are already loaded to force re-import
    if adapter_module in sys.modules:
        del sys.modules[adapter_module]
    if factory_module in sys.modules:
        del sys.modules[factory_module]

    # Simulate ImportError by setting the module in sys.modules to None
    # This causes Python to raise ModuleNotFoundError (subclass of ImportError)
    with patch.dict(sys.modules, {adapter_module: None}):
        with caplog.at_level(logging.WARNING):
            try:
                import mekhane.symploke.factory
            except ImportError:
                # In case the module level import raises (it shouldn't, it catches it)
                pytest.fail("Import of factory raised ImportError, should have been caught.")

            # Verify the warning was logged
            # The message format is: "Could not register 'hnswlib' adapter: {e}"
            assert "Could not register 'hnswlib' adapter" in caplog.text

    # Cleanup: Remove the broken factory module so other tests (if any) reload it correctly
    if factory_module in sys.modules:
        del sys.modules[factory_module]
