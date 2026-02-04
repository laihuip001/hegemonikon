"""
Tests for mekhane.anamnesis.ux_utils
"""

import pytest
from mekhane.anamnesis import ux_utils


def test_colorize_usage():
    # Green (< 50%)
    res = ux_utils.colorize_usage(40, 100)
    assert "40 / 100 (40.0%)" in res

    # Yellow (< 80%)
    res = ux_utils.colorize_usage(70, 100)
    assert "70 / 100 (70.0%)" in res

    # Red (>= 80%)
    res = ux_utils.colorize_usage(90, 100)
    assert "90 / 100 (90.0%)" in res

    # Zero limit
    res = ux_utils.colorize_usage(0, 0)
    assert "0/0" in res


def test_print_success(capsys):
    ux_utils.print_success("Operation completed")
    captured = capsys.readouterr()
    assert "Operation completed" in captured.out
    assert ux_utils.CHECK in captured.out
    assert "[SUCCESS]" in captured.out


def test_print_error(capsys):
    ux_utils.print_error("Operation failed")
    captured = capsys.readouterr()
    assert "Operation failed" in captured.out
    assert ux_utils.CROSS in captured.out
    assert "[ERROR]" in captured.out


def test_print_warning(capsys):
    ux_utils.print_warning("Operation warning")
    captured = capsys.readouterr()
    assert "Operation warning" in captured.out
    assert ux_utils.WARN in captured.out
    assert "[WARNING]" in captured.out


def test_print_info(capsys):
    ux_utils.print_info("Operation info")
    captured = capsys.readouterr()
    assert "Operation info" in captured.out
    assert ux_utils.INFO in captured.out
    assert "[INFO]" in captured.out


def test_print_header(capsys):
    ux_utils.print_header("My Header")
    captured = capsys.readouterr()
    assert "=== My Header ===" in captured.out
