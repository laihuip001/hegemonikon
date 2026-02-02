
import unittest
from pathlib import Path
import sys
import os

# Ensure we can import doc_maintenance
sys.path.append(os.path.dirname(__file__))

import doc_maintenance
from doc_maintenance import is_safe_path

class MockPathWithoutIsRelative:
    """Mock that mimics Path but lacks is_relative_to method."""
    def __init__(self, path):
        self.path = str(path)

    def resolve(self):
        return self

    def relative_to(self, other):
        other_str = str(other)
        if self.path.startswith(other_str):
            return self.path[len(other_str):]
        raise ValueError(f"{self.path} does not start with {other_str}")

    def __str__(self):
        return self.path

class TestDocMaintenance(unittest.TestCase):
    def setUp(self):
        self.root = Path("/home/user/repo")
        self.safe = self.root / "safe.txt"
        self.unsafe = Path("/home/user/other/unsafe.txt")
        self.unsafe_nested = Path("/etc/passwd")

    def test_is_safe_path_valid(self):
        """Test safe paths."""
        self.assertTrue(is_safe_path(self.safe, self.root))

    def test_is_safe_path_invalid(self):
        """Test unsafe paths."""
        self.assertFalse(is_safe_path(self.unsafe, self.root))
        self.assertFalse(is_safe_path(self.unsafe_nested, self.root))

    def test_fallback_logic(self):
        """Test the fallback logic where is_relative_to is missing."""
        # This test verifies that if is_relative_to is missing, we fall back to relative_to
        # and handle ValueError correctly.

        # Safe case with mock
        mock_safe = MockPathWithoutIsRelative(str(self.safe))
        # Note: We need to make sure base_dir matching works string-wise in our mock
        # verify our mock works as expected
        try:
            mock_safe.relative_to(self.root)
        except ValueError:
            self.fail("Mock failed basic relative_to check")

        # Since doc_maintenance.is_safe_path uses hasattr to check for is_relative_to,
        # our object failing that check triggers the try-except block.

        # Logic in is_safe_path:
        # if hasattr(target_path, "is_relative_to"): ...
        # else: try target_path.relative_to(...)

        # Test safe path via fallback
        self.assertTrue(is_safe_path(mock_safe, self.root), "Fallback logic failed for safe path")

        # Test unsafe path via fallback
        mock_unsafe = MockPathWithoutIsRelative(str(self.unsafe))
        # This should raise ValueError inside is_safe_path and return False (after falling through to step 3 and failing there too)
        self.assertFalse(is_safe_path(mock_unsafe, self.root), "Fallback logic failed for unsafe path")

    def test_case_insensitive_fallback(self):
        """Test the windows-specific case insensitive check."""
        # Using mixed case paths
        # Note: Path resolution on Linux won't handle case folding unless the FS does,
        # but the string comparison logic in step 3 should handle it.

        # We manually construct paths that differ in case but are "same" string-wise
        # mocking resolve() behavior might be needed if the OS is case-sensitive

        # For this test, we rely on the implementation of step 3 which converts to string and lowercases.
        # We need step 1 and 2 to fail.

        target = Path(str(self.root) + "/CaseMismatch.txt")
        # In a real case-sensitive FS, target is safe if it exists or is inside root.
        # But if we want to trigger step 3, we need step 1 & 2 to fail or be skipped?
        # Actually step 1 & 2 will pass for simple case mismatch on Linux if the path logic thinks it's relative.
        # Path("/A/B").is_relative_to("/A") is True regardless of case on Linux usually?
        # No, "/A/b".is_relative_to("/A") is True.

        # Wait, if step 1 & 2 pass, step 3 is skipped.
        # To test step 3, we need a case where relative_to FAILS but string check PASSES.
        # This happens on Windows if we have "C:\Foo" and "c:\foo".
        # On Linux, Path("C:\Foo").relative_to("c:\foo") raises ValueError.

        base = Path("/home/user/REPO")
        target = Path("/home/user/repo/file.txt")

        # On Linux:
        # target.relative_to(base) -> ValueError (case mismatch)

        # So this should trigger step 3.
        self.assertTrue(is_safe_path(target, base))

if __name__ == "__main__":
    unittest.main()
