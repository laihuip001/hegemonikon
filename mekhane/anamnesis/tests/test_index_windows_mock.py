import sys
import unittest
from unittest.mock import patch, MagicMock
import io
import os

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

class TestIndexWindowsCompat(unittest.TestCase):
    def test_reconfigure_stdout_warning(self):
        # We need to test the module level execution.
        target_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../index.py"))

        with open(target_file, 'r', encoding='utf-8') as f:
            code = f.read()

        # Scenario 1: Exception during reconfigure -> Warning
        mock_stdout = MagicMock()
        mock_stdout.reconfigure.side_effect = Exception("Test Error")

        captured_stderr = io.StringIO()

        with patch('sys.platform', 'win32'), \
             patch('sys.stdout', mock_stdout), \
             patch('sys.stderr', captured_stderr):

            global_vars = {"__file__": target_file, "__name__": "__main__"}
            try:
                exec(code, global_vars)
            except Exception:
                # Ignore other errors (imports etc) that might happen during exec
                pass

        self.assertIn("Warning: Failed to set console encoding: Test Error", captured_stderr.getvalue())

    def test_reconfigure_stdout_attribute_error(self):
        target_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../index.py"))
        with open(target_file, 'r', encoding='utf-8') as f:
            code = f.read()

        # Scenario 2: AttributeError -> No Warning
        mock_stdout = MagicMock()
        mock_stdout.reconfigure.side_effect = AttributeError("No reconfigure")

        captured_stderr = io.StringIO()

        with patch('sys.platform', 'win32'), \
             patch('sys.stdout', mock_stdout), \
             patch('sys.stderr', captured_stderr):

            global_vars = {"__file__": target_file, "__name__": "__main__"}
            try:
                exec(code, global_vars)
            except Exception:
                pass

        self.assertEqual(captured_stderr.getvalue(), "")

if __name__ == '__main__':
    unittest.main()
