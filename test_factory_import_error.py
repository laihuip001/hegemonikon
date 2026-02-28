import sys
from unittest.mock import patch
import logging

def test_import_error():
    with patch.dict(sys.modules, {'mekhane.symploke.adapters.hnswlib_adapter': None}):
        with patch('logging.getLogger') as mock_getLogger:
            # We need to reload the module to trigger _register_adapters
            import importlib
            import mekhane.symploke.factory
            importlib.reload(mekhane.symploke.factory)

            mock_logger = mock_getLogger.return_value
            mock_logger.warning.assert_called()
            args = mock_logger.warning.call_args[0]
            assert args[0] == "Failed to import adapter 'hnswlib'. It will not be available. Error: %s"
            assert isinstance(args[1], ImportError)

if __name__ == '__main__':
    test_import_error()
    print("Test passed!")
