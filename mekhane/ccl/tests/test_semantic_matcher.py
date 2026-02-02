import sys
import unittest
import logging
from unittest.mock import MagicMock, patch

# Mock dependencies before importing module under test
# This ensures that imports inside the module don't fail
# We need to ensure we don't overwrite if they exist, but for this test environment
# where they might be missing, we force mock them to control behavior.
# However, to be safe, we only mock if not present or just forcefully mock for this test module context.
# Since we import inside the test file, we can just patch sys.modules.

sys.modules["sentence_transformers"] = MagicMock()
sys.modules["numpy"] = MagicMock()

# Now we can safely import the module
from mekhane.ccl import semantic_matcher

class TestSemanticMacroMatcher(unittest.TestCase):
    def test_init_exception_handling(self):
        """Test that exception during initialization is logged and model is None."""

        # We need to mock SentenceTransformer constructor to raise exception
        # semantic_matcher.SentenceTransformer is the one we mocked in sys.modules
        mock_st_class = sys.modules["sentence_transformers"].SentenceTransformer
        mock_st_class.side_effect = Exception("Model load failed")

        # Also ensure HAS_EMBEDDINGS is True so it enters the block
        with patch('mekhane.ccl.semantic_matcher.HAS_EMBEDDINGS', True):
            # We expect an ERROR log.
            # Note: assertLogs captures logs from the specified logger.
            with self.assertLogs('mekhane.ccl.semantic_matcher', level='ERROR') as cm:
                matcher = semantic_matcher.SemanticMacroMatcher()

            # Check if error was logged
            self.assertTrue(any("Failed to initialize semantic matcher" in o for o in cm.output))
            # The exception message should likely be included
            # self.assertTrue(any("Model load failed" in o for o in cm.output))

            # Check state
            self.assertIsNone(matcher.model)
            self.assertFalse(matcher.is_available())
