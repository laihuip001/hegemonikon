import time
import sys
import arxiv
import mekhane.anamnesis.collectors.arxiv as arxiv_module
from mekhane.anamnesis.collectors.arxiv import ArxivCollector

def run_benchmark(num_results=10, run_original=True):
    collector = ArxivCollector()

    # We will search for a generic term to get results
    query = "quantum computing"

    start_time = time.time()

    if run_original:
        print(f"Running Original (fetching {num_results} results)...")
        results = collector.search(query, max_results=num_results)
    else:
        print(f"Running Optimized (fetching {num_results} results)...")
        # Ensure our patched search does not call rate_limit per item if batched
        results = collector.search(query, max_results=num_results)

    end_time = time.time()
    duration = end_time - start_time

    print(f"Got {len(results)} results in {duration:.2f} seconds.")
    return duration

if __name__ == "__main__":
    print("Testing ArxivCollector rate limiting behavior")
    duration = run_benchmark(10, True)
