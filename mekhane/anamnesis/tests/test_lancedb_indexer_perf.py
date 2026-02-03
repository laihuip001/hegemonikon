
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import lancedb
from mekhane.anamnesis.lancedb_indexer import index_sessions, TABLE_NAME

@pytest.fixture
def temp_env():
    # Create temporary directories for sessions and db
    temp_dir = tempfile.mkdtemp()
    sessions_dir = Path(temp_dir) / "sessions"
    sessions_dir.mkdir()
    db_dir = Path(temp_dir) / "lancedb"
    db_dir.mkdir()

    yield sessions_dir, db_dir

    # Cleanup
    shutil.rmtree(temp_dir)

def create_dummy_session(directory, index):
    content = f"""# Session {index}
**Exported** 2023-10-27T10:00:00
**Messages** 10

---

## 🤖 Bot
Hello!

## 👤 User
Hi there! This is a test message for session {index}.
"""
    file_path = directory / f"session_{index}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

def test_index_sessions_performance(temp_env):
    sessions_dir, db_path = temp_env

    # Create a reasonable number of dummy files
    num_files = 25  # Enough to test batching if batch size is small, or just general flow
    for i in range(num_files):
        create_dummy_session(sessions_dir, i)

    # Patch the global variables in the module
    with patch("mekhane.anamnesis.lancedb_indexer.SESSIONS_DIR", sessions_dir), \
         patch("mekhane.anamnesis.lancedb_indexer.DB_PATH", db_path):

        # Run the indexer
        db, table = index_sessions()

        # Verify
        assert table is not None
        assert table.count_rows() == num_files

        # Verify content
        results = table.search("test message", query_type="fts").limit(10).to_list()
        assert len(results) > 0
        assert "test message" in results[0]["content"]
