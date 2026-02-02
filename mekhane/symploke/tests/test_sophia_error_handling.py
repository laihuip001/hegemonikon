import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import io
import asyncio

# Setup paths
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, 'mekhane/mcp'))

# Mock mcp.types
class MockTextContent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

# Mock mcp.server.Server
class MockServer:
    def __init__(self, *args, **kwargs):
        pass
    def list_tools(self):
        def decorator(func):
            return func
        return decorator
    def call_tool(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def run(self, *args, **kwargs):
        pass
    def create_initialization_options(self):
        pass

# Apply mocks to sys.modules
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server'].Server = MockServer
sys.modules['mcp.server.stdio'] = MagicMock()
sys.modules['mcp.types'] = MagicMock()
sys.modules['mcp.types'].TextContent = MockTextContent
sys.modules['mcp.types'].Tool = MagicMock()

# Mock EmbeddingAdapter
mock_adapter_pkg = MagicMock()
sys.modules['mekhane.symploke.adapters.embedding_adapter'] = mock_adapter_pkg
MockEmbeddingAdapter = MagicMock()
mock_adapter_pkg.EmbeddingAdapter = MockEmbeddingAdapter

# Import module under test
import sophia_mcp_server

class TestSophiaErrorHandling(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        MockEmbeddingAdapter.reset_mock()
        self.mock_adapter_instance = MagicMock()
        MockEmbeddingAdapter.return_value = self.mock_adapter_instance

        # Mock indices existence
        self.original_sophia_index = sophia_mcp_server.SOPHIA_INDEX
        self.original_kairos_index = sophia_mcp_server.KAIROS_INDEX

        sophia_mcp_server.SOPHIA_INDEX = MagicMock()
        sophia_mcp_server.SOPHIA_INDEX.exists.return_value = False
        sophia_mcp_server.KAIROS_INDEX = MagicMock()
        sophia_mcp_server.KAIROS_INDEX.exists.return_value = True

    def tearDown(self):
        sophia_mcp_server.SOPHIA_INDEX = self.original_sophia_index
        sophia_mcp_server.KAIROS_INDEX = self.original_kairos_index

    def test_date_parsing_error_handling(self):
        # Setup mock result with invalid timestamp
        mock_result = MagicMock()
        mock_result.metadata = {
            "timestamp": "invalid-date-format",
            "file_path": "/tmp/test_file.txt",
            "primary_task": "Test Task"
        }
        mock_result.score = 0.9

        # Configure search return value
        self.mock_adapter_instance.search.return_value = [mock_result]
        self.mock_adapter_instance.encode.return_value = [MagicMock()]

        # Capture stderr
        captured_stderr = io.StringIO()
        original_stderr = sys.stderr
        sys.stderr = captured_stderr

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # call_tool is now the async function itself because the decorator returns it as is
            results = loop.run_until_complete(sophia_mcp_server.call_tool("search", {
                "query": "test",
                "source": "kairos",
                "recent_days": 1
            }))

            log_output = captured_stderr.getvalue()
            print("Captured Log:", log_output)

            if "Error parsing date" in log_output:
                print("FOUND_ERROR_LOG: True")
            else:
                print("FOUND_ERROR_LOG: False")
                # Fail if not found
                self.fail(f"Expected error message not found in logs: {log_output}")

        finally:
            sys.stderr = original_stderr
            loop.close()

if __name__ == '__main__':
    unittest.main()
