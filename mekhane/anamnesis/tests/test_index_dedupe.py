import unittest
import shutil
import tempfile
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure we can import mekhane
# Assuming running from repo root
sys.path.append(str(Path.cwd()))

from mekhane.anamnesis.index import GnosisIndex
from mekhane.anamnesis.models.paper import Paper

class TestGnosisIndexDedupe(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.index = GnosisIndex(lance_dir=self.test_dir)

        # Mock embedder to avoid loading models
        self.mock_embedder = MagicMock()
        # Mocking embed to return a list of floats (vector)
        # Using 384 dimensions as used in benchmark
        self.mock_embedder.embed.return_value = [0.1] * 384
        self.index.embedder = self.mock_embedder

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_deduplication(self):
        # Create a paper
        paper1 = Paper(
            id="test_1",
            source="test",
            source_id="1",
            title="Test Paper 1",
            abstract="Abstract 1"
        )

        # Add paper
        print("Adding paper 1...")
        count = self.index.add_papers([paper1])
        self.assertEqual(count, 1)

        # Verify it's in DB
        table = self.index.db.open_table(self.index.TABLE_NAME)
        self.assertEqual(len(table.to_pandas()), 1)

        # Verify primary key cache was updated
        self.assertIn(paper1.primary_key, self.index._primary_key_cache)

        # Create another index instance pointing to same DB (simulating restart)
        print("Creating index 2...")
        index2 = GnosisIndex(lance_dir=self.test_dir)
        index2.embedder = self.mock_embedder

        # Load primary keys (this triggers the code we want to optimize)
        print("Loading primary keys in index 2...")
        index2._load_primary_keys()
        self.assertIn(paper1.primary_key, index2._primary_key_cache)

        # Try adding same paper again
        print("Adding paper 1 again to index 2...")
        count = index2.add_papers([paper1])
        self.assertEqual(count, 0)

        # Add a new paper
        paper2 = Paper(
            id="test_2",
            source="test",
            source_id="2",
            title="Test Paper 2",
            abstract="Abstract 2"
        )
        print("Adding paper 2 to index 2...")
        count = index2.add_papers([paper2])
        self.assertEqual(count, 1)

        # Verify total
        table = self.index.db.open_table(self.index.TABLE_NAME)
        self.assertEqual(len(table.to_pandas()), 2)
        print("Test finished successfully.")

if __name__ == '__main__':
    unittest.main()
