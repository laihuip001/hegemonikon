#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/symploke/tests/test_intent_wal.py O1->Zet->Impl
# PURPOSE: Tests for Intent-WAL Manager.
"""Tests for Intent-WAL Manager."""

import sys
import tempfile
from pathlib import Path

import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.intent_wal import (
    CONTEXT_HEALTH_LEVELS,
    IntentWAL,
    IntentWALManager,
    ProgressEntry,
)


# PURPOSE: Test IntentWAL dataclass serialization
class TestIntentWALDataStructure:
    """Test IntentWAL dataclass serialization."""

    # PURPOSE: Minimal WAL with only required fields
    def test_create_minimal_wal(self):
        """Minimal WAL with only required fields."""
        wal = IntentWAL(session_id="test-123", session_goal="Fix bug")
        assert wal.session_id == "test-123"
        assert wal.session_goal == "Fix bug"
        assert wal.agent == "Claude"
        assert wal.context_health_level == "green"
        assert wal.created_at != ""

    # PURPOSE: to_dict -> from_dict should preserve all fields
    def test_roundtrip_serialization(self):
        """to_dict -> from_dict should preserve all fields."""
        wal = IntentWAL(
            session_id="test-456",
            session_goal="Implement feature X",
            acceptance_criteria=["Tests pass", "No warnings"],
            context="Previous session worked on Y",
        )
        wal.progress.append(
            ProgressEntry(
                timestamp="2026-02-15T16:00:00+09:00",
                step=1,
                action="Setup",
                status="done",
                detail="Created files",
            )
        )

        data = wal.to_dict()
        restored = IntentWAL.from_dict(data)

        assert restored.session_id == "test-456"
        assert restored.session_goal == "Implement feature X"
        assert len(restored.acceptance_criteria) == 2
        assert len(restored.progress) == 1
        assert restored.progress[0].step == 1
        assert restored.progress[0].status == "done"

    # PURPOSE: Serialized dict should include version 1.0
    def test_version_field(self):
        """Serialized dict should include version 1.0."""
        wal = IntentWAL(session_id="v", session_goal="test")
        data = wal.to_dict()
        assert data["version"] == "1.0"


# PURPOSE: Test WAL Manager operations
class TestIntentWALManager:
    """Test WAL Manager operations."""

    # PURPOSE: Create a new WAL file
    def test_create_wal(self):
        """Create a new WAL file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            wal, path = mgr.create(
                session_goal="Test goal",
                session_id="create-test",
            )

            assert path.exists()
            assert path.name.startswith("intent_")
            assert path.suffix == ".yaml"
            assert wal.session_goal == "Test goal"

            # Verify file content
            with open(path) as f:
                data = yaml.safe_load(f)
            assert data["intent"]["session_goal"] == "Test goal"

    # PURPOSE: Progress updates are append-only
    def test_update_progress_appends(self):
        """Progress updates are append-only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            mgr.create(session_goal="Multi-step", session_id="progress-test")

            mgr.update_progress(step=1, action="Step one", status="done")
            mgr.update_progress(step=2, action="Step two", status="in_progress")

            assert len(mgr.current.progress) == 2
            assert mgr.current.progress[0].step == 1
            assert mgr.current.progress[1].step == 2

            # Verify persisted
            reloaded = mgr.load(mgr.current_path)
            assert len(reloaded.progress) == 2

    # PURPOSE: Context health updates (BC-18 integration)
    def test_update_context_health(self):
        """Context health updates (BC-18 integration)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            mgr.create(session_goal="Health test", session_id="health-test")

            mgr.update_context_health(level="yellow", savepoint="/tmp/save.md")
            assert mgr.current.context_health_level == "yellow"
            assert mgr.current.savepoint == "/tmp/save.md"

    # PURPOSE: Invalid health level should raise ValueError
    def test_invalid_health_level_raises(self):
        """Invalid health level should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            mgr.create(session_goal="Invalid", session_id="invalid-test")

            try:
                mgr.update_context_health(level="purple")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

    # PURPOSE: load_latest returns most recent WAL
    def test_load_latest(self):
        """load_latest returns most recent WAL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))

            # Create two WALs
            _, path1 = mgr.create(session_goal="First", session_id="first")
            # Force different filename
            import time

            time.sleep(0.1)
            second_path = Path(tmpdir) / "intent_99991231_2359.yaml"
            wal2 = IntentWAL(session_id="second", session_goal="Second")
            with open(second_path, "w") as f:
                yaml.dump(wal2.to_dict(), f, allow_unicode=True)

            latest = mgr.load_latest()
            assert latest is not None
            assert latest.session_goal == "Second"

    # PURPOSE: load_latest returns None when no WALs exist
    def test_load_latest_empty_dir(self):
        """load_latest returns None when no WALs exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            assert mgr.load_latest() is None

    # PURPOSE: Update recovery information
    def test_update_recovery(self):
        """Update recovery information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            mgr.create(session_goal="Recovery test", session_id="recovery-test")

            mgr.update_recovery(
                last_file_edited="src/main.py",
                uncommitted_changes=True,
                blockers=["API down"],
            )

            assert mgr.current.last_file_edited == "src/main.py"
            assert mgr.current.uncommitted_changes is True
            assert mgr.current.blockers == ["API down"]

    # PURPOSE: Operations without active WAL should raise RuntimeError
    def test_no_active_wal_raises(self):
        """Operations without active WAL should raise RuntimeError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            try:
                mgr.update_progress(step=1, action="Fail", status="done")
                assert False, "Should have raised RuntimeError"
            except RuntimeError:
                pass


# PURPOSE: Test WAL to Handoff/Boot section conversion
class TestHandoffConversion:
    """Test WAL to Handoff/Boot section conversion."""

    # PURPOSE: Convert WAL to Handoff-compatible markdown section
    def test_to_handoff_section(self):
        """Convert WAL to Handoff-compatible markdown section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            mgr.create(
                session_goal="Build dashboard",
                session_id="handoff-test",
                acceptance_criteria=["All cards render", "No console errors"],
            )
            mgr.update_progress(step=1, action="Create API", status="done")
            mgr.update_progress(step=2, action="Build cards", status="in_progress")

            section = mgr.to_handoff_section()
            assert "## Intent-WAL" in section
            assert "Build dashboard" in section
            assert "All cards render" in section
            assert "| 1 | Create API | done |" in section
            assert "green" in section

    # PURPOSE: Convert WAL to Boot Report section
    def test_to_boot_section(self):
        """Convert WAL to Boot Report section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            mgr.create(session_goal="Fix safety", session_id="boot-test")
            mgr.update_progress(step=1, action="Audit", status="done")

            section = mgr.to_boot_section()
            assert "## Intent-WAL" in section
            assert "session_goal" in section
            assert "Fix safety" in section
            assert "1/1 steps completed" in section

    # PURPOSE: Conversion with no active WAL returns empty string
    def test_empty_wal_conversion(self):
        """Conversion with no active WAL returns empty string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = IntentWALManager(wal_dir=Path(tmpdir))
            assert mgr.to_handoff_section() == ""
            assert mgr.to_boot_section() == ""


# PURPOSE: Run all tests and report results
def run_tests():
    """Run all tests and report results."""
    import traceback

    test_classes = [TestIntentWALDataStructure, TestIntentWALManager, TestHandoffConversion]
    passed = 0
    failed = 0
    errors = []

    for cls in test_classes:
        print(f"\n{'='*60}")
        print(f"  {cls.__name__}")
        print(f"{'='*60}")
        instance = cls()
        for method_name in sorted(dir(instance)):
            if not method_name.startswith("test_"):
                continue
            method = getattr(instance, method_name)
            try:
                method()
                print(f"  ✅ {method_name}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                errors.append((f"{cls.__name__}.{method_name}", traceback.format_exc()))
                failed += 1

    print(f"\n{'='*60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    if errors:
        print("\nErrors:")
        for name, tb in errors:
            print(f"\n--- {name} ---")
            print(tb)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
