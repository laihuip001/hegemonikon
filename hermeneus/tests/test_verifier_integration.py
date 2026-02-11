# PROOF: [L3/テスト] <- hermeneus/tests/test_verifier_integration.py
"""
Hermēneus Verifier Integration Tests

Tests verify_execution in sync and async contexts.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src.verifier import verify_execution, ConsensusResult

def test_verify_execution_sync():
    """Test verify_execution in a synchronous context."""
    # This should just work via asyncio.run() internally
    result = verify_execution(
        ccl="test_sync",
        execution_output="output",
        debate_rounds=1
    )
    assert isinstance(result, ConsensusResult)

def test_verify_execution_async_context():
    """Test verify_execution in an asynchronous context (manual loop)."""
    async def _async_test():
        # This will fail if the fix is not working (RuntimeError)
        return verify_execution(
            ccl="test_async",
            execution_output="output",
            debate_rounds=1
        )

    # Run in an event loop
    result = asyncio.run(_async_test())
    assert isinstance(result, ConsensusResult)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
