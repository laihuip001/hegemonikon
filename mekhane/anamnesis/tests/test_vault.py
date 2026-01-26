import unittest
import shutil
import tempfile
import os
import json
import yaml
from pathlib import Path
from mekhane.anamnesis.vault import VaultManager

class TestVaultManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault = VaultManager(self.test_dir)
        self.file_path = "test.txt"
        self.json_path = "test.json"
        self.yaml_path = "test.yaml"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_write_read_file(self):
        content = "Hello Vault"
        self.vault.write_file(self.file_path, content)
        read_content = self.vault.read_file(self.file_path)
        self.assertEqual(content, read_content)

    def test_backup_creation(self):
        # Initial write
        self.vault.write_file(self.file_path, "v1")

        # Second write should trigger backup
        self.vault.write_file(self.file_path, "v2")

        # Check main file
        self.assertEqual(self.vault.read_file(self.file_path), "v2")

        # Check backup file
        backup_path = Path(self.test_dir) / (self.file_path + ".bak")
        self.assertTrue(backup_path.exists())
        with open(backup_path, 'r') as f:
            self.assertEqual(f.read(), "v1")

    def test_read_fallback(self):
        # Create a file and backup manually
        path = Path(self.test_dir) / self.file_path
        backup_path = Path(self.test_dir) / (self.file_path + ".bak")

        # Write backup
        with open(backup_path, 'w') as f:
            f.write("backup")

        # Ensure main file does not exist to trigger FileNotFoundError fallback
        if path.exists():
            os.remove(path)

        content = self.vault.read_file(self.file_path)
        self.assertEqual(content, "backup")

    def test_json_backup_recovery(self):
        data_v1 = {"version": 1}
        data_v2 = {"version": 2}

        self.vault.write_json(self.json_path, data_v1)
        self.vault.write_json(self.json_path, data_v2)

        # corrupt main file
        path = Path(self.test_dir) / self.json_path
        with open(path, 'w') as f:
            f.write("{invalid_json")

        recovered = self.vault.read_json(self.json_path)
        self.assertEqual(recovered, data_v1)

    def test_yaml_backup_recovery(self):
        data_v1 = {"version": 1}
        data_v2 = {"version": 2}

        self.vault.write_yaml(self.yaml_path, data_v1)
        self.vault.write_yaml(self.yaml_path, data_v2)

        # corrupt main file
        path = Path(self.test_dir) / self.yaml_path
        with open(path, 'w') as f:
            f.write(": invalid_yaml")

        recovered = self.vault.read_yaml(self.yaml_path)
        self.assertEqual(recovered, data_v1)

if __name__ == '__main__':
    unittest.main()
