import pytest
from hermeneus.src.prover import SchemaProver, ProofResult, ProofType, ProofStatus

class TestSchemaProver:
    def test_verify_valid_json(self):
        prover = SchemaProver()
        data = '{"name": "test", "age": 30}'
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        result = prover.verify(data, schema=schema)
        assert result.verified
        assert result.proof_type == ProofType.SCHEMA
        assert result.status == ProofStatus.VERIFIED
