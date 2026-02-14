
import unittest
import tempfile
import os
import shutil
from pathlib import Path
from mekhane.anamnesis.lancedb_indexer import parse_session_file, SessionDocument

class TestLanceDBIndexerOpt(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test_session.md"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_session_file_basic(self):
        content = """# My Session
**Exported**: 2023-10-27T12:00:00
**Messages**: 42
---
## 👤 User
Hello

## 🤖 Claude
Hi there!
"""
        self.test_file.write_text(content, encoding="utf-8")

        doc = parse_session_file(self.test_file)
        self.assertIsNotNone(doc)
        self.assertEqual(doc.title, "My Session")
        self.assertEqual(doc.exported_at, "2023-10-27T12:00:00")
        self.assertEqual(doc.message_count, 42)
        self.assertIn("Hello", doc.content)
        self.assertIn("Hi there!", doc.content)
        self.assertNotIn("## 👤", doc.content)
        self.assertNotIn("## 🤖", doc.content)
        self.assertNotIn("---", doc.content)

    def test_parse_session_file_noise_removal(self):
        content = """# Noise Test
---
## 🤖 Claude
Here is some CSS:
/* Comment */
@media (min-width: 600px) { body { color: red; } }
.markdown-alert { color: blue; }
Thought for 5s
Actual Content
"""
        self.test_file.write_text(content, encoding="utf-8")

        doc = parse_session_file(self.test_file)
        self.assertIsNotNone(doc)
        self.assertIn("Actual Content", doc.content)
        self.assertNotIn("/* Comment */", doc.content)
        self.assertNotIn("@media", doc.content)
        self.assertNotIn(".markdown-alert", doc.content)
        self.assertNotIn("Thought for 5s", doc.content)

    def test_parse_session_file_large_body(self):
        # Create a large body to test truncation and performance logic (correctness only here)
        body = "A" * 20000
        content = f"""# Large Session
---
{body}
"""
        self.test_file.write_text(content, encoding="utf-8")

        doc = parse_session_file(self.test_file)
        self.assertIsNotNone(doc)
        self.assertEqual(len(doc.content), 10000)
        self.assertTrue(doc.content.startswith("A" * 100))

if __name__ == "__main__":
    unittest.main()
