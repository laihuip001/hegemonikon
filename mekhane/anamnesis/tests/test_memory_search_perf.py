# PROOF: [L3/ユーティリティ] <- mekhane/anamnesis/tests/
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add project root to path so we can import mekhane
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

class TestMemorySearchPerformance(unittest.TestCase):

    def setUp(self):
        # We need to mock the modules BEFORE importing memory_search
        # because memory_search imports them at top level.

        # Mock lancedb_indexer
        self.mock_lancedb_indexer = MagicMock()
        self.mock_lancedb_indexer.search_sessions.return_value = [
            {
                "title": "Test Session",
                "filename": "test.md",
                "content_preview": "Preview content...",
            }
        ]
        sys.modules["mekhane.anamnesis.lancedb_indexer"] = self.mock_lancedb_indexer
        sys.modules["lancedb_indexer"] = self.mock_lancedb_indexer

        # Mock module_indexer
        self.mock_module_indexer = MagicMock()
        self.mock_module_indexer.search_modules.return_value = [
            {
                "title": "Test Module",
                "category": "hypervisor",
                "filename": "module.md",
                "content_preview": "Module content...",
            }
        ]
        sys.modules["mekhane.anamnesis.module_indexer"] = self.mock_module_indexer
        sys.modules["module_indexer"] = self.mock_module_indexer

        # Mock chat_history_kb dependencies to avoid import errors during dynamic import
        # We need to mock lancedb, onnxruntime, tokenizers, numpy
        sys.modules["lancedb"] = MagicMock()
        sys.modules["onnxruntime"] = MagicMock()
        sys.modules["tokenizers"] = MagicMock()
        sys.modules["numpy"] = MagicMock()

    def test_search_calls(self):
        # Import memory_search inside the test method to ensure mocks are applied
        # Force reload if already imported
        if "mekhane.anamnesis.memory_search" in sys.modules:
            del sys.modules["mekhane.anamnesis.memory_search"]

        from mekhane.anamnesis import memory_search

        # Mock the dynamically imported chat_history_kb
        mock_chat_kb = MagicMock()
        mock_chat_kb.search_chat_history.return_value = [
            {
                "session_id": "session_123",
                "artifact_type": "summary",
                "summary": "Chat summary...",
                "updated_at": "2023-01-01",
            }
        ]

        # memory_search.chat_history_kb might be None if import failed (due to paths)
        # So we manually inject the mock
        memory_search.chat_history_kb = mock_chat_kb

        # Test hybrid_search
        query = "test query"
        result = memory_search.hybrid_search(query)

        # Verify calls
        self.mock_lancedb_indexer.search_sessions.assert_called_with(query, limit=3)
        self.mock_module_indexer.search_modules.assert_called_with(query, limit=3)
        mock_chat_kb.search_chat_history.assert_called_with(query, n_results=3)

        # Verify output format
        self.assertIn("Test Session", result)
        self.assertIn("Test Module", result)
        # Session ID is truncated to 8 chars
        self.assertIn("session_", result)
        self.assertIn("Preview content...", result)
        self.assertIn("Chat summary...", result)

        print("\n[SUCCESS] Memory search verified with mocked calls.")

if __name__ == "__main__":
    unittest.main()
