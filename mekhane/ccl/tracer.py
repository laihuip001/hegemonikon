# PROOF: [L1/定理] CCL→CCLパーサーが必要→tracer が担う
#!/usr/bin/env python3
"""
CCL Tracer v2.0

Session-isolated tracing for CCL execution debugging.
Each session gets its own directory with trace.log, state.json, and summary.md.

Usage:
    from mekhane.ccl import CCLTracer

    tracer = CCLTracer()
    tracer.start("/s+_/dia")
    tracer.step("/s+", status="success")
    tracer.step("/dia", status="success")
    tracer.end()
"""

import datetime
import json
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict

TRACES_BASE = Path("/home/laihuip001/oikos/mneme/.hegemonikon/ccl_traces")


@dataclass
class Step:
    """A single step in CCL execution."""

    timestamp: str
    op: str
    status: str
    note: str


@dataclass
class Session:
    """A CCL execution session."""

    session_id: str
    expression: str
    start_time: str
    end_time: Optional[str]
    status: str
    steps: List[dict]


class CCLTracer:
    """
    Session-isolated CCL tracer.

    Creates a directory for each session under ccl_traces/{session_id}/.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the tracer.

        Args:
            base_path: Override default traces directory
        """
        self.base_path = base_path or TRACES_BASE
        self.current_session: Optional[Session] = None
        self.session_dir: Optional[Path] = None

    def start(self, expression: str) -> str:
        """
        Start a new tracing session.

        Args:
            expression: The CCL expression being executed

        Returns:
            Session ID
        """
        session_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # Create session directory
        self.session_dir = self.base_path / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize session
        self.current_session = Session(
            session_id=session_id,
            expression=expression,
            start_time=datetime.datetime.now().isoformat(),
            end_time=None,
            status="running",
            steps=[],
        )

        # Save initial state
        self._save_state()
        self._log(f"SESSION_START: {expression}")

        print(f"CCL_TRACE: Started session {session_id} for: {expression}")
        return session_id

    def step(self, op: str, status: str = "running", note: str = ""):
        """
        Log a step in the current session.

        Args:
            op: The operation/workflow being executed
            status: Status (running, success, failed, skipped)
            note: Optional note
        """
        if not self.current_session:
            print("Error: No active CCL session. Call start() first.")
            return

        step = Step(
            timestamp=datetime.datetime.now().isoformat(),
            op=op,
            status=status,
            # NOTE: Removed self-assignment: note = note
        )

        self.current_session.steps.append(asdict(step))
        self._save_state()
        self._log(f"STEP: {op} [{status}] {note}")

        print(f"CCL_TRACE: {op} [{status}] {note}")

    def end(self, status: str = "completed"):
        """
        End the current session.

        Args:
            status: Final status (completed, failed, aborted)
        """
        if not self.current_session:
            print("Error: No active CCL session.")
            return

        self.current_session.end_time = datetime.datetime.now().isoformat()
        self.current_session.status = status

        self._save_state()
        self._generate_summary()
        self._log(f"SESSION_END: {status}")

        duration = self._calculate_duration()
        print(
            f"CCL_TRACE: Ended session {self.current_session.session_id} "
            f"[{status}] Duration: {duration}"
        )

        self.current_session = None
        self.session_dir = None

    def load_session(self, session_id: str) -> bool:
        """
        Load an existing session for continued tracing.

        Args:
            session_id: The session ID to load

        Returns:
            True if loaded successfully
        """
        session_dir = self.base_path / session_id
        state_file = session_dir / "state.json"

        if not state_file.exists():
            return False

        try:
            state = json.loads(state_file.read_text())
            self.current_session = Session(
                session_id=state["session_id"],
                expression=state["expression"],
                start_time=state["start_time"],
                end_time=state.get("end_time"),
                status=state["status"],
                steps=state.get("steps", []),
            )
            self.session_dir = session_dir
            return True
        except (json.JSONDecodeError, KeyError):
            return False

    @classmethod
    def load_latest(cls, base_path: Optional[Path] = None) -> Optional["CCLTracer"]:
        """
        Load the most recent session.

        Returns:
            CCLTracer with loaded session, or None
        """
        tracer = cls(base_path)
        sessions = list(tracer.base_path.glob("*/state.json"))
        if not sessions:
            return None

        latest = max(sessions, key=lambda p: p.stat().st_mtime)
        session_id = latest.parent.name

        if tracer.load_session(session_id):
            return tracer
        return None

    def _save_state(self):
        """Save current session state to JSON."""
        if not self.session_dir or not self.current_session:
            return

        state_file = self.session_dir / "state.json"
        state_file.write_text(json.dumps(asdict(self.current_session), indent=2))

    def _log(self, message: str):
        """Append to trace log."""
        if not self.session_dir:
            return

        log_file = self.session_dir / "trace.log"
        timestamp = datetime.datetime.now().isoformat()
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def _generate_summary(self):
        """Generate summary.md for the session."""
        if not self.session_dir or not self.current_session:
            return

        s = self.current_session

        # Count step statuses
        success_count = sum(1 for step in s.steps if step.get("status") == "success")
        failed_count = sum(1 for step in s.steps if step.get("status") == "failed")

        summary = f"""# CCL Session Summary

**Session ID**: {s.session_id}
**Expression**: `{s.expression}`
**Status**: {s.status}
**Duration**: {self._calculate_duration()}

## Steps

| # | Operation | Status | Note |
|---|-----------|--------|------|
"""
        for i, step in enumerate(s.steps, 1):
            status_emoji = (
                "✅"
                if step.get("status") == "success"
                else "❌" if step.get("status") == "failed" else "⏳"
            )
            summary += f"| {i} | `{step.get('op')}` | {status_emoji} {step.get('status')} | {step.get('note', '')} |\n"

        summary += f"""
## Result

- **Total Steps**: {len(s.steps)}
- **Success**: {success_count}
- **Failed**: {failed_count}

---
*Generated by CCL Tracer v2.0*
"""

        summary_file = self.session_dir / "summary.md"
        summary_file.write_text(summary)

    def _calculate_duration(self) -> str:
        """Calculate session duration."""
        if not self.current_session:
            return "unknown"

        try:
            start = datetime.datetime.fromisoformat(self.current_session.start_time)
            end = datetime.datetime.fromisoformat(
                self.current_session.end_time or datetime.datetime.now().isoformat()
            )
            return str(end - start)
        except (ValueError, TypeError):
            return "unknown"


# CLI support
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CCL Tracer v2.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Start
    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("expression", help="CCL expression to trace")

    # Step
    step_parser = subparsers.add_parser("step")
    step_parser.add_argument("op", help="Current operation")
    step_parser.add_argument("--status", default="running")
    step_parser.add_argument("--note", default="")

    # End
    end_parser = subparsers.add_parser("end")
    end_parser.add_argument("--status", default="completed")

    args = parser.parse_args()

    # For CLI, we need to persist tracer state
    # This is simplified - in production, use state file
    tracer = CCLTracer()

    if args.command == "start":
        tracer.start(args.expression)
    elif args.command == "step":
        # Load existing session from latest directory
        latest = max(TRACES_BASE.glob("*/state.json"), default=None)
        if latest:
            state = json.loads(latest.read_text())
            tracer.current_session = Session(**state)
            tracer.session_dir = latest.parent
            tracer.step(args.op, args.status, args.note)
    elif args.command == "end":
        latest = max(TRACES_BASE.glob("*/state.json"), default=None)
        if latest:
            state = json.loads(latest.read_text())
            tracer.current_session = Session(**state)
            tracer.session_dir = latest.parent
            tracer.end(args.status)
