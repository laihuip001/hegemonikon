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
    """Test suite for gnosis index."""
    # PURPOSE: Verify set up behaves correctly
    def setUp(self):
        """Verify set up behavior."""
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
        """Verify tear down behavior."""
        self.embedder_patcher.stop()
        shutil.rmtree(self.test_dir)

    # PURPOSE: load_primary_keys をテストする
    def test_load_primary_keys(self):
        # Create dummy papers
        """Verify load primary keys behavior."""
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


# PURPOSE: Test suite validating embedder dimension correctness
class TestEmbedderDimension(unittest.TestCase):
    """Embedder._dimension と _is_onnx_fallback の検証。"""

    # PURPOSE: Verify dimension property exists after init behaves correctly
    @patch("mekhane.anamnesis.index.Embedder._instances", {})
    def test_dimension_property_exists_after_init(self):
        """Embedder 初期化後、_dimension が正の整数であること。"""
        from mekhane.anamnesis.index import Embedder
        with patch.object(Embedder, '__init__', lambda self, **kw: None):
            e = object.__new__(Embedder)
            e._initialized = False
            e._dimension = 1024
            e._is_onnx_fallback = False
            self.assertEqual(e._dimension, 1024)
            self.assertFalse(e._is_onnx_fallback)

    # PURPOSE: Verify model dimensions map behaves correctly
    def test_model_dimensions_map(self):
        """_MODEL_DIMENSIONS に既知モデルが登録されていること。"""
        from mekhane.anamnesis.index import Embedder
        self.assertEqual(Embedder._MODEL_DIMENSIONS["BAAI/bge-m3"], 1024)
        self.assertEqual(Embedder._MODEL_DIMENSIONS["BAAI/bge-small-en-v1.5"], 384)


# PURPOSE: Test suite validating get vector dimension correctness
class TestGetVectorDimension(unittest.TestCase):
    """_get_vector_dimension() ヘルパーの検証。"""

    # PURPOSE: Verify extracts dimension from schema behaves correctly
    def test_extracts_dimension_from_schema(self):
        """fixed_size_list<item: float>[1024] 形式から次元を抽出。"""
        from mekhane.anamnesis.index import _get_vector_dimension
        mock_field = MagicMock()
        mock_field.name = "vector"
        mock_field.type = "fixed_size_list<item: float>[1024]"
        mock_table = MagicMock()
        mock_table.schema = [mock_field]
        self.assertEqual(_get_vector_dimension(mock_table), 1024)

    # PURPOSE: Verify returns none for no vector column behaves correctly
    def test_returns_none_for_no_vector_column(self):
        """vector カラムがない場合 None を返す。"""
        from mekhane.anamnesis.index import _get_vector_dimension
        mock_field = MagicMock()
        mock_field.name = "text"
        mock_table = MagicMock()
        mock_table.schema = [mock_field]
        self.assertIsNone(_get_vector_dimension(mock_table))


# PURPOSE: Test suite validating dimension mismatch guard correctness
class TestDimensionMismatchGuard(unittest.TestCase):
    """GnosisIndex.search() の次元不一致防御の検証。"""

    # PURPOSE: Verify set up behaves correctly
    def setUp(self):
        """Verify set up behavior."""
        self.test_dir = tempfile.mkdtemp()
        self.lance_dir = Path(self.test_dir) / "lancedb"

        self.embedder_patcher = patch("mekhane.anamnesis.index.Embedder")
        self.mock_embedder_class = self.embedder_patcher.start()
        self.mock_embedder_instance = self.mock_embedder_class.return_value
        # 384-dim embedder (ONNX fallback scenario)
        self.mock_embedder_instance.embed_batch.side_effect = lambda texts: [
            [0.1] * 384 for _ in texts
        ]
        self.mock_embedder_instance.embed.return_value = [0.1] * 384
        self.mock_embedder_instance._dimension = 384
        self.mock_embedder_instance._is_onnx_fallback = True
        self.mock_embedder_instance.model_name = "bge-small-onnx"

        self.index = GnosisIndex(lance_dir=self.lance_dir)
        self.index._get_embedder = lambda: self.mock_embedder_instance

    # PURPOSE: Verify tear down behaves correctly
    def tearDown(self):
        """Verify tear down behavior."""
        self.embedder_patcher.stop()
        shutil.rmtree(self.test_dir)

    # PURPOSE: Verify search returns empty on dimension mismatch behaves correctly
    def test_search_returns_empty_on_dimension_mismatch(self):
        """384-dim embedder で 1024-dim テーブルを検索 → 空リスト。"""
        # Create table with 1024-dim vectors to simulate bge-m3 index
        import lancedb
        db = lancedb.connect(str(self.lance_dir))
        db.create_table("knowledge", data=[{
            "primary_key": "test-001",
            "title": "Test Paper",
            "abstract": "Abstract",
            "source": "test",
            "source_id": "1",
            "vector": [0.1] * 1024,  # 1024-dim
        }])

        results = self.index.search("test query")
        self.assertEqual(results, [])

    # PURPOSE: Verify search succeeds on matching dimensions behaves correctly
    def test_search_succeeds_on_matching_dimensions(self):
        """384-dim embedder で 384-dim テーブルを検索 → 正常結果。"""
        papers = [Paper(
            id="test-001", source="test", source_id="1",
            title="Test Paper", abstract="Abstract",
        )]
        self.index.add_papers(papers, dedupe=False)

        results = self.index.search("test query")
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
