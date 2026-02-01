# PROOF: [L3/テスト] 対象モジュールが存在→その検証が必要→test_night_review が担う

import unittest
import tempfile
import shutil
import json
import os
import sys
from pathlib import Path
from datetime import date, datetime
from unittest.mock import patch, MagicMock

# Ensure the module can be imported
sys.path.insert(0, os.path.abspath("."))

from mekhane.anamnesis import night_review


class TestNightReview(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.brain_dir = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_session(self, session_id, files_data, is_hidden=False):
        dir_name = session_id if not is_hidden else f"_{session_id}"
        session_path = self.brain_dir / dir_name
        session_path.mkdir()

        for i, data in enumerate(files_data):
            if len(data) == 3:
                filename, content, meta = data
            else:
                filename = f"file_{i}.md"
                content, meta = data

            md_path = session_path / filename
            meta_path = session_path / f"{filename}.metadata.json"

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)

            if meta:
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f)
        return session_path

    def test_get_sessions_basic(self):
        files = [
            (
                "plan.md",
                "# Title 1\nContent",
                {"artifactType": "test", "summary": "sum", "updatedAt": "2023-01-01T12:00:00Z"},
            ),
        ]
        self.create_session("session_1", files)

        with patch("mekhane.anamnesis.night_review.BRAIN_DIR", self.brain_dir):
            sessions = night_review.get_sessions()

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].session_id, "session_1")
        self.assertEqual(sessions[0].title, "Title 1")
        self.assertEqual(len(sessions[0].artifacts), 1)

    def test_get_sessions_skip_hidden(self):
        files = [("C", {"updatedAt": "2023-01-01T12:00:00Z"})]
        self.create_session("session_hidden", files, is_hidden=True)

        with patch("mekhane.anamnesis.night_review.BRAIN_DIR", self.brain_dir):
            sessions = night_review.get_sessions()

        self.assertEqual(len(sessions), 0)

    def test_get_sessions_missing_metadata(self):
        # File without metadata should be skipped, but if session has other valid files it might be included?
        # The code says: "if not meta_file.exists(): continue" inside the loop.
        # If no artifacts, "if not artifacts: continue" -> session skipped.

        files = [("Content", None)]  # None means no metadata file created
        self.create_session("session_no_meta", files)

        with patch("mekhane.anamnesis.night_review.BRAIN_DIR", self.brain_dir):
            sessions = night_review.get_sessions()

        self.assertEqual(len(sessions), 0)

    def test_get_sessions_date_filter(self):
        # Session 1: 2023-10-27
        files1 = [("C1", {"updatedAt": "2023-10-27T10:00:00Z"})]
        self.create_session("s1", files1)

        # Session 2: 2023-10-28
        files2 = [("C2", {"updatedAt": "2023-10-28T10:00:00Z"})]
        self.create_session("s2", files2)

        target_date = date(2023, 10, 27)

        with patch("mekhane.anamnesis.night_review.BRAIN_DIR", self.brain_dir):
            sessions = night_review.get_sessions(target_date=target_date)

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].session_id, "s1")

    def test_get_sessions_sorting(self):
        # s1: old
        files1 = [("C1", {"updatedAt": "2023-01-01T10:00:00Z"})]
        self.create_session("s1", files1)

        # s2: new
        files2 = [("C2", {"updatedAt": "2023-02-01T10:00:00Z"})]
        self.create_session("s2", files2)

        with patch("mekhane.anamnesis.night_review.BRAIN_DIR", self.brain_dir):
            sessions = night_review.get_sessions()

        self.assertEqual(len(sessions), 2)
        # Should be sorted by modified_at descending (newest first)
        self.assertEqual(sessions[0].session_id, "s2")
        self.assertEqual(sessions[1].session_id, "s1")


if __name__ == "__main__":
    unittest.main()
