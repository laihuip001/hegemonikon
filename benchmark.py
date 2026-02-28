import time
import sys
import uuid
from datetime import datetime
from dataclasses import field, dataclass
from typing import Dict, Any

from hermeneus.src.verifier import AuditStore, AuditRecord, ConsensusResult, Verdict, VerdictType, DebateRound

def create_dummy_audit(id_str):
    consensus = ConsensusResult(
        accepted=True,
        confidence=0.9,
        majority_ratio=1.0,
        verdict=Verdict(VerdictType.ACCEPT, "ok", 0.9),
        dissent_reasons=[],
        rounds=[]
    )
    return AuditRecord(
        id=id_str,
        timestamp=datetime.now(),
        ccl="/test",
        input_hash="hash_in",
        output_hash="hash_out",
        consensus=consensus,
    )

store = AuditStore()

# Populate
print("Populating store...")
n_items = 100000
ids = []
for i in range(n_items):
    id_str = f"audit_{i}"
    ids.append(id_str)
    store.record(create_dummy_audit(id_str))

# Benchmark get()
print("Benchmarking get()...")
start = time.perf_counter()
for i in range(100):
    # Query something towards the end to show worst-case of linear search
    store.get(f"audit_{n_items - 1 - i}")
end = time.perf_counter()

print(f"Baseline Time for 100 queries: {end - start:.6f} seconds")

# Also measure query to ensure we aren't breaking anything
start = time.perf_counter()
store.query(limit=5)
end = time.perf_counter()
print(f"Query baseline Time: {end - start:.6f} seconds")
