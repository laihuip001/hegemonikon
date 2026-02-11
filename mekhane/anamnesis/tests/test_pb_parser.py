# PROOF: [L3/Test] <- mekhane/anamnesis/pb_parser.py P3→信頼性確保→回帰テスト
import unittest
import sys
import os
from pathlib import Path

# Add project root to path
# Assuming this test is in mekhane/anamnesis/tests/
# We need to go up 3 levels: tests -> anamnesis -> mekhane -> root
sys.path.insert(0, str(Path(__file__).parents[3]))

from mekhane.anamnesis.pb_parser import extract_text_from_pb

class TestPbParser(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("test_extract.pb")

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def create_pb_file(self, content):
        with open(self.test_file, "wb") as f:
            f.write(content)

    def test_extract_text_utf8(self):
        # Field 1: String "Hello World" (valid, 11 chars)
        # Key = (1 << 3) | 2 = 0x0A
        # Length = 11 (0x0B)
        # Value = "Hello World"

        # Field 2: Invalid UTF-8 bytes, length > 10
        # Value = b"This is invalid \xff\xff\xff" (length 19)
        invalid_bytes = b"This is invalid \xff\xff\xff"

        # Field 3: String "Goodbye World" (valid, 13 chars)
        # Value = "Goodbye World"

        data = bytearray()

        # Field 1
        data.append(0x0A)
        data.append(11)
        data.extend(b"Hello World")

        # Field 2 (Invalid UTF-8)
        data.append(0x0A)
        data.append(len(invalid_bytes))
        data.extend(invalid_bytes)

        # Field 3
        data.append(0x0A)
        data.append(13)
        data.extend(b"Goodbye World")

        self.create_pb_file(data)

        texts = extract_text_from_pb(self.test_file)

        # We expect "Hello World" and "Goodbye World"
        self.assertIn("Hello World", texts)
        self.assertIn("Goodbye World", texts)

        # The invalid one should be skipped silently (caught by exception handler)
        self.assertEqual(len(texts), 2)

if __name__ == "__main__":
    unittest.main()
