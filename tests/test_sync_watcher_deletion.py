import unittest
import tempfile
import shutil
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import lancedb
except ImportError:
    lancedb = None

try:
    import pandas
except ImportError:
    pandas = None

# Patch dependencies before importing modules that use them
class MockEmbedder:
    def __init__(self, *args, **kwargs):
        self._dimension = 384
        self.model_name = "mock-bge-small"
        self._is_onnx_fallback = False
        self._initialized = True # Prevent re-init logic if any

    def embed(self, text):
        return [0.1] * 384

    def embed_batch(self, texts):
        return [[0.1] * 384 for _ in texts]

# Apply patches
patch_embedder = patch("mekhane.anamnesis.index.Embedder", MockEmbedder)
patch_embedder.start()

# Now import modules
from mekhane.anamnesis.index import GnosisIndex, Paper
from mekhane.pks.sync_watcher import SyncWatcher, FileChange

@unittest.skipIf(lancedb is None or pandas is None, "lancedb or pandas not installed")
class TestSyncWatcherDeletion(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.lance_dir = Path(self.test_dir) / "lancedb"
        self.watch_dir = Path(self.test_dir) / "watch"
        self.watch_dir.mkdir()

        # Patch LANCE_DIR in index module
        self.patcher_lance = patch("mekhane.anamnesis.index.LANCE_DIR", self.lance_dir)
        self.patcher_lance.start()

        # Initialize index
        self.index = GnosisIndex()

    def tearDown(self):
        self.patcher_lance.stop()
        shutil.rmtree(self.test_dir)

    def test_deletion_logic(self):
        # 1. Add a dummy document directly to index
        doc_path = self.watch_dir / "test_doc.md"
        doc_path.write_text("dummy content")

        # Create Paper object mimicking what we expect to store
        paper = Paper(
            id="gnosis_local_test",
            source=str(doc_path),
            source_id="test_doc",
            title="test_doc",
            abstract="dummy content"
        )
        self.index.add_papers([paper])

        # Verify it exists
        results = self.index.search("dummy")
        self.assertTrue(len(results) > 0, "Document should be indexed initially")
        self.assertEqual(results[0]['source'], str(doc_path))

        # 2. Simulate deletion event in SyncWatcher
        watcher = SyncWatcher(watch_dirs=[self.watch_dir])
        change = FileChange(path=doc_path, change_type="deleted")

        # Capture stdout to check for errors/logs
        import io
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            watcher.ingest_changes([change])
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        # print(f"DEBUG OUTPUT (deletion): {output}")

        # 3. Assert deletion
        results_after = self.index.search("dummy")
        self.assertEqual(len(results_after), 0, "Document should be deleted from index")

    def test_addition_logic(self):
        # 1. Simulate addition event
        doc_path = self.watch_dir / "new_doc.md"
        doc_path.write_text("new content for addition test")

        watcher = SyncWatcher(watch_dirs=[self.watch_dir])
        change = FileChange(path=doc_path, change_type="added")

        # Capture stdout
        import io
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            watcher.ingest_changes([change])
        finally:
            sys.stdout = sys.__stdout__

        # 2. Assert addition
        results = self.index.search("addition")
        self.assertEqual(len(results), 1, "Document should be added to index")

if __name__ == "__main__":
    unittest.main()
