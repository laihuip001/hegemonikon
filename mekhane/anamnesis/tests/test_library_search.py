
import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import lancedb

# Add repo root to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from mekhane.anamnesis.library_search import LibrarySearch
from mekhane.anamnesis.models.prompt_module import PromptModule

class TestLibrarySearch(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.lance_dir = Path(self.test_dir) / "data"
        self.lance_dir.mkdir(parents=True)

        # Create dummy data matching what index_library.py produces (activation_triggers as string)
        self.db = lancedb.connect(str(self.lance_dir))

        data = [
            {
                "id": "prompt_test_1",
                "name": "Test Prompt 1",
                "category": "test",
                "activation_triggers": "trigger1, foo",
                "hegemonikon_mapping": "/noe+*dia^",
                "essence": "Essence 1",
                "body": "Body 1",
                "filepath": "path/to/1",
                "origin": "test",
                "model_target": "universal",
                "vector": [0.1] * 384
            },
            {
                "id": "prompt_test_2",
                "name": "Test Prompt 2",
                "category": "test",
                "activation_triggers": "trigger2, bar",
                "hegemonikon_mapping": "/bou",
                "essence": "Essence 2",
                "body": "Body 2",
                "filepath": "path/to/2",
                "origin": "test",
                "model_target": "universal",
                "vector": [0.2] * 384
            }
        ]
        self.db.create_table("prompts", data=data)

        self.searcher = LibrarySearch(lance_dir=str(self.lance_dir))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_count(self):
        self.assertEqual(self.searcher.count(), 2)

    def test_get_module(self):
        module = self.searcher.get_module("prompt_test_1")
        self.assertIsNotNone(module)
        self.assertEqual(module.name, "Test Prompt 1")

        module = self.searcher.get_module("non_existent")
        self.assertIsNone(module)

    def test_search_by_mapping(self):
        results = self.searcher.search_by_mapping("/noe")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Test Prompt 1")

    def test_search_by_triggers(self):
        results = self.searcher.search_by_triggers("trigger1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Test Prompt 1")

        results = self.searcher.search_by_triggers("bar")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Test Prompt 2")

if __name__ == "__main__":
    unittest.main()
