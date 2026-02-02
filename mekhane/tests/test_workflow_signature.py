import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
import yaml
import pytest
from mekhane.ccl.workflow_signature import SignatureRegistry

def test_add_from_yaml_malformed(caplog):
    """Test that malformed YAML logs a warning."""
    registry = SignatureRegistry()
    # We mock Path object passed to the method, but the method calls .read_text() on it.
    # It's easier to use a real file or mock the method's internal Path usage if possible.
    # But add_from_yaml takes a Path object.

    malformed_path = MagicMock(spec=Path)
    malformed_path.exists.return_value = True
    malformed_path.read_text.return_value = """---
ccl_signature: /test
  indentation: error
---
"""
    malformed_path.stem = "malformed_test"
    malformed_path.__str__.return_value = "malformed_test.md"

    with caplog.at_level(logging.WARNING):
        registry.add_from_yaml(malformed_path)

        assert "Failed to parse workflow signature" in caplog.text

def test_add_from_yaml_valid(caplog):
    """Test that valid YAML is parsed correctly."""
    registry = SignatureRegistry()

    valid_path = MagicMock(spec=Path)
    valid_path.exists.return_value = True
    valid_path.read_text.return_value = """---
ccl_signature: /valid_sig
description: valid description
has_side_effects: false
---
"""
    valid_path.stem = "valid_test"

    with caplog.at_level(logging.WARNING):
        registry.add_from_yaml(valid_path)

        # Check if signature was added
        sig = registry.get("/valid_test")
        assert sig is not None
        assert sig.ccl_signature == "/valid_sig"
        assert sig.has_side_effects is False

        # Ensure no warnings were logged
        assert not caplog.text
