
import unittest
import logging
from unittest.mock import MagicMock, patch
from mekhane.anamnesis.collectors.arxiv import ArxivCollector

class TestArxivCollector(unittest.TestCase):
    def test_fetch_by_id_error_handling(self):
        """Test that fetch_by_id handles exceptions gracefully and logs them."""
        collector = ArxivCollector()

        # Mock the client.results to raise an exception
        with patch.object(collector.client, 'results', side_effect=Exception("Simulated API Error")):
            with self.assertLogs('mekhane.anamnesis.collectors.arxiv', level='ERROR') as cm:
                result = collector.fetch_by_id("2401.12345")

                # Check that it returns None
                self.assertIsNone(result)

                # Check that the error was logged
                self.assertTrue(any("Failed to fetch paper" in log for log in cm.output))
                self.assertTrue(any("Simulated API Error" in log for log in cm.output))

if __name__ == '__main__':
    unittest.main()
