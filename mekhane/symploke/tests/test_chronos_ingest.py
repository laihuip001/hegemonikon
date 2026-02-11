# PROOF: [L3/テスト] <- mekhane/symploke/tests/ 対象モジュールが存在→検証が必要→test_chronos_ingest が担う
"""
Tests for chronos_ingest.py
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mekhane.symploke.indices import Document

# PURPOSE: Tests for chronos_ingest.py
class TestChronosIngest:
    """Tests for chronos_ingest.py"""

    # PURPOSE: Test parsing of conversation logs
    def test_parse_conversation(self):
        """Test parsing of conversation logs"""
        from mekhane.symploke.chronos_ingest import parse_conversation

        # Create temp conversation file
        with tempfile.TemporaryDirectory() as tmpdir:
            new_path = Path(tmpdir) / "2026-01-31_conv_50_Test_Title.md"

            new_path.write_text("""# Test Title

## 🤖 Claude
Hello user.

## User
Hi.
""", encoding="utf-8")

            doc = parse_conversation(new_path)

            assert doc is not None
            assert doc.id == "conv-2026-01-31-50"
            assert doc.metadata["title"] == "Test Title"
            assert doc.metadata["conv_num"] == 50
            assert doc.metadata["msg_count"] == 1
            assert "Test Title" in doc.content


    # PURPOSE: Test chunking of conversation logs
    def test_parse_conversation_chunks(self):
        """Test chunking of conversation logs"""
        from mekhane.symploke.chronos_ingest import parse_conversation_chunks

        # Create temp conversation file with long content
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "2026-01-31_conv_50_Long_Conv.md"

            # Generate long content
            content = "# Long Conv\n\n"
            for i in range(10):
                content += f"## 🤖 Claude\nThis is message {i}.\n" + "A" * 500 + "\n\n"

            file_path.write_text(content, encoding="utf-8")

            # Use small chunk size to force split
            chunks = parse_conversation_chunks(file_path, chunk_size=1000)

            assert len(chunks) > 1
            for i, chunk in enumerate(chunks):
                assert chunk.metadata["chunk_idx"] == i
                assert chunk.metadata["type"] == "conversation_chunk"
                assert chunk.id.startswith("conv-2026-01-31-50-c")

    # PURPOSE: Test ingestion logic (mocked adapter)
    @patch("mekhane.symploke.adapters.embedding_adapter.EmbeddingAdapter")
    @patch("mekhane.symploke.chronos_ingest.ChronosIndex")
    def test_ingest_to_chronos(self, mock_index_cls, mock_adapter_cls):
        """Test ingestion logic (mocked adapter)"""
        from mekhane.symploke.chronos_ingest import ingest_to_chronos

        # Setup mocks
        mock_adapter = MagicMock()
        mock_adapter.encode.return_value = np.zeros((1, 384)) # Mock embedding
        mock_adapter_cls.return_value = mock_adapter

        mock_index = MagicMock()
        mock_index_cls.return_value = mock_index
        mock_index.ingest.return_value = 1

        # Create dummy doc
        doc = Document(id="test", content="test", metadata={})

        # Run ingest
        count = ingest_to_chronos([doc], save_path="test.pkl")

        assert count == 1
        mock_index.initialize.assert_called_once()
        mock_index.ingest.assert_called_once()
        mock_adapter.save.assert_called_once_with("test.pkl")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
