import unittest
import shutil
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from mekhane.anamnesis.memory import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.vault_root = Path(self.test_dir.name) / "vault"
        self.cache_dir = Path(self.test_dir.name) / "cache"
        self.hegemonikon_dir = self.vault_root / ".hegemonikon"

        # Create Vault structure
        self.hegemonikon_dir.mkdir(parents=True)

        # Initialize MemoryManager with test paths
        self.manager = MemoryManager(vault_root=self.vault_root, cache_dir=self.cache_dir)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_load_from_vault(self):
        # Setup: Create a file in Vault
        filename = "test.json"
        data = {"key": "value"}
        (self.hegemonikon_dir / filename).write_text(json.dumps(data), encoding='utf-8')

        # Test: Load from Vault
        loaded = self.manager.load(filename)
        self.assertEqual(loaded, data)

        # Verify: Cache updated
        cache_file = self.cache_dir / filename
        self.assertTrue(cache_file.exists())
        self.assertEqual(json.loads(cache_file.read_text()), data)

    def test_load_from_cache_when_vault_unavailable(self):
        # Setup: Create a file in Cache but not Vault (simulating offline mode or Vault failure)
        filename = "cached.json"
        data = {"offline": True}
        (self.cache_dir).mkdir(parents=True, exist_ok=True)
        (self.cache_dir / filename).write_text(json.dumps(data), encoding='utf-8')

        # Test: Load
        # Temporarily rename Vault to simulate inaccess
        shutil.rmtree(self.vault_root)

        loaded = self.manager.load(filename)
        self.assertEqual(loaded, data)

    def test_save_syncs_to_vault(self):
        filename = "save_test.json"
        data = {"saved": True}

        # Test: Save
        success = self.manager.save(filename, data)
        self.assertTrue(success)

        # Verify: Saved to Vault
        vault_file = self.hegemonikon_dir / filename
        self.assertTrue(vault_file.exists())
        self.assertEqual(json.loads(vault_file.read_text()), data)

        # Verify: Saved to Cache
        cache_file = self.cache_dir / filename
        self.assertTrue(cache_file.exists())
        self.assertEqual(json.loads(cache_file.read_text()), data)

    def test_save_offline_cache_only(self):
        filename = "offline_save.json"
        data = {"offline_save": True}

        # Simulate offline
        shutil.rmtree(self.vault_root)

        # Test: Save
        success = self.manager.save(filename, data)
        self.assertTrue(success)

        # Verify: Saved to Cache
        cache_file = self.cache_dir / filename
        self.assertTrue(cache_file.exists())
        self.assertEqual(json.loads(cache_file.read_text()), data)

    def test_yaml_fallback(self):
        # Test yaml string handling if yaml module is missing (or mocked missing)
        filename = "config.yaml"
        content = "key: value"

        (self.hegemonikon_dir / filename).write_text(content, encoding='utf-8')

        loaded = self.manager.load(filename)
        # Depending on environment, it might parse or return string
        # We assert it's at least one of them
        if isinstance(loaded, dict):
            self.assertEqual(loaded, {"key": "value"})
        else:
            self.assertEqual(loaded, content)

if __name__ == '__main__':
    unittest.main()
