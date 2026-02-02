import sys
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
import asyncio
from pathlib import Path

# Mock the imports that happen inside the function
mock_adapter_module = MagicMock()
sys.modules["mekhane.symploke.adapters.embedding_adapter"] = mock_adapter_module

# Now import the server
# We assume the test is run from a location where mekhane is importable
from mekhane.mcp import sophia_mcp_server

class TestSophiaMCP(unittest.TestCase):
    def test_date_parsing_error_logging(self):
        # Setup mock adapter
        mock_adapter = MagicMock()
        mock_adapter_module.EmbeddingAdapter.return_value = mock_adapter

        # Mock search results
        mock_result = MagicMock()
        mock_result.score = 0.9
        # metadata with invalid timestamp
        mock_result.metadata = {
            "timestamp": "INVALID-DATE",
            "primary_task": "Test Task",
            "file_path": "/path/to/file"
        }
        mock_adapter.search.return_value = [mock_result]
        mock_adapter.encode.return_value = [[0.1, 0.2]] # Dummy vector

        # Mock Path.exists to return True for Kairos index
        with patch("pathlib.Path.exists", return_value=True):
            # Capture stderr
            with patch("sys.stderr", new=StringIO()) as fake_stderr:
                # Call the tool
                # We need to run async function
                asyncio.run(sophia_mcp_server.call_tool("search", {
                    "query": "test",
                    "source": "kairos",
                    "recent_days": 7
                }))

                # Check stderr
                output = fake_stderr.getvalue()
                print(f"Captured stderr: {output}") # For debug

                # Assert that we logged the error
                self.assertIn("Error parsing date", output)
                self.assertIn("INVALID-DATE", output)

if __name__ == "__main__":
    unittest.main()
