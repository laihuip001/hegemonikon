import sys
import unittest
from unittest.mock import patch, MagicMock
from mekhane.anamnesis import ux_utils

class TestUxUtils(unittest.TestCase):
    def test_colors_class(self):
        self.assertTrue(hasattr(ux_utils.Colors, 'HEADER'))
        self.assertTrue(hasattr(ux_utils.Colors, 'SUCCESS'))
        self.assertTrue(hasattr(ux_utils.Colors, 'ERROR'))

    @patch('mekhane.anamnesis.ux_utils.cprint')
    def test_print_functions(self, mock_cprint):
        ux_utils.print_header("Test Header")
        mock_cprint.assert_called_with("\n=== Test Header ===", ux_utils.Colors.HEADER, attrs=["bold"])

        ux_utils.print_success("Test Success")
        mock_cprint.assert_called_with("✓ Test Success", ux_utils.Colors.SUCCESS)

        ux_utils.print_error("Test Error")
        mock_cprint.assert_called_with("✗ Test Error", ux_utils.Colors.ERROR)

if __name__ == '__main__':
    unittest.main()
