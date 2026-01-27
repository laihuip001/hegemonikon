
import time
import shutil
import tempfile
import random
import string
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock

# Adjust path to import mekhane
import sys
import os
sys.path.append(os.getcwd())

# Mock lancedb if not installed (but I just installed it)
# Mock Embedder to avoid needing the model files
from mekhane.anamnesis import index
from mekhane.anamnesis.models.paper import Paper

class MockEmbedder:
    def __init__(self):
        pass

    def embed(self, text: str) -> list:
        return np.random.rand(384).tolist()

    def embed_batch(self, texts: list[str]) -> list[list]:
        return np.random.rand(len(texts), 384).tolist()

# Monkeypatch Embedder
index.Embedder = MockEmbedder

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_paper(i, source="test"):
    return Paper(
        id=f"gnosis_{source}_{i}",
        source=source,
        source_id=str(i),
        title=f"Paper Title {i} {generate_random_string()}",
        abstract=f"Abstract content for paper {i} " * 5,
        url=f"http://example.com/{i}"
    )

def benchmark():
    # Setup temporary directory for DB
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "lancedb"

    try:
        idx = index.GnosisIndex(lance_dir=db_path)

        # 1. Populate DB with initial papers
        INITIAL_COUNT = 10000
        print(f"Populating DB with {INITIAL_COUNT} papers...")

        initial_papers = [generate_paper(i) for i in range(INITIAL_COUNT)]

        # Batch add to avoid memory issues during setup if any
        BATCH_SIZE = 1000
        for i in range(0, INITIAL_COUNT, BATCH_SIZE):
            batch = initial_papers[i : i + BATCH_SIZE]
            idx.add_papers(batch, dedupe=False) # Skip dedupe for initial population to be fast

        print("Population complete.")

        # 2. Prepare mixed batch (duplicates and new)
        NEW_COUNT = 1000
        DUPLICATE_COUNT = 1000

        # Papers that already exist (indices 0 to DUPLICATE_COUNT-1)
        duplicate_papers = [generate_paper(i) for i in range(DUPLICATE_COUNT)]

        # Papers that are new (indices INITIAL_COUNT to INITIAL_COUNT + NEW_COUNT - 1)
        new_papers = [generate_paper(i) for i in range(INITIAL_COUNT, INITIAL_COUNT + NEW_COUNT)]

        test_batch = duplicate_papers + new_papers
        random.shuffle(test_batch)

        print(f"Benchmarking add_papers with {len(test_batch)} papers ({DUPLICATE_COUNT} duplicates, {NEW_COUNT} new)...")

        start_time = time.time()
        added_count = idx.add_papers(test_batch, dedupe=True)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Added {added_count} papers in {duration:.4f} seconds.")
        print(f"Time per paper: {duration / len(test_batch) * 1000:.4f} ms")

        return duration

    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    benchmark()
