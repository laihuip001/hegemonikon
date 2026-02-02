# PROOF: [L3/テスト] <- mekhane/symploke/tests/ 対象モジュールが存在→検証が必要→test_chronos_ingest が担う
"""
Tests for chronos_ingest.py
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

class TestChronosIngest:
    """Tests for chronos_ingest.py"""

    def test_parse_conversation_messages(self):
        """Test parsing of conversation logs into messages"""
        from mekhane.symploke.chronos_ingest import parse_conversation_messages

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""# Test Session

- **ID**: `test-id-123`
- **Date**: 2023-10-27

---

## 👤 User

Message 1

## 🤖 Claude

Message 2
""")
            f.flush()
            temp_path = Path(f.name)

        try:
            docs = parse_conversation_messages(temp_path)

            assert len(docs) == 2

            # Check Message 1
            assert docs[0].content == "Message 1"
            assert docs[0].metadata["role"] == "user"
            assert docs[0].metadata["session_id"] == "test-id-123"
            assert "content" in docs[0].metadata

            # Check Message 2
            assert docs[1].content == "Message 2"
            assert docs[1].metadata["role"] == "assistant"

        finally:
            temp_path.unlink()

    def test_parse_conversation_messages_filename_metadata(self):
        """Test parsing metadata from filename"""
        from mekhane.symploke.chronos_ingest import parse_conversation_messages

        with tempfile.TemporaryDirectory() as tmpdir:
            # 2024-02-02_conv-456_Test_Title.md
            filename = "2024-02-02_conv-456_Test_Title.md"
            file_path = Path(tmpdir) / filename

            file_path.write_text("""
## 👤 User

Hello
""", encoding="utf-8")

            docs = parse_conversation_messages(file_path)

            assert len(docs) == 1
            assert docs[0].metadata["session_id"] == "conv-456"
            assert docs[0].metadata["title"] == "Test Title"
            # Timestamp should be based on 2024-02-02
            assert docs[0].metadata["timestamp"].startswith("2024-02-02")
