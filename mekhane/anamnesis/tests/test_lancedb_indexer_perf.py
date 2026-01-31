
import pytest
import lancedb
from pathlib import Path
from unittest.mock import patch
from mekhane.anamnesis import lancedb_indexer

@pytest.fixture
def setup_env(tmp_path):
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()

    db_path = tmp_path / "lancedb"

    # Create dummy session files
    for i in range(5):
        content = f"""# Session {i}
**Exported**: 2023-01-0{i+1}T12:00:00
**Messages**: 10
---
user: hello {i}
model: hi {i}
"""
        # Ensure content length > 50 chars for the filter
        content += "A" * 60

        (sessions_dir / f"session_{i}.md").write_text(content, encoding="utf-8")

    return sessions_dir, db_path

def test_index_sessions(setup_env):
    sessions_dir, db_path = setup_env

    with patch("mekhane.anamnesis.lancedb_indexer.SESSIONS_DIR", sessions_dir), \
         patch("mekhane.anamnesis.lancedb_indexer.DB_PATH", db_path):

        # Run indexer
        db, table = lancedb_indexer.index_sessions()

        # Verify
        assert table is not None, "Table creation failed"
        assert table.name == "sessions"
        assert len(table) == 5

        # Search
        results = table.search("hello", query_type="fts").limit(5).to_list()
        assert len(results) > 0
