
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src.audit import AuditRecord, AuditStore

class TestAuditStoreBatch:
    """AuditStore Batch Operations Test"""

    @pytest.fixture
    def temp_store(self, tmp_path):
        """Temporary store"""
        db_path = tmp_path / "test_audit_batch.db"
        return AuditStore(db_path)

    def test_record_batch(self, temp_store):
        """Batch record"""
        records = []
        for i in range(10):
            records.append(AuditRecord(
                record_id="",
                ccl_expression=f"/batch{i}+",
                execution_result=f"Result {i}",
                debate_summary="Summary",
                consensus_accepted=True,
                confidence=0.8,
                dissent_reasons=[],
                metadata={"idx": i}
            ))

        record_ids = temp_store.record_batch(records)
        assert len(record_ids) == 10

        # Verify all recorded
        all_records = temp_store.query()
        assert len(all_records) == 10

        # Verify content of one
        rec0 = temp_store.get(record_ids[0])
        assert rec0.ccl_expression == "/batch0+"
        assert rec0.execution_result == "Result 0"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
