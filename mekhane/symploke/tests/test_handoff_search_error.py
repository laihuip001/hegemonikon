import sys
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from pathlib import Path

# Adjust path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mekhane.symploke.handoff_search import get_boot_handoffs, Document

class TestHandoffSearchError(unittest.TestCase):
    @patch("mekhane.symploke.handoff_search.load_handoffs")
    @patch("mekhane.symploke.handoff_search.CONVERSATION_INDEX_PATH")
    @patch("mekhane.symploke.handoff_search.HANDOFF_INDEX_PATH")
    @patch("mekhane.symploke.handoff_search.EmbeddingAdapter")
    def test_proactive_recall_error_handling(self, MockAdapter, MockHandoffPath, MockConvPath, mock_load_handoffs):
        # Setup mocks
        mock_doc = Document(id="test_doc", content="Some content with Keywords like Python and AI.", metadata={"primary_task": "Test Task", "timestamp": "2023-01-01"})
        mock_load_handoffs.return_value = [mock_doc]

        MockHandoffPath.exists.return_value = True
        MockConvPath.exists.return_value = True

        # Mock paths string representation
        str(MockHandoffPath).replace("Mock", "/path/to/handoffs.pkl")
        str(MockConvPath).replace("Mock", "/path/to/kairos.pkl")

        # Mock Adapter instance
        mock_adapter = MockAdapter.return_value

        # Define side effect for load to control search behavior
        def load_side_effect(path):
            if path == str(MockHandoffPath):
                # Success for handoff search
                mock_result = MagicMock()
                mock_result.id = "related_doc"
                mock_result.score = 0.9
                mock_result.metadata = {"idx": 0}
                mock_adapter.search.side_effect = None
                mock_adapter.search.return_value = [mock_result]
            elif path == str(MockConvPath):
                # Fail for conversation/proactive search
                mock_adapter.search.side_effect = Exception("Simulated Search Error")

        mock_adapter.load.side_effect = load_side_effect

        # Also need encode to return something iterable
        mock_adapter.encode.return_value = [[0.1, 0.2, 0.3]]

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Run function with detailed mode to trigger proactive recall
            get_boot_handoffs(mode="detailed")
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()

        # Verify conversation search error is printed (existing behavior)
        self.assertIn("Conversation search error: Simulated Search Error", output)

        # Verify proactive recall error is NOT printed (current bug)
        # We expect this assertion to PASS now (confirming the bug), and FAIL after we fix it.
        # But wait, usually we write the test to FAIL first.
        # So I should assert that the error IS printed, and expect the test to fail.

        self.assertIn("Proactive recall error: Simulated Search Error", output)

if __name__ == "__main__":
    unittest.main()
