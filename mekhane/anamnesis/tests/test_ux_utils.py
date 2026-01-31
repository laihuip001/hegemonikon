"""
Tests for UX Utilities
"""

import sys
from unittest.mock import patch
from mekhane.anamnesis.ux_utils import Colors, print_header, print_success, print_error, print_warning, print_info, print_dim

def test_print_header(capsys):
    with patch('sys.stdout.isatty', return_value=True):
        print_header("Header")
        captured = capsys.readouterr()
        assert Colors.BOLD + Colors.CYAN in captured.out
        assert "Header" in captured.out
        assert Colors.RESET in captured.out

def test_print_success(capsys):
    with patch('sys.stdout.isatty', return_value=True):
        print_success("Success")
        captured = capsys.readouterr()
        assert Colors.GREEN in captured.out
        assert "✔ Success" in captured.out

def test_print_error(capsys):
    with patch('sys.stdout.isatty', return_value=True):
        print_error("Error")
        captured = capsys.readouterr()
        assert Colors.RED in captured.out
        assert "✘ Error" in captured.out

def test_print_warning(capsys):
    with patch('sys.stdout.isatty', return_value=True):
        print_warning("Warning")
        captured = capsys.readouterr()
        assert Colors.YELLOW in captured.out
        assert "⚠ Warning" in captured.out

def test_print_info(capsys):
    with patch('sys.stdout.isatty', return_value=True):
        print_info("Info")
        captured = capsys.readouterr()
        assert Colors.BLUE in captured.out
        assert "ℹ Info" in captured.out

def test_print_dim(capsys):
    with patch('sys.stdout.isatty', return_value=True):
        print_dim("Dim")
        captured = capsys.readouterr()
        assert Colors.DIM in captured.out
        assert "Dim" in captured.out

def test_no_color_when_not_tty(capsys):
    with patch('sys.stdout.isatty', return_value=False):
        print_success("Success")
        captured = capsys.readouterr()
        # Should not have color codes
        assert Colors.GREEN not in captured.out
        # Should still have content
        assert "✔ Success" in captured.out
