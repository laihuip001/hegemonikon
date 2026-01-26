import lancedb
import numpy as np
import time
import shutil
import tempfile
import pandas as pd
from pathlib import Path

def run_benchmark():
    # Use a temporary directory for the database to ensure cleanup
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "benchmark.lancedb"

        print(f"Initializing Database in {db_path}...")
        db = lancedb.connect(str(db_path))

        # Create a decent amount of data
        N_ROWS = 50000
        DIM = 128

        print(f"Generating {N_ROWS} rows of dummy data...")

        # Create a pandas dataframe
        df = pd.DataFrame({
            "vector": [np.random.rand(DIM).astype(np.float32) for _ in range(N_ROWS)],
            "id": range(N_ROWS),
            "text": [f"This is a dummy text string number {i}" for i in range(N_ROWS)],
            "category": [f"cat_{i%10}" for i in range(N_ROWS)]
        })

        print("Creating table...")
        start_setup = time.time()
        table = db.create_table("bench_table", data=df)
        print(f"Table created in {time.time() - start_setup:.4f} seconds")

        # Benchmark 1: Old Approach (to_pandas)
        print("\n--- Benchmarking Old Approach (len(table.to_pandas())) ---")
        start_time = time.time()
        count_pandas = len(table.to_pandas())
        end_time = time.time()
        pandas_duration = end_time - start_time
        print(f"Result: {count_pandas}")
        print(f"Time: {pandas_duration:.6f} seconds")

        # Benchmark 2: Optimized Approach (count_rows)
        print("\n--- Benchmarking Optimized Approach (table.count_rows()) ---")
        start_time = time.time()
        count_optimized = table.count_rows()
        end_time = time.time()
        optimized_duration = end_time - start_time
        print(f"Result: {count_optimized}")
        print(f"Time: {optimized_duration:.6f} seconds")

        print("\nSummary:")
        print(f"Baseline (to_pandas): {pandas_duration:.6f}s")
        print(f"Optimized (count_rows): {optimized_duration:.6f}s")
        if optimized_duration > 0:
            print(f"Speedup: {pandas_duration / optimized_duration:.2f}x")
        else:
            print("Speedup: Infinite (instant)")

if __name__ == "__main__":
    run_benchmark()
