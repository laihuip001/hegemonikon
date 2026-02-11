import sys
import logging
from unittest.mock import MagicMock, patch

# Mock arxiv before importing ArxivCollector
mock_arxiv = MagicMock()
sys.modules["arxiv"] = mock_arxiv

from mekhane.anamnesis.collectors.arxiv import ArxivCollector

def test_fetch_by_id_logs_error(caplog):
    # Setup
    collector = ArxivCollector()

    # Configure mock to raise exception when results are iterated
    # self.client.results(search) returns an iterator
    mock_iterator = MagicMock()
    mock_iterator.__next__.side_effect = Exception("Simulated arXiv error")

    collector.client.results.return_value = mock_iterator

    # Act
    with caplog.at_level(logging.ERROR):
        result = collector.fetch_by_id("1234.5678")

    # Assert
    assert result is None
    # This assertion is expected to fail before the fix
    assert "Simulated arXiv error" in caplog.text
