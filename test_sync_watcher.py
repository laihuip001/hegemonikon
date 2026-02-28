from mekhane.anamnesis.index import GnosisIndex
from mekhane.pks.sync_watcher import SyncWatcher, FileChange
from pathlib import Path
import os
import shutil

LANCE_DIR = Path("test_lance")
if LANCE_DIR.exists():
    shutil.rmtree(LANCE_DIR)

# Mock GnosisIndex in index
index = GnosisIndex(lance_dir=LANCE_DIR)
print("Index initialized")

watcher = SyncWatcher([Path('.')])

from unittest.mock import patch
import lancedb

def mock_open_table(name):
    class MockTable:
        def delete(self, condition):
            print(f"Delete called with condition: {condition}")
    return MockTable()

with patch('mekhane.anamnesis.index.GnosisIndex') as mock_index_class:
    mock_instance = mock_index_class.return_value
    mock_instance._table_exists.return_value = True
    mock_instance.TABLE_NAME = "knowledge"
    mock_instance.db.open_table = mock_open_table

    watcher.ingest_changes([
        FileChange(path=Path("some/test/file.md"), change_type="deleted")
    ])

print("Test complete.")
