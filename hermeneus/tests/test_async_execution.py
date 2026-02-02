
import pytest
import asyncio
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src import (
    execute_ccl,
    execute_ccl_async,
    LMQLExecutor,
    WorkflowExecutor,
    ExecutionStatus # Import this
)

try:
    from unittest.mock import AsyncMock
except ImportError:
    class AsyncMock(MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)

@pytest.mark.asyncio
async def test_execute_ccl_async():
    """Test async execution works directly"""
    with patch("hermeneus.src.compile_ccl", return_value="mock_code"), \
         patch.object(LMQLExecutor, "execute_async", new_callable=AsyncMock) as mock_exec:

        mock_exec.return_value = MagicMock(status=ExecutionStatus.SUCCESS, output="result")

        result = await execute_ccl_async("/noe+")

        assert result.output == "result"
        mock_exec.assert_awaited_once()

@pytest.mark.asyncio
async def test_sync_execute_ccl_raises_in_loop():
    """Test sync wrapper raises error in async loop"""
    with pytest.raises(RuntimeError, match="Cannot call sync execute_ccl"):
        execute_ccl("/noe+")

def test_sync_execute_ccl_works_no_loop():
    """Test sync wrapper works outside loop"""

    with patch("hermeneus.src.compile_ccl", return_value="mock_code"), \
         patch.object(LMQLExecutor, "execute_async", new_callable=AsyncMock) as mock_exec:

        mock_exec.return_value = MagicMock(status=ExecutionStatus.SUCCESS, output="result")

        result = execute_ccl("/noe+")
        assert result.output == "result"

@pytest.mark.asyncio
async def test_workflow_executor_uses_async():
    """Test WorkflowExecutor uses async path properly"""
    executor = WorkflowExecutor()

    async def mock_compile(*args):
        from hermeneus.src.executor import PhaseResult, ExecutionPhase
        return PhaseResult(ExecutionPhase.COMPILE, True, "code")

    executor._phase_compile = mock_compile

    with patch("hermeneus.src.runtime.execute_ccl_async", new_callable=AsyncMock) as mock_ccl_async:
        # result.status must be an Enum or match logic
        mock_ccl_async.return_value = MagicMock(status=ExecutionStatus.SUCCESS, output="output", error=None)

        executor._phase_verify = AsyncMock(return_value=MagicMock(success=True))
        executor._phase_audit = AsyncMock(return_value=MagicMock(success=True))
        executor._phase_compile = mock_compile

        result = await executor.execute("/noe+", verify=False, audit=False)

        assert result.success
        mock_ccl_async.assert_awaited_once()
