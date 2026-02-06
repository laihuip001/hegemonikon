import logging
import pytest
from pathlib import Path
from mekhane.ccl.workflow_signature import SignatureRegistry

def test_add_from_yaml_invalid_yaml(tmp_path, caplog):
    """Test that add_from_yaml logs an error when encountering invalid YAML."""
    registry = SignatureRegistry()

    # Create a temporary file with invalid YAML (unbalanced brackets)
    workflow_file = tmp_path / "invalid.md"
    workflow_file.write_text("""---
ccl_signature: /test
description: "Test workflow"
tags: [unclosed_list
---
Workflow content
""")

    # Configure logging to capture output
    caplog.set_level(logging.ERROR)

    # Call add_from_yaml
    registry.add_from_yaml(workflow_file)

    # Verify that an error was logged
    # Note: Before the fix, this will fail because nothing is logged.
    assert "Failed to load workflow signature" in caplog.text
    assert str(workflow_file) in caplog.text
