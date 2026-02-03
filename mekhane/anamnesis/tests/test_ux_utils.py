import pytest
from mekhane.anamnesis.ux_utils import colorize_usage

def test_colorize_usage():
    # Check output format
    assert "800/1,000 (80.0%)" in colorize_usage(800, 1000)
    # Check division by zero handling
    assert "100/0 (?%)" in colorize_usage(100, 0)
