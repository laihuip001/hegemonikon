
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import logging
import sys
import re

# Adjust path to import extract_strings
sys.path.append(str(Path(__file__).resolve().parent.parent))

from extract_strings import extract_strings

class TestExtractStrings(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.test_dir.name) / "test.bin"

    def tearDown(self):
        self.test_dir.cleanup()

    def test_ascii_extraction(self):
        # Create a binary file with some ASCII strings
        # We need enough length because min_length defaults to 20
        content = b"\x00\x01" + b"Hello World This Is ASCII" + b"\x00\xff"
        with open(self.test_file, "wb") as f:
            f.write(content)

        # Min length is 20 by default
        strings = extract_strings(self.test_file, min_length=20)
        found_texts = [s[1] for s in strings if s[0] == "ascii"]
        self.assertIn("Hello World This Is ASCII", found_texts)

    @patch("re.finditer")
    def test_decode_error_handling(self, mock_finditer):
        # Mock file existence/open
        # But extract_strings opens the file. We just need it to exist.
        with open(self.test_file, "wb") as f:
            f.write(b"dummy")

        # Mock match object
        mock_match = MagicMock()
        mock_match.start.return_value = 42

        # Mock the return value of match.group() to be an object that raises on decode
        mock_bytes_like = MagicMock()
        mock_bytes_like.decode.side_effect = UnicodeDecodeError('ascii', b'', 0, 1, 'mock error')
        mock_match.group.return_value = mock_bytes_like

        mock_finditer.return_value = [mock_match]

        # We expect error logs.
        # The test will fail if no logs are captured (assertLogs behavior)
        # Or if we manually assert and find nothing.

        with self.assertLogs() as cm:
            extract_strings(self.test_file)

            # If we reach here, assertLogs might not have checked yet (it checks on exit).
            # But we can also check cm.output manually if we want to be specific about what was logged.
            self.assertTrue(len(cm.output) > 0, "No logs captured!")
            self.assertTrue(any("decoding ASCII match" in r for r in cm.output) or
                            any("Unexpected error" in r for r in cm.output) or
                            any("mock error" in r for r in cm.output),
                            f"Logs did not match expected pattern. Got: {cm.output}")

if __name__ == "__main__":
    unittest.main()
