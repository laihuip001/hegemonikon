import unittest
import shutil
import tempfile
from pathlib import Path
import json
import yaml
from mekhane.anamnesis.vault import VaultManager

class TestVaultManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.vault = VaultManager(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_init(self):
        self.assertTrue((self.test_dir / ".hegemonikon").exists())
        self.assertTrue((self.test_dir / ".hegemonikon" / "backups").exists())

    def test_write_read_file(self):
        filename = "test.txt"
        content = "Hello Vault"
        self.vault.write_file(filename, content)
        read_content = self.vault.read_file(filename)
        self.assertEqual(content, read_content)

    def test_backup_creation(self):
        filename = "backup_test.txt"
        content1 = "Version 1"
        content2 = "Version 2"

        # First write, no backup yet because file didn't exist
        self.vault.write_file(filename, content1)
        self.assertEqual(len(self.vault.list_backups(filename)), 0)

        # Second write, should backup version 1
        self.vault.write_file(filename, content2)
        backups = self.vault.list_backups(filename)
        self.assertEqual(len(backups), 1)

        with open(backups[0], 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), content1)

    def test_restore_backup(self):
        filename = "restore_test.txt"
        content1 = "Version 1"
        content2 = "Version 2"

        self.vault.write_file(filename, content1)
        self.vault.write_file(filename, content2)

        # Current content should be Version 2
        self.assertEqual(self.vault.read_file(filename), content2)

        # Restore from backup (Version 1)
        self.assertTrue(self.vault.restore_backup(filename))

        # Current content should be Version 1
        self.assertEqual(self.vault.read_file(filename), content1)

        # Check if broken version was backed up
        broken_backups = list(self.vault.backup_dir.glob(f"{filename}.broken.*.bak"))
        self.assertEqual(len(broken_backups), 1)
        with open(broken_backups[0], 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), content2)

    def test_json_operations(self):
        filename = "data.json"
        data = {"key": "value", "list": [1, 2, 3]}
        self.vault.write_json(filename, data)
        read_data = self.vault.read_json(filename)
        self.assertEqual(data, read_data)

        # Modify and verify backup
        data2 = {"key": "value2"}
        self.vault.write_json(filename, data2)
        backups = self.vault.list_backups(filename)
        self.assertEqual(len(backups), 1)

    def test_yaml_operations(self):
        filename = "data.yaml"
        data = {"key": "value", "list": [1, 2, 3]}
        self.vault.write_yaml(filename, data)
        read_data = self.vault.read_yaml(filename)
        self.assertEqual(data, read_data)

    def test_corrupt_json(self):
        filename = "corrupt.json"
        filepath = self.vault.hegemonikon_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("{invalid json")

        self.assertIsNone(self.vault.read_json(filename))

if __name__ == '__main__':
    unittest.main()
