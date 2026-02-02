# PROOF: [L3/テスト] <- mekhane/anamnesis/tests/ vault.py が存在→その検証が必要→test_vault が担う
import unittest
import shutil
import tempfile
import os
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from mekhane.anamnesis.vault import VaultManager


class TestVaultManager(unittest.TestCase):
    """Tests for VaultManager static methods."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_path = Path(self.test_dir) / "test.txt"
        self.json_path = Path(self.test_dir) / "test.json"
        self.yaml_path = Path(self.test_dir) / "test.yaml"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_write_read_file(self):
        """write_safe and read_safe work correctly."""
        content = "Hello Vault"
        VaultManager.write_safe(self.file_path, content)
        read_content = VaultManager.read_safe(self.file_path)
        self.assertEqual(content, read_content)

    def test_backup_creation(self):
        """write_safe creates backup when file exists."""
        # Initial write
        VaultManager.write_safe(self.file_path, "v1")

        # Second write should trigger backup
        VaultManager.write_safe(self.file_path, "v2")

        # Check main file
        self.assertEqual(VaultManager.read_safe(self.file_path), "v2")

        # Check backup file
        backup_path = self.file_path.with_suffix(self.file_path.suffix + ".bak")
        self.assertTrue(backup_path.exists())
        with open(backup_path, "r") as f:
            self.assertEqual(f.read(), "v1")

    def test_read_fallback(self):
        """read_safe falls back to backup when main file is missing."""
        backup_path = self.file_path.with_suffix(self.file_path.suffix + ".bak")

        # Write backup only
        with open(backup_path, "w") as f:
            f.write("backup content")

        # Ensure main file does not exist
        if self.file_path.exists():
            os.remove(self.file_path)

        content = VaultManager.read_safe(self.file_path)
        self.assertEqual(content, "backup content")

    def test_file_not_found(self):
        """read_safe raises FileNotFoundError when no file or backup exists."""
        non_existent = Path(self.test_dir) / "non_existent.txt"
        with self.assertRaises(FileNotFoundError):
            VaultManager.read_safe(non_existent)

    @patch("mekhane.anamnesis.vault.tempfile.NamedTemporaryFile")
    @patch("mekhane.anamnesis.vault.logger")
    @patch("mekhane.anamnesis.vault.Path")
    def test_cleanup_failure_logging(self, MockPath, mock_logger, MockTempFile):
        """write_safe logs warning when temp file cleanup fails."""
        # Setup mock instance for Path
        mock_path_instance = MockPath.return_value

        # Configure mocks to fail at replace and unlink
        mock_path_instance.replace.side_effect = IOError("Simulated Write Failure")
        mock_path_instance.exists.return_value = True
        mock_path_instance.unlink.side_effect = OSError("Simulated Unlink Failure")

        # Configure parent.mkdir to do nothing
        mock_path_instance.parent.mkdir.return_value = None

        # Configure TempFile
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/mock_file"
        MockTempFile.return_value.__enter__.return_value = mock_temp

        # Execute
        with self.assertRaises(IOError) as cm:
            VaultManager.write_safe("dummy_path", "content", backup=False)

        # Verify
        self.assertIn("Failed to write file safely", str(cm.exception))

        # Check that warning was called with the expected message pattern
        found = False
        for call in mock_logger.warning.call_args_list:
            args, _ = call
            if "Failed to delete temporary file" in args[0]:
                found = True
                break

        self.assertTrue(found, "Warning log for cleanup failure was not found")


if __name__ == "__main__":
    unittest.main()
