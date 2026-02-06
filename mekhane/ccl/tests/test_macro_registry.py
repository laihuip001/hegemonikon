import pytest
import logging
from pathlib import Path
from mekhane.ccl.macro_registry import MacroRegistry

def test_load_invalid_json(tmp_path, caplog):
    """Test that invalid JSON in macro file logs an error instead of failing silently."""
    # Setup
    f = tmp_path / "macros.json"
    f.write_text("{invalid_json", encoding="utf-8")

    # Enable logging capture
    caplog.set_level(logging.ERROR)

    # Execute
    registry = MacroRegistry(path=f)

    # Verify
    # We expect an error message to be logged
    assert "Failed to load macros" in caplog.text
    # And the registry should still be functional (empty user macros)
    assert registry.user_macros == {}

def test_load_valid_json(tmp_path):
    """Test that valid JSON loads correctly."""
    f = tmp_path / "macros.json"
    content = '[{"name": "test", "ccl": "abc", "description": "desc"}]'
    f.write_text(content, encoding="utf-8")

    registry = MacroRegistry(path=f)

    assert "test" in registry.user_macros
    assert registry.user_macros["test"].ccl == "abc"
