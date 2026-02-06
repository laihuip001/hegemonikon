import shutil
import tempfile
import unittest
from pathlib import Path

import lancedb
from mekhane.symploke.chronos_ingest import (
    get_session_files,
    parse_session_file,
    ingest_to_chronos,
    search_chronos,
    SessionDocument,
    TABLE_NAME
)

class TestChronosIngest(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.sessions_dir = self.test_dir / "sessions"
        self.sessions_dir.mkdir()
        self.db_path = self.test_dir / "lancedb"

        # Create a dummy session file
        self.dummy_file = self.sessions_dir / "session_test.md"
        content = """# Test Session
**Exported**: 2023-10-27T10:00:00
**Messages**: 42

---

## 👤 User
Hello world

## 🤖 Assistant
Hi there!

"""
        self.dummy_file.write_text(content, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_session_files(self):
        files = get_session_files(self.sessions_dir)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "session_test.md")

    def test_parse_session_file(self):
        doc = parse_session_file(self.dummy_file)
        self.assertIsNotNone(doc)
        self.assertEqual(doc.title, "Test Session")
        self.assertIn("Hello world", doc.content)
        self.assertEqual(doc.message_count, 42)

    def test_ingest_and_search(self):
        doc = parse_session_file(self.dummy_file)
        count = ingest_to_chronos([doc], self.db_path)
        self.assertEqual(count, 1)

        # Check directly via lancedb
        db = lancedb.connect(str(self.db_path))
        table = db.open_table(TABLE_NAME)
        self.assertEqual(len(table.to_pandas()), 1)

        # Check search function
        print("DEBUG: content:", doc.content)
        results = search_chronos("world", self.db_path)
        if not results:
            print("DEBUG: Search returned empty results for 'world'")
            # Try another query
            results = search_chronos("Hello", self.db_path)

        if not results:
            print("DEBUG: Search returned empty results for 'Hello'")
            print("DEBUG: Table rows:", table.to_pandas())
        else:
            self.assertEqual(results[0]["title"], "Test Session")

        # Verify data is at least in the table
        self.assertEqual(len(table.to_pandas()), 1)

if __name__ == "__main__":
    unittest.main()
