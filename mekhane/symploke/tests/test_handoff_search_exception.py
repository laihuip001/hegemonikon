import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mekhane.symploke.handoff_search import get_boot_handoffs

class TestHandoffSearchException(unittest.TestCase):

    @patch('mekhane.symploke.handoff_search.load_handoffs')
    @patch('mekhane.symploke.handoff_search.extract_keywords')
    @patch('mekhane.symploke.handoff_search.CONVERSATION_INDEX_PATH')
    @patch('mekhane.symploke.handoff_search.EmbeddingAdapter')
    @patch('mekhane.symploke.handoff_search.search_handoffs')
    @patch('builtins.print')
    def test_proactive_recall_exception_handled(self, mock_print, MockSearch, MockAdapter, MockPath, MockExtract, MockLoad):
        """Test that ensures Proactive Recall exception is properly logged/printed."""

        # 1. Mock load_handoffs to return a dummy document
        mock_doc = MagicMock()
        mock_doc.id = "test-doc"
        mock_doc.content = "Test content"
        mock_doc.metadata = {"primary_task": "Test Task"}
        MockLoad.return_value = [mock_doc]

        # 2. Mock extract_keywords
        MockExtract.return_value = ["test", "keyword"]

        # 3. Mock CONVERSATION_INDEX_PATH.exists()
        MockPath.exists.return_value = True

        # 4. Mock EmbeddingAdapter to raise Exception on load
        mock_adapter_instance = MockAdapter.return_value
        mock_adapter_instance.load.side_effect = Exception("Simulated Failure")

        # 5. Mock search_handoffs
        MockSearch.return_value = []

        # Run function
        get_boot_handoffs(mode="detailed")

        # Check for specific error message for Proactive Recall
        found_proactive_error = False
        found_conversation_error = False

        for call_args in mock_print.call_args_list:
            args, _ = call_args
            if not args:
                continue
            msg = str(args[0])
            if "Conversation search error" in msg and "Simulated Failure" in msg:
                found_conversation_error = True
            if "Proactive recall error" in msg and "Simulated Failure" in msg:
                found_proactive_error = True

        # Expect both to be handled now
        self.assertTrue(found_conversation_error, "Existing conversation error handling should work")
        self.assertTrue(found_proactive_error, "Proactive recall exception should be printed now")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHandoffSearchException)
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
