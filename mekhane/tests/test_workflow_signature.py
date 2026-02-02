import pytest
import logging
import tempfile
import os
from pathlib import Path
from mekhane.ccl.workflow_signature import SignatureRegistry

def test_add_from_yaml_logs_warning_on_error(caplog):
    """
    Test that add_from_yaml logs a warning when YAML parsing fails.
    """
    registry = SignatureRegistry()

    # Create a temporary file with invalid YAML
    # We use delete=False to ensure the file exists when we pass the path
    # and then manually clean it up.
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
        tmp.write("---\n")
        tmp.write("key: : value\n") # Invalid YAML syntax
        tmp.write("---\n")
        tmp_path = Path(tmp.name)

    try:
        # Capture logs
        with caplog.at_level(logging.WARNING):
             registry.add_from_yaml(tmp_path)

        # Check if any warning log contains the expected message
        # This assertion is expected to FAIL before the fix
        found = False
        for record in caplog.records:
            if "Failed to parse workflow signature" in record.message:
                found = True
                break

        assert found, "Expected a warning log about YAML parsing failure, but none was found."

    finally:
        # Cleanup
        if tmp_path.exists():
            os.unlink(tmp_path)
