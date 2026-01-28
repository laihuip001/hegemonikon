import unittest
from unittest.mock import patch, MagicMock
from mekhane.anamnesis.ux_utils import _c, print_header, print_success, print_error, print_warning, Spinner

class TestUxUtils(unittest.TestCase):
    def test_color_formatting(self):
        # Test with color enabled
        with patch('mekhane.anamnesis.ux_utils.USE_COLOR', True):
            self.assertEqual(_c('RED', 'text'), 'REDtext\033[0m')

        # Test with color disabled
        with patch('mekhane.anamnesis.ux_utils.USE_COLOR', False):
            self.assertEqual(_c('RED', 'text'), 'text')

    @patch('builtins.print')
    def test_print_functions(self, mock_print):
        print_header("Header")
        mock_print.assert_called()

        print_success("Success")
        mock_print.assert_called()

        print_error("Error")
        mock_print.assert_called()

    def test_spinner(self):
        # Just ensure it doesn't crash
        with Spinner("Testing"):
            pass

if __name__ == '__main__':
    unittest.main()
