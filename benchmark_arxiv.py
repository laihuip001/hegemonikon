import time
import sys
sys.path.append('.')
from mekhane.anamnesis.collectors.arxiv import ArxivCollector

def run_benchmark():
    collector = ArxivCollector()

    start_time = time.time()
    papers = collector.search(query="machine learning", max_results=100)
    end_time = time.time()

    print(f"Fetched {len(papers)} papers in {end_time - start_time:.4f} seconds.")

if __name__ == "__main__":
    run_benchmark()
