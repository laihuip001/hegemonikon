import json
import logging
import pytest
from mekhane.ccl.macro_registry import MacroRegistry

def test_load_invalid_json(tmp_path, caplog):
    """Test that loading invalid JSON logs an error."""
    # Create a dummy macro file with invalid JSON
    macro_file = tmp_path / "macros.json"
    macro_file.write_text("{invalid_json", encoding="utf-8")

    # Capture logs
    with caplog.at_level(logging.ERROR):
        registry = MacroRegistry(path=macro_file)

    # Verify macros are empty (silent failure for now, or partial load if implemented that way, but here it fails completely)
    assert registry.user_macros == {}

    # Verify that the error was logged
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert "Failed to load user macros" in caplog.records[0].message
