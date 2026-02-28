import time
from hermeneus.src.verifier import AuditStore, AuditRecord, ConsensusResult, Verdict, VerdictType
from datetime import datetime

store = AuditStore()

# Generate 100,000 dummy records
print("Generating dummy records...")
for i in range(100000):
    store.record(AuditRecord(
        id=f"audit_{i}",
        timestamp=datetime.now(),
        ccl="test_ccl",
        input_hash="hash_in",
        output_hash="hash_out",
        consensus=ConsensusResult(
            accepted=True,
            confidence=1.0,
            majority_ratio=1.0,
            verdict=Verdict(type=VerdictType.ACCEPT, reasoning="test", confidence=1.0),
            dissent_reasons=[],
            rounds=[]
        )
    ))

print("Benchmarking get()...")
start_time = time.time()
for i in range(100):
    store.get(f"audit_{90000 + i}")
end_time = time.time()

print(f"Time taken for 100 gets: {end_time - start_time} seconds")
