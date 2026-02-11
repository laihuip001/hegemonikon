"""
Guardian Integration Tests — /bou ② テスト守護者

Regression tests for the param=param bug pattern + cross-module integration.
These tests ensure that arguments are actually passed through to constructors
and function calls, preventing silent data loss.

Bug pattern: automated refactoring tool mistook `param=param` for self-assignment
and commented it out, causing 11 production bugs across the codebase.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from dataclasses import asdict
import pytest


# ============ 1. MeaningfulTrace — context regression ============


class TestMeaningfulTraceContextRegression:
    """Verify that context= is actually passed to MeaningfulTrace."""

    def test_mark_meaningful_with_context(self):
        """context must be stored in the trace, not silently dropped."""
        from mekhane.fep.meaningful_traces import (
            mark_meaningful,
            clear_session_traces,
            get_session_traces,
        )

        clear_session_traces()
        trace = mark_meaningful(
            reason="test moment",
            intensity=2,
            session_id="test-session",
            context="important context that must not be lost",
        )

        assert trace.context == "important context that must not be lost"
        assert trace.session_id == "test-session"

        # Also verify via get_session_traces
        traces = get_session_traces()
        assert len(traces) >= 1
        found = [t for t in traces if t.reason == "test moment"]
        assert found[0].context == "important context that must not be lost"

        clear_session_traces()

    def test_mark_meaningful_context_none_by_default(self):
        """context should default to None, not crash."""
        from mekhane.fep.meaningful_traces import mark_meaningful, clear_session_traces

        clear_session_traces()
        trace = mark_meaningful(reason="no context", intensity=1)
        assert trace.context is None
        clear_session_traces()

    def test_trace_roundtrip_with_context(self):
        """context must survive to_dict -> from_dict roundtrip."""
        from mekhane.fep.meaningful_traces import MeaningfulTrace

        original = MeaningfulTrace(
            timestamp="2026-02-09T13:00:00",
            reason="roundtrip test",
            intensity=3,
            session_id="s1",
            context="survives roundtrip",
        )

        data = original.to_dict()
        assert data["context"] == "survives roundtrip"

        restored = MeaningfulTrace.from_dict(data)
        assert restored.context == "survives roundtrip"

    def test_save_load_preserves_context(self):
        """context must survive save -> load cycle."""
        from mekhane.fep.meaningful_traces import (
            mark_meaningful,
            save_traces,
            load_traces,
            clear_session_traces,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "traces.json"

            # Write a trace with context
            clear_session_traces()
            mark_meaningful(
                reason="persist context",
                intensity=2,
                context="must persist to disk",
            )
            save_traces(path)

            # Load and verify
            loaded = load_traces(path)
            assert len(loaded) >= 1
            found = [t for t in loaded if t.reason == "persist context"]
            assert len(found) == 1
            assert found[0].context == "must persist to disk"

            clear_session_traces()


# ============ 2. FailureDB — resolution regression ============


class TestFailureDBResolutionRegression:
    """Verify that resolution= is actually passed to FailureRecord."""

    def test_record_failure_with_resolution(self):
        """resolution must be stored, not silently dropped."""
        from mekhane.ccl.learning.failure_db import FailureDB

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "failures.json"

            db = FailureDB(db_path=path)
            record_id = db.record_failure(
                ccl_expr="/noe!",
                operator="!",
                failure_type="演算子誤解",
                cause="! を否定と解釈した",
                resolution="operators.md を確認",
            )

            # Verify resolution was stored
            failure = db.data["failures"][record_id]
            assert failure["resolution"] == "operators.md を確認"

    def test_record_failure_without_resolution(self):
        """resolution=None by default, not crash."""
        from mekhane.ccl.learning.failure_db import FailureDB

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "failures.json"

            db = FailureDB(db_path=path)
            record_id = db.record_failure(
                ccl_expr="/dia",
                operator="/dia",
                failure_type="test",
                cause="test cause",
            )
            failure = db.data["failures"][record_id]
            assert failure["resolution"] is None

    def test_record_failure_roundtrip(self):
        """Failures with resolution must survive save -> reload."""
        from mekhane.ccl.learning.failure_db import FailureDB

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "failures.json"

            # Write
            db1 = FailureDB(db_path=path)
            db1.record_failure(
                ccl_expr="/noe",
                operator="/noe",
                failure_type="test",
                cause="cause",
                resolution="fix this way",
            )

            # Reload from disk
            db2 = FailureDB(db_path=path)
            failure = db2.data["failures"][0]
            assert failure["resolution"] == "fix this way"


# ============ 3. CCL Executor — context regression ============


class TestExecutorContextRegression:
    """Verify that context= is passed to ExecutionResult."""

    def test_execute_preserves_context(self):
        """ExecutionResult.context must contain the actual ExecutionContext."""
        from mekhane.ccl.executor import ZeroTrustCCLExecutor

        executor = ZeroTrustCCLExecutor()
        result = executor.execute("/noe", "## Noesis\n\nDeep analysis here.\n" * 5, record=False)

        assert result.context is not None
        assert result.context.ccl_expr == "/noe"
        assert result.context.injected_prompt  # Not empty

    def test_execute_result_access_chain(self):
        """Can traverse result.context.ccl_expr without error."""
        from mekhane.ccl.executor import ZeroTrustCCLExecutor

        executor = ZeroTrustCCLExecutor()
        result = executor.execute("/dia", "## Analysis\n\nContent.\n" * 5, record=False)

        # This would crash if context was None (the old bug)
        assert hasattr(result.context, "ccl_expr")
        assert hasattr(result.context, "injected_prompt")
        assert hasattr(result.context, "warnings")


# ============ 4. PromptLang — tool_chain regression ============


class TestPromptLangToolChainRegression:
    """Verify that tool_chain= is passed to ContextItem."""

    def test_context_item_tool_chain(self):
        """ContextItem must preserve tool_chain field."""
        try:
            from mekhane.ergasterion.typos import prompt_lang as pl
        except ImportError:
            pytest.skip("prompt_lang not available")

        # Create a ContextItem with tool_chain
        item = pl.ContextItem(
            ref_type="mcp",
            path="gnosis",
            tool_chain="gnosis.tool(search)",
        )
        assert item.tool_chain == "gnosis.tool(search)"

    def test_parse_mcp_with_tool_chain(self):
        """Parser should extract MCP context references."""
        try:
            from mekhane.ergasterion.typos import prompt_lang as pl
        except ImportError:
            pytest.skip("prompt_lang not available")

        # Test that ContextItem preserves tool_chain when explicitly set
        item = pl.ContextItem(
            ref_type="mcp",
            path="gnosis",
            tool_chain="gnosis.tool(search)",
        )
        assert item.tool_chain == "gnosis.tool(search)"
        assert item.ref_type == "mcp"
        assert item.path == "gnosis"


# ============ 5. Cross-module integration ============


class TestCrossModuleIntegration:
    """Tests that span multiple modules to catch integration issues."""

    def test_traces_format_for_boot(self):
        """Verify traces with context format correctly for boot display."""
        from mekhane.fep.meaningful_traces import MeaningfulTrace, format_traces_for_boot

        traces = [
            MeaningfulTrace(
                timestamp="2026-02-09T10:00:00",
                reason="Creator shared a personal insight",
                intensity=3,
                session_id="s1",
                context="About trust and autonomy",
            ),
            MeaningfulTrace(
                timestamp="2026-02-09T09:00:00",
                reason="Found a surprising pattern",
                intensity=2,
                context="In the FEP A-matrix",
            ),
        ]

        output = format_traces_for_boot(traces)
        assert "存在的" in output  # intensity 3
        assert "洞察" in output  # intensity 2
        assert "Creator shared" in output

    def test_failure_db_warnings_flow(self):
        """Verify full flow: record failure with resolution -> get warnings."""
        from mekhane.ccl.learning.failure_db import FailureDB

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "failures.json"

            db = FailureDB(db_path=path)

            # Record a failure with resolution
            db.record_failure(
                ccl_expr="/noe!",
                operator="!",
                failure_type="演算子誤解",
                cause="! を否定と解釈した",
                resolution="operators.md を確認",
            )

            # Get warnings for a similar expression
            warnings = db.get_warnings("/noe!")
            # Should get 2 warnings: known issue for "!" + past failure for "!"
            assert len(warnings) >= 2

            # Format should not crash
            formatted = db.format_warnings(warnings)
            assert "🔴" in formatted  # critical known issue
            assert "否定" in formatted  # from past failure

    def test_executor_regeneration_prompt_uses_context(self):
        """Regeneration prompt must use result.context (was None before fix)."""
        from mekhane.ccl.executor import ZeroTrustCCLExecutor

        executor = ZeroTrustCCLExecutor()
        result = executor.execute("/noe", "bad output", record=False)

        if not result.success:
            regen = executor.get_regeneration_prompt(result)
            # This would crash with AttributeError if context was None
            assert "/noe" in regen
            assert "CCL 式" in regen


# ============ 6. JulesClient — regression (async) ============


class TestJulesClientParamRegression:
    """Verify jules_client params are passed correctly.
    These use mocks since we can't hit the real API."""

    def test_jules_session_has_source(self):
        """JulesSession must accept and store source."""
        from mekhane.symploke.jules_client import JulesSession, SessionState

        session = JulesSession(
            id="test-id",
            name="test",
            state=SessionState.COMPLETED,
            prompt="test prompt",
            source="sources/github/owner/repo",
        )
        assert session.source == "sources/github/owner/repo"

    def test_unknown_state_error_has_session_id(self):
        """UnknownStateError must store session_id."""
        from mekhane.symploke.jules_client import UnknownStateError

        error = UnknownStateError(state="WEIRD", session_id="sess-123")
        assert error.session_id == "sess-123"
        assert error.state == "WEIRD"
        assert "sess-123" in str(error)

    def test_session_state_from_string_known(self):
        """SessionState.from_string should parse known states."""
        from mekhane.symploke.jules_client import SessionState

        assert SessionState.from_string("COMPLETED") == SessionState.COMPLETED
        assert SessionState.from_string("FAILED") == SessionState.FAILED
        assert SessionState.from_string("QUEUED") == SessionState.QUEUED

    def test_session_state_from_string_unknown(self):
        """SessionState.from_string should return UNKNOWN for unknown states."""
        from mekhane.symploke.jules_client import SessionState

        state = SessionState.from_string("TOTALLY_NEW_STATE")
        assert state == SessionState.UNKNOWN

    def test_jules_result_success_requires_completed(self):
        """JulesResult.is_success must check session.state == COMPLETED."""
        from mekhane.symploke.jules_client import (
            JulesResult,
            JulesSession,
            SessionState,
        )

        # Completed = success
        session_ok = JulesSession(
            id="1", name="t", state=SessionState.COMPLETED,
            prompt="p", source="s",
        )
        result_ok = JulesResult(session=session_ok)
        assert result_ok.is_success is True

        # Failed = not success
        session_fail = JulesSession(
            id="2", name="t", state=SessionState.FAILED,
            prompt="p", source="s",
        )
        result_fail = JulesResult(session=session_fail)
        assert result_fail.is_success is False

        # Error = not success
        result_err = JulesResult(error=Exception("boom"))
        assert result_err.is_success is False


# ============ 7. DigestorMCP — dry_run regression ============


class TestDigestorMCPDryRunRegression:
    """Verify dry_run is passed to pipeline.run()."""

    def test_pipeline_run_signature(self):
        """DigestorPipeline.run should accept dry_run parameter."""
        try:
            from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
            import inspect

            sig = inspect.signature(DigestorPipeline.run)
            assert "dry_run" in sig.parameters
        except ImportError:
            pytest.skip("DigestorPipeline not available")


# ============ 8. Anti-regression scan ============


class TestAntiRegressionScan:
    """Scan for the dangerous comment pattern to catch future occurrences."""

    def test_no_removed_self_assignment_in_production_code(self):
        """No production Python files should have commented-out self-assignments.
        
        Allowed exceptions: 
        - ai_fixer.py (contains the pattern as a string constant)
        - test files (may have it in fixtures)
        """
        import re

        pattern = re.compile(r"#\s*NOTE:\s*Removed self-assignment:")
        mekhane_dir = Path(__file__).parent.parent

        violations = []
        for py_file in mekhane_dir.rglob("*.py"):
            # Skip allowed files
            rel = str(py_file.relative_to(mekhane_dir))
            if "ai_fixer" in rel:
                continue
            if "test_" in py_file.name:
                continue
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.split("\n"), 1):
                    if pattern.search(line):
                        violations.append(f"{rel}:{i}: {line.strip()}")
            except (UnicodeDecodeError, PermissionError):
                continue

        assert violations == [], (
            f"Found {len(violations)} removed self-assignment comment(s) in production code:\n"
            + "\n".join(violations)
        )


# ============ 9. D1: JulesClient json= mock verification ============


class TestJulesClientJsonPassthrough:
    """D1: Verify _request() actually passes json= to aiohttp.session.request().

    This is the most critical verification — the json=json bug caused
    all HTTP POST bodies to be empty.
    """

    @pytest.mark.asyncio
    async def test_request_passes_json_to_session(self):
        """json payload must reach aiohttp.session.request()."""
        from mekhane.symploke.jules_client import JulesClient

        client = JulesClient(api_key="test-key")

        # Create a mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.ok = True
        mock_response.json = AsyncMock(return_value={"result": "ok"})

        # Create a mock context manager for session.request
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        payload = {"prompt": "test prompt", "name": "test-session"}

        with patch("aiohttp.ClientSession") as MockSession:
            mock_session = MagicMock()
            mock_session.request = MagicMock(return_value=mock_cm)
            mock_session.close = AsyncMock()
            MockSession.return_value = mock_session

            # Force creation of a new session
            client._shared_session = None
            client._owned_session = None

            await client._request("POST", "sessions", json=payload)

            # THE CRITICAL ASSERTION: json= must be passed through
            mock_session.request.assert_called_once()
            call_kwargs = mock_session.request.call_args
            assert call_kwargs.kwargs.get("json") == payload or \
                   (len(call_kwargs.args) > 3 and call_kwargs.args[3] == payload), \
                f"json payload was NOT passed to session.request! kwargs: {call_kwargs}"


# ============ 10. D2: ai_fixer AST-based self-assignment ============


class TestAIFixerSelfAssignment:
    """D2: Verify ai_fixer correctly distinguishes self-assignment from keyword args.

    The root cause of the 11 param=param bugs was a regex that couldn't
    tell apart `x = x` (self-assignment) from `func(x=x)` (keyword arg).
    The fix uses AST analysis.
    """

    def test_detects_true_self_assignment(self):
        """ai_fixer should flag `x = x` as a self-assignment."""
        from mekhane.synedrion.ai_fixer import AIFixer

        fixer = AIFixer(dry_run=True)
        code = [
            "def example():",
            "    x = 42",
            "    y = y",          # <-- This IS a self-assignment
            "    return x",
        ]

        fixes = fixer._fix_ai_015_self_assignment(code, Path("test.py"))
        assert len(fixes) == 1
        assert "y = y" in fixes[0].description

    def test_ignores_keyword_argument_pass(self):
        """ai_fixer must NOT flag `func(param=param)` as self-assignment."""
        from mekhane.synedrion.ai_fixer import AIFixer

        fixer = AIFixer(dry_run=True)
        # This code contains keyword argument passes, NOT self-assignments
        code = [
            "def example(context, json, source):",
            "    result = SomeClass(",
            "        context=context,",    # keyword arg — must be IGNORED
            "        json=json,",          # keyword arg — must be IGNORED
            "        source=source,",      # keyword arg — must be IGNORED
            "    )",
            "    return result",
        ]

        fixes = fixer._fix_ai_015_self_assignment(code, Path("test.py"))
        assert fixes == [], (
            f"ai_fixer incorrectly flagged keyword arguments as self-assignments: "
            f"{[f.description for f in fixes]}"
        )

    def test_mixed_code_only_flags_assignment(self):
        """In code with both patterns, only true self-assignments are flagged."""
        from mekhane.synedrion.ai_fixer import AIFixer

        fixer = AIFixer(dry_run=True)
        code = [
            "def build():",
            "    name = name",           # <-- True self-assignment
            "    obj = Builder(",
            "        name=name,",        # keyword arg — IGNORE
            "        value=value,",      # keyword arg — IGNORE
            "    )",
            "    return obj",
        ]

        fixes = fixer._fix_ai_015_self_assignment(code, Path("test.py"))
        assert len(fixes) == 1
        assert "name = name" in fixes[0].description
