import sys
import unittest
from unittest.mock import MagicMock
import numpy as np
from pathlib import Path

# --- Mocks Setup (Copied from benchmark) ---

lancedb_mock = MagicMock()
sys.modules["lancedb"] = lancedb_mock

ort_mock = MagicMock()
sys.modules["onnxruntime"] = ort_mock

tokenizers_mock = MagicMock()
sys.modules["tokenizers"] = tokenizers_mock

class MockInferenceSession:
    def __init__(self, path):
        pass

    def run(self, output_names, input_feed):
        input_ids = input_feed["input_ids"]
        batch_size = input_ids.shape[0]
        seq_len = input_ids.shape[1]
        # Return constant to verify value propagation if needed, or random
        return [np.ones((batch_size, seq_len, 384)).astype(np.float32)]

ort_mock.InferenceSession = MockInferenceSession

class MockTokenizer:
    def enable_truncation(self, max_length): pass
    def enable_padding(self, length): pass
    def encode(self, text):
        m = MagicMock()
        m.ids = [1] * 10
        m.attention_mask = [1] * 10
        return m
    def encode_batch(self, texts):
        batch = []
        for _ in texts:
            m = MagicMock()
            m.ids = [1] * 10
            m.attention_mask = [1] * 10
            batch.append(m)
        return batch
    @classmethod
    def from_file(cls, path): return cls()

tokenizers_mock.Tokenizer = MockTokenizer

# Mock Path.exists
original_exists = Path.exists
def mock_exists(self):
    if "model.onnx" in str(self) or "tokenizer.json" in str(self): return True
    return original_exists(self)
Path.exists = mock_exists

# --- Import ---
from mekhane.anamnesis.index import GnosisIndex, Paper, Embedder

class TestGnosisIndex(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        lancedb_mock.reset_mock()
        self.mock_db = MagicMock()
        self.mock_table = MagicMock()
        self.mock_db.table_names.return_value = ["papers"]
        self.mock_db.open_table.return_value = self.mock_table
        lancedb_mock.connect.return_value = self.mock_db

        self.index = GnosisIndex()

    def test_embed_batch_structure(self):
        embedder = Embedder()
        texts = ["hello", "world", "test"]
        vectors = embedder.embed_batch(texts)
        self.assertEqual(len(vectors), 3)
        self.assertEqual(len(vectors[0]), 384) # BGE-small dim
        # Since we return ones, pooled is ones, norm is sqrt(384).
        # normalized = 1 / sqrt(384).
        # Just check it's a list of floats
        self.assertIsInstance(vectors[0][0], float)

    def test_add_papers_batching(self):
        papers = []
        for i in range(70): # 32 + 32 + 6
            p = Paper(
                id=f"t_{i}", source="t", source_id=str(i),
                title=f"Title {i}", abstract="Abs"
            )
            papers.append(p)

        count = self.index.add_papers(papers, dedupe=False)
        self.assertEqual(count, 70)

        # Verify lancedb add was called
        # batch size is 32, so calls should happen.
        # But wait, GnosisIndex collects `data` list and calls `table.add(data)` ONCE at the end.
        self.mock_table.add.assert_called_once()
        args, _ = self.mock_table.add.call_args
        added_data = args[0]
        self.assertEqual(len(added_data), 70)
        self.assertIn("vector", added_data[0])

    def test_add_papers_empty(self):
        count = self.index.add_papers([], dedupe=False)
        self.assertEqual(count, 0)
        self.mock_table.add.assert_not_called()

if __name__ == "__main__":
    unittest.main()
