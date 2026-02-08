# PROOF: [L3/テスト] <- mekhane/anamnesis/tests/ 対象モジュールが存在→その検証が必要→test_index が担う
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os
import sys
from pathlib import Path

# Add repo root to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from mekhane.anamnesis.index import GnosisIndex
from mekhane.anamnesis.models.paper import Paper


# PURPOSE: Test gnosis index の実装
class TestGnosisIndex(unittest.TestCase):
    # PURPOSE: setUp をセットアップする
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.lance_dir = Path(self.test_dir) / "lancedb"

        # Mock Embedder to avoid loading models
        self.embedder_patcher = patch("mekhane.anamnesis.index.Embedder")
        self.mock_embedder_class = self.embedder_patcher.start()
        self.mock_embedder_instance = self.mock_embedder_class.return_value
        # Mock embed_batch to return one vector per input text
        self.mock_embedder_instance.embed_batch.side_effect = lambda texts: [
            [0.1] * 384 for _ in texts
        ]
        self.mock_embedder_instance.embed.return_value = [0.1] * 384

        self.index = GnosisIndex(lance_dir=self.lance_dir)
        # Override _get_embedder to always return our mock
        self.index._get_embedder = lambda: self.mock_embedder_instance

    # PURPOSE: tearDown の処理
    def tearDown(self):
        self.embedder_patcher.stop()
        shutil.rmtree(self.test_dir)

    # PURPOSE: load_primary_keys をテストする
    def test_load_primary_keys(self):
        # Create dummy papers
        papers = []
        for i in range(15):  # 15 to exceed default limit if it was 10
            p = Paper(
                id=f"id_{i}",
                source="test",
                source_id=str(i),
                title=f"Title {i}",
                abstract="Abstract",
            )
            papers.append(p)

        # Add papers (this will create the table and add data)
        self.index.add_papers(papers, dedupe=False)

        # Verify papers are in DB
        table = self.index.db.open_table(self.index.TABLE_NAME)
        self.assertEqual(len(table.to_pandas()), 15)

        # Clear cache to force reload
        self.index._primary_key_cache = set()

        # Call _load_primary_keys
        self.index._load_primary_keys()

        # Verify cache
        expected_keys = {p.primary_key for p in papers}
        self.assertEqual(self.index._primary_key_cache, expected_keys)
        self.assertEqual(len(self.index._primary_key_cache), 15)


if __name__ == "__main__":
    unittest.main()
