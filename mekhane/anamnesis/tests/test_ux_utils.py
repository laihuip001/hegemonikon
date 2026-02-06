"""
Tests for ux_utils.py
"""

import sys
import unittest
from io import StringIO
from unittest.mock import patch
from mekhane.anamnesis.ux_utils import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    colorize_usage,
)


class TestUxUtils(unittest.TestCase):
    def test_colorize_usage(self):
        # Test low usage (green)
        res = colorize_usage(10, 100)
        self.assertIn("10 / 100", res)

        # Test high usage (red)
        res = colorize_usage(95, 100)
        self.assertIn("95 / 100", res)

        # Test zero limit
        res = colorize_usage(0, 0)
        self.assertEqual(res, "0 / 0")

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_functions(self, mock_stdout):
        print_success("Success message")
        self.assertIn("Success message", mock_stdout.getvalue())

        # Clear buffer
        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        print_error("Error message")
        self.assertIn("Error message", mock_stdout.getvalue())

        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        print_warning("Warning message")
        self.assertIn("Warning message", mock_stdout.getvalue())

        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        print_info("Info message")
        self.assertIn("Info message", mock_stdout.getvalue())

        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        print_header("Header message")
        self.assertIn("Header message", mock_stdout.getvalue())
        self.assertIn("======", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
