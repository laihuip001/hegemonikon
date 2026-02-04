import sys
import pytest
from mekhane.anamnesis.ux_utils import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    colorize_usage,
)


def test_print_success(capsys):
    print_success("Operation completed")
    captured = capsys.readouterr()
    # Check for the tick mark and text
    assert "✓ Operation completed" in captured.out


def test_print_error(capsys):
    print_error("Operation failed")
    captured = capsys.readouterr()
    # Check for the cross mark and text in stderr
    assert "✗ Operation failed" in captured.err


def test_print_warning(capsys):
    print_warning("Be careful")
    captured = capsys.readouterr()
    assert "⚠ Be careful" in captured.out


def test_print_info(capsys):
    print_info("Processing", label="Status")
    captured = capsys.readouterr()
    assert "ℹ Status: Processing" in captured.out


def test_print_header(capsys):
    print_header("Section 1")
    captured = capsys.readouterr()
    assert "[Section 1]" in captured.out


def test_colorize_usage_low():
    # 50/100 = 50% (Green)
    result = colorize_usage(50, 100)
    assert "50 / 100 (50.0%)" in result


def test_colorize_usage_medium():
    # 80/100 = 80% (Yellow)
    result = colorize_usage(80, 100)
    assert "80 / 100 (80.0%)" in result


def test_colorize_usage_high():
    # 95/100 = 95% (Red)
    result = colorize_usage(95, 100)
    assert "95 / 100 (95.0%)" in result

def test_colorize_usage_zero_limit():
    result = colorize_usage(10, 0)
    assert "10 / 0" in result
