import time
from mekhane.anamnesis.collectors.arxiv import ArxivCollector

def run_benchmark():
    collector = ArxivCollector()

    start_time = time.time()
    # Fetch 10 papers
    papers = collector.search("LLM", max_results=10)
    end_time = time.time()

    print(f"Fetched {len(papers)} papers in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    run_benchmark()
