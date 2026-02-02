import pytest
import logging
import sys
from unittest.mock import MagicMock, patch
from mekhane.symploke import factory, adapters

def test_register_adapters_missing_hnswlib(caplog):
    """
    Test that _register_adapters logs a warning and does NOT register 'hnswlib'
    when the underlying hnswlib package is missing (simulated by hnswlib_adapter.hnswlib is None).
    """
    factory.VectorStoreFactory._adapters.clear()
    caplog.set_level(logging.WARNING)

    mock_adapter_module = MagicMock()
    mock_adapter_module.hnswlib = None
    mock_adapter_module.HNSWlibAdapter = MagicMock()

    # Patch both the module in sys.modules AND the attribute on the package
    with patch.dict(sys.modules, {"mekhane.symploke.adapters.hnswlib_adapter": mock_adapter_module}):
        with patch.object(adapters, "hnswlib_adapter", mock_adapter_module, create=True):
             factory._register_adapters()

    assert "Could not register 'hnswlib' adapter" in caplog.text
    assert not factory.VectorStoreFactory.is_registered("hnswlib")


def test_register_adapters_present_hnswlib(caplog):
    """
    Test that _register_adapters registers 'hnswlib' when present.
    """
    factory.VectorStoreFactory._adapters.clear()
    caplog.set_level(logging.WARNING)

    mock_adapter_module = MagicMock()
    mock_adapter_module.hnswlib = "present"
    mock_adapter_module.HNSWlibAdapter = MagicMock()

    with patch.dict(sys.modules, {"mekhane.symploke.adapters.hnswlib_adapter": mock_adapter_module}):
        with patch.object(adapters, "hnswlib_adapter", mock_adapter_module, create=True):
            factory._register_adapters()

    assert "Could not register 'hnswlib' adapter" not in caplog.text
    assert factory.VectorStoreFactory.is_registered("hnswlib")
