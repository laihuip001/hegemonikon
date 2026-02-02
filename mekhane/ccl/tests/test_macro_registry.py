import unittest
from unittest.mock import MagicMock, patch
import logging
from mekhane.ccl.macro_registry import MacroRegistry

class TestMacroRegistryErrorHandling(unittest.TestCase):

    def setUp(self):
        # Ensure the logger propagates so assertLogs can catch it,
        # though assertLogs usually attaches a handler to the logger.
        pass

    def test_load_invalid_json_logs_error(self):
        """Test that invalid JSON in the macro file results in a logged error."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "invalid json content"

        # Current implementation: pass silently. Test expectation: Log ERROR.
        # This will fail initially because no log is emitted.
        with self.assertLogs('mekhane.ccl.macro_registry', level='ERROR') as cm:
            MacroRegistry(path=mock_path)

        self.assertTrue(any("Failed to load macros" in o for o in cm.output))

    def test_load_os_error_logs_error(self):
        """Test that OSError during load is caught and logged."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.read_text.side_effect = OSError("Disk read error")

        # Current implementation: Raises OSError. Test expectation: Log ERROR.
        with self.assertLogs('mekhane.ccl.macro_registry', level='ERROR') as cm:
            MacroRegistry(path=mock_path)

        self.assertTrue(any("Disk read error" in o for o in cm.output))

    def test_save_error_logs_error(self):
        """Test that OSError during save is caught and logged."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False # Avoid loading logic
        mock_path.parent.mkdir.return_value = None
        mock_path.write_text.side_effect = OSError("Write protected")

        registry = MacroRegistry(path=mock_path)

        # Current implementation: Raises OSError. Test expectation: Log ERROR.
        with self.assertLogs('mekhane.ccl.macro_registry', level='ERROR') as cm:
            registry.define("test_macro", "/test")

        self.assertTrue(any("Write protected" in o for o in cm.output))
