import pytest
from pathlib import Path
import json
import logging
import os
from mekhane.ccl.macro_registry import MacroRegistry

def test_load_corrupted_json(tmp_path, caplog):
    """Test that a corrupted JSON file is backed up and an empty registry is initialized."""
    # Setup
    macro_file = tmp_path / "ccl_macros.json"
    macro_file.write_text("{invalid_json")  # Write invalid JSON

    # Execute
    # We expect the log to capture the error
    with caplog.at_level(logging.ERROR):
        registry = MacroRegistry(path=macro_file)

    # Verify
    assert len(registry.user_macros) == 0

    # Check that original file is gone (renamed)
    assert not macro_file.exists(), "Original corrupted file should be moved"

    # Check that backup file exists
    backup_file = macro_file.with_name(macro_file.name + ".bak")
    assert backup_file.exists(), f"Backup file {backup_file} should exist"
    assert backup_file.read_text() == "{invalid_json"

    # Check logs
    assert "Failed to load user macros" in caplog.text
