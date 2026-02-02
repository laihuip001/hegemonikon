import unittest
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from mekhane.anamnesis.collectors.base import BaseCollector
from mekhane.anamnesis.models.paper import Paper

class TestCollector(BaseCollector):
    def search(self, query, max_results=10, categories=None):
        return [Paper(id="1", source="test", source_id="1", title="Test", abstract="Abstract")]

    def fetch_by_id(self, paper_id):
        return None

class TestBaseCollectorSync(unittest.TestCase):
    def test_collect_sync(self):
        c = TestCollector()
        c.rate_limit = 100.0 # Fast
        start = time.time()
        papers = c.collect("query")
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Test")
        # Should work without error

    def test_wait_logic(self):
        c = TestCollector()
        c.rate_limit = 10.0 # 0.1s
        c._last_request_time = time.time()
        start = time.time()
        c._rate_limit_wait()
        duration = time.time() - start
        # Should wait approx 0.1s
        self.assertGreater(duration, 0.08)

if __name__ == "__main__":
    unittest.main()
