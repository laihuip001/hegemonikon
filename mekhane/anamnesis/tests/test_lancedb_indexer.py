import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add root to path
sys.path.insert(0, str(Path(__file__).parents[3]))

from mekhane.anamnesis.lancedb_indexer import index_sessions, get_session_count, SessionDocument

def test_session_document_model():
    doc = SessionDocument(
        filename="test.md",
        title="Test",
        exported_at="2024-01-01",
        message_count=10,
        content="test content",
        content_preview="test"
    )
    assert doc.filename == "test.md"
    assert doc.content == "test content"

@patch("mekhane.anamnesis.lancedb_indexer.lancedb")
def test_index_sessions(mock_lancedb):
    # Mock setup
    mock_db = MagicMock()
    mock_lancedb.connect.return_value = mock_db
    mock_table = MagicMock()
    mock_db.create_table.return_value = mock_table
    mock_db.table_names.return_value = []

    # Mock sessions dir
    with patch("pathlib.Path.glob") as mock_glob, \
         patch("pathlib.Path.exists") as mock_exists, \
         patch("mekhane.anamnesis.lancedb_indexer.parse_session_file") as mock_parse:

        mock_exists.return_value = True
        mock_glob.return_value = [Path("test.md")]

        mock_doc = SessionDocument(
            filename="test.md",
            title="Test",
            exported_at="2024-01-01",
            message_count=10,
            content="a" * 100, # > 50 chars
            content_preview="test"
        )
        mock_parse.return_value = mock_doc

        db, count = index_sessions(Path("sessions"), Path("db"))

        assert count == 1
        mock_db.create_table.assert_called_once()

@patch("mekhane.anamnesis.lancedb_indexer.lancedb")
def test_get_session_count(mock_lancedb):
    mock_db = MagicMock()
    mock_lancedb.connect.return_value = mock_db
    mock_table = MagicMock()
    mock_db.open_table.return_value = mock_table

    # Mock table exists
    mock_db.table_names.return_value = ["sessions"]
    mock_table.count_rows.return_value = 5

    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        count = get_session_count(Path("db"))
        assert count == 5
