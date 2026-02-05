import unittest
from unittest.mock import patch
from mekhane.anamnesis import ux_utils


class TestUxUtils(unittest.TestCase):

    @patch("mekhane.anamnesis.ux_utils.cprint")
    def test_print_success(self, mock_cprint):
        ux_utils.print_success("test message")
        mock_cprint.assert_called_with("✅ test message", "green")

    @patch("mekhane.anamnesis.ux_utils.cprint")
    def test_print_error(self, mock_cprint):
        ux_utils.print_error("test message")
        mock_cprint.assert_called_with("❌ test message", "red")

    @patch("mekhane.anamnesis.ux_utils.cprint")
    def test_print_warning(self, mock_cprint):
        ux_utils.print_warning("test message")
        mock_cprint.assert_called_with("⚠️  test message", "yellow")

    @patch("mekhane.anamnesis.ux_utils.cprint")
    def test_print_info(self, mock_cprint):
        ux_utils.print_info("test message")
        mock_cprint.assert_called_with("ℹ️  test message", "cyan")

    @patch("mekhane.anamnesis.ux_utils.cprint")
    def test_print_header(self, mock_cprint):
        ux_utils.print_header("test message")
        mock_cprint.assert_called_with("\ntest message", attrs=["bold", "underline"])

    @patch("mekhane.anamnesis.ux_utils.colored")
    def test_colorize_usage(self, mock_colored):
        ux_utils.colorize_usage("50%")
        mock_colored.assert_called_with("50%", "cyan")


if __name__ == "__main__":
    unittest.main()
