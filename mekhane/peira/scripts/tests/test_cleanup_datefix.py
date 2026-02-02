import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import importlib.util
from unittest.mock import MagicMock

# Mock dependencies that might be missing in the test environment
sys.modules['requests'] = MagicMock()
sys.modules['bs4'] = MagicMock()

# Load the module dynamically due to hyphen in filename
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_PATH = os.path.join(CURRENT_DIR, "..", "cleanup-datefix.py")
spec = importlib.util.spec_from_file_location("cleanup_datefix", MODULE_PATH)
cleanup_datefix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup_datefix)

class TestCleanupDatefix(unittest.TestCase):
    @patch('os.rmdir')
    @patch('builtins.print')
    def test_safe_rmdir_success(self, mock_print, mock_rmdir):
        path = "dummy/path"
        cleanup_datefix.safe_rmdir(path)

        mock_rmdir.assert_called_once_with(path)
        # Verify print output contains success message
        # We look for partial match in arguments
        found = False
        for call_args in mock_print.call_args_list:
            if "Removed empty directory" in str(call_args):
                found = True
                break
        self.assertTrue(found, "Success message not printed")

    @patch('os.rmdir')
    @patch('builtins.print')
    def test_safe_rmdir_not_empty(self, mock_print, mock_rmdir):
        path = "dummy/path"
        # Simulate directory not empty (errno 39 on Linux, 66 on some others, WinError 145)
        # We can just check that generic OSError handling catches it or specific check
        mock_rmdir.side_effect = OSError(39, "Directory not empty")

        cleanup_datefix.safe_rmdir(path)

        mock_rmdir.assert_called_once_with(path)
        found = False
        for call_args in mock_print.call_args_list:
            if "Directory not empty" in str(call_args) or "Error removing" in str(call_args):
                found = True
                break
        self.assertTrue(found, "Error message not printed")

    @patch('os.rmdir')
    @patch('builtins.print')
    def test_safe_rmdir_other_error(self, mock_print, mock_rmdir):
        path = "dummy/path"
        mock_rmdir.side_effect = OSError(13, "Permission denied")

        cleanup_datefix.safe_rmdir(path)

        mock_rmdir.assert_called_once_with(path)
        found = False
        for call_args in mock_print.call_args_list:
            if "Error removing" in str(call_args):
                found = True
                break
        self.assertTrue(found, "Generic error message not printed")

if __name__ == '__main__':
    unittest.main()
