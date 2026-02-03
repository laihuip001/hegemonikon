import sys
from unittest.mock import patch, MagicMock
from mekhane.anamnesis import ux_utils

def test_print_header():
    # Force HAS_TERMCOLOR to True for the test if it's False, to test the logic
    with patch('mekhane.anamnesis.ux_utils.HAS_TERMCOLOR', True), \
         patch('mekhane.anamnesis.ux_utils.cprint') as mock_cprint, \
         patch('sys.stdout.isatty', return_value=True):
        ux_utils.print_header("Test Header")
        mock_cprint.assert_called_once_with("\nTest Header", color=ux_utils.Colors.HEADER, attrs=['bold'])

def test_print_success():
    with patch('mekhane.anamnesis.ux_utils.HAS_TERMCOLOR', True), \
         patch('mekhane.anamnesis.ux_utils.cprint') as mock_cprint, \
         patch('sys.stdout.isatty', return_value=True):
        ux_utils.print_success("Success")
        mock_cprint.assert_called_once_with("[OK] Success", color=ux_utils.Colors.OKGREEN, attrs=None)

def test_print_error():
    with patch('mekhane.anamnesis.ux_utils.HAS_TERMCOLOR', True), \
         patch('mekhane.anamnesis.ux_utils.cprint') as mock_cprint, \
         patch('sys.stdout.isatty', return_value=True):
        ux_utils.print_error("Error")
        mock_cprint.assert_called_once_with("[!!] Error", color=ux_utils.Colors.FAIL, attrs=['bold'])

def test_print_warning():
    with patch('mekhane.anamnesis.ux_utils.HAS_TERMCOLOR', True), \
         patch('mekhane.anamnesis.ux_utils.cprint') as mock_cprint, \
         patch('sys.stdout.isatty', return_value=True):
        ux_utils.print_warning("Warning")
        mock_cprint.assert_called_once_with("[WARN] Warning", color=ux_utils.Colors.WARNING, attrs=None)

def test_print_info():
    with patch('mekhane.anamnesis.ux_utils.HAS_TERMCOLOR', True), \
         patch('mekhane.anamnesis.ux_utils.cprint') as mock_cprint, \
         patch('sys.stdout.isatty', return_value=True):
        ux_utils.print_info("Info")
        mock_cprint.assert_called_once_with("[INFO] Info", color=ux_utils.Colors.OKCYAN, attrs=None)

def test_print_dim():
    with patch('mekhane.anamnesis.ux_utils.HAS_TERMCOLOR', True), \
         patch('mekhane.anamnesis.ux_utils.cprint') as mock_cprint, \
         patch('sys.stdout.isatty', return_value=True):
        ux_utils.print_dim("Dim text")
        mock_cprint.assert_called_once_with("Dim text", color=None, attrs=['dark'])

def test_print_fallback():
    # Test that it calls standard print when not TTY
    with patch('builtins.print') as mock_print, \
         patch('sys.stdout.isatty', return_value=False):
        ux_utils.print_success("Success")
        mock_print.assert_called_once_with("[OK] Success")
