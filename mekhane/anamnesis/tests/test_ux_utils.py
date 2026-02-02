import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure we can import the new module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from mekhane.anamnesis.ux_utils import Colors, print_header, print_success, print_error

class TestUxUtils(unittest.TestCase):
    @patch('mekhane.anamnesis.ux_utils.cprint')
    def test_print_header(self, mock_cprint):
        print_header("Test Header")
        mock_cprint.assert_called_with("\n=== Test Header ===", Colors.HEADER, attrs=["bold"])

    @patch('mekhane.anamnesis.ux_utils.cprint')
    def test_print_success(self, mock_cprint):
        print_success("Success Message")
        mock_cprint.assert_called_with("✓ Success Message", Colors.SUCCESS)

    @patch('mekhane.anamnesis.ux_utils.cprint')
    def test_print_error(self, mock_cprint):
        print_error("Error Message")
        mock_cprint.assert_called_with("✗ Error Message", Colors.ERROR, attrs=["bold"])

if __name__ == '__main__':
    unittest.main()
