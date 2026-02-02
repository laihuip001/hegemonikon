
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib.util
from datetime import datetime

# Load the module dynamically due to dashes in filename
file_path = "mekhane/peira/scripts/chat-history-kb.py"
module_name = "chat_history_kb"
spec = importlib.util.spec_from_file_location(module_name, file_path)
chat_kb = importlib.util.module_from_spec(spec)
sys.modules[module_name] = chat_kb
spec.loader.exec_module(chat_kb)

class TestDateParsing(unittest.TestCase):
    @patch('builtins.print')
    def test_invalid_date_parsing(self, mock_print):
        # Mock dependencies
        with patch.object(chat_kb, 'check_dependencies', return_value=True), \
             patch.object(chat_kb, 'load_sync_state', return_value=datetime(2023, 1, 1)), \
             patch.object(chat_kb, 'Embedder') as MockEmbedder, \
             patch.object(chat_kb, 'get_sessions') as mock_get_sessions, \
             patch.object(chat_kb, 'save_sync_state'), \
             patch.dict(sys.modules, {'lancedb': MagicMock()}):

            # Setup mock data
            mock_session = {
                "session_id": "test_session_123",
                "artifacts": [
                    {
                        "session_id": "test_session_123",
                        "artifact_type": "ARTIFACT_TYPE_TEST",
                        "updated_at": "invalid-date-format",
                        "summary": "Test Summary",
                        "content": "Test Content"
                    }
                ]
            }
            mock_get_sessions.return_value = [mock_session]

            # Mock DB connection
            mock_db = MagicMock()
            sys.modules['lancedb'].connect.return_value = mock_db

            # Run build_index with incremental=True to trigger the date check
            chat_kb.build_index(incremental=True, report_mode=False)

            mock_embedder_instance = MockEmbedder.return_value

            # Check for warning message in print calls
            warning_found = False
            for call in mock_print.call_args_list:
                args, _ = call
                if args and "Skipping artifact" in str(args[0]) and "invalid date" in str(args[0]):
                    warning_found = True
                    break

            # Expectations for the FIX:
            # 1. Warning should be printed
            if not warning_found:
                self.fail("Warning message was not printed.")

            # 2. Embedder should NOT be called for the skipped artifact
            if mock_embedder_instance.embed.called:
                self.fail("Embedder was called, artifact was not skipped.")

if __name__ == '__main__':
    unittest.main()
