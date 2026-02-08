# PROOF: [L3/テスト] <- mekhane/anamnesis/tests/ vault.py が存在→その検証が必要→test_vault が担う
import unittest
import shutil
import tempfile
import os
import json
import yaml
from pathlib import Path
from mekhane.anamnesis.vault import VaultManager


# PURPOSE: Tests for VaultManager static methods
class TestVaultManager(unittest.TestCase):
    """Tests for VaultManager static methods."""

    # PURPOSE: setUp をセットアップする
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_path = Path(self.test_dir) / "test.txt"
        self.json_path = Path(self.test_dir) / "test.json"
        self.yaml_path = Path(self.test_dir) / "test.yaml"

    # PURPOSE: tearDown の処理
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    # PURPOSE: write_safe and read_safe work correctly
    def test_write_read_file(self):
        """write_safe and read_safe work correctly."""
        content = "Hello Vault"
        VaultManager.write_safe(self.file_path, content)
        read_content = VaultManager.read_safe(self.file_path)
        self.assertEqual(content, read_content)

    # PURPOSE: write_safe creates backup when file exists
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

    # PURPOSE: read_safe falls back to backup when main file is missing
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

    # PURPOSE: read_safe raises FileNotFoundError when no file or backup exists
    def test_file_not_found(self):
        """read_safe raises FileNotFoundError when no file or backup exists."""
        non_existent = Path(self.test_dir) / "non_existent.txt"
        with self.assertRaises(FileNotFoundError):
            VaultManager.read_safe(non_existent)


if __name__ == "__main__":
    unittest.main()
