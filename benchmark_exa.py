import time
import asyncio
from unittest.mock import MagicMock
from mekhane.ergasterion.digestor.pipeline import DigestorPipeline

class MockExaSearcher:
    async def search_academic(self, query, max_results):
        await asyncio.sleep(0.5) # Simulate API call delay
        return [MagicMock(title=f"Result for {query}", url=f"url_{query}")]

def benchmark():
    pipeline = DigestorPipeline()
    pipeline.selector = MagicMock()
    # Provide multiple topics to search to demonstrate concurrent vs sequential speedup
    pipeline.selector.get_topics.return_value = [
        {"id": f"topic_{i}", "query": f"query_{i}"} for i in range(10)
    ]

    # We patch the import inside _fetch_from_exa
    import sys
    sys.modules['mekhane.periskope.searchers.exa_searcher'] = MagicMock()
    sys.modules['mekhane.periskope.searchers.exa_searcher'].ExaSearcher = MockExaSearcher

    import os
    os.environ['EXA_API_KEY'] = 'fake_key'

    start_time = time.time()
    results = pipeline._fetch_from_exa(max_papers=20)
    end_time = time.time()

    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print(f"Results gathered: {len(results)}")

if __name__ == "__main__":
    benchmark()
