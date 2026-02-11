"""Tests for wf_env_bridge — WF turbo inter-step context store."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mekhane.fep.wf_env_bridge import WFContext, WFStepRecord, _ctx_path


# PURPOSE: Isolate context files to tmp_path for each test
@pytest.fixture(autouse=True)
def isolated_context(tmp_path, monkeypatch):
    """Isolate context files to tmp_path for each test."""
    monkeypatch.setattr(
        "mekhane.fep.wf_env_bridge._DEFAULT_DIR", tmp_path
    )
    monkeypatch.setenv("HGK_SESSION_ID", "test_session")
    yield tmp_path


# PURPOSE: Test w f step record の実装
class TestWFStepRecord:
    # PURPOSE: auto_timestamp をテストする
    """Test suite for w f step record."""
    # PURPOSE: Verify auto timestamp behaves correctly
    def test_auto_timestamp(self):
        """Verify auto timestamp behavior."""
        rec = WFStepRecord(theorem_id="O1", output="test")
        assert rec.timestamp  # auto-generated
        assert rec.pw == 0.0

    # PURPOSE: explicit_values をテストする
    def test_explicit_values(self):
        """Verify explicit values behavior."""
        rec = WFStepRecord(
            theorem_id="S2", output="method",
            pw=0.5, metadata={"source": "test"}
        )
        assert rec.pw == 0.5
        assert rec.metadata["source"] == "test"


# PURPOSE: Test w f context の実装
class TestWFContext:
    # PURPOSE: set_and_get をテストする
    """Test suite for w f context."""
    # PURPOSE: Verify set and get behaves correctly
    def test_set_and_get(self):
        """Verify set and get behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "深い認識の出力")
        assert ctx.get_output("O1") == "深い認識の出力"

    # PURPOSE: get_nonexistent をテストする
    def test_get_nonexistent(self):
        """Verify get nonexistent behavior."""
        ctx = WFContext()
        assert ctx.get_output("X99") is None

    # PURPOSE: Context survives reconstruction
    def test_persistence(self):
        """Context survives reconstruction."""
        ctx1 = WFContext()
        ctx1.set_output("O1", "output1")
        ctx1.set_output("O2", "output2")

        # New instance should load from file
        ctx2 = WFContext()
        assert ctx2.get_output("O1") == "output1"
        assert ctx2.get_output("O2") == "output2"

    # PURPOSE: series_outputs をテストする
    def test_series_outputs(self):
        """Verify series outputs behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "o1")
        ctx.set_output("O2", "o2")
        ctx.set_output("O3", "o3")
        ctx.set_output("O4", "o4")
        ctx.set_output("S1", "s1")  # different series

        series = ctx.get_series_outputs("O")
        assert len(series) == 4
        assert series["O1"] == "o1"
        assert "S1" not in series

    # PURPOSE: series_pw をテストする
    def test_series_pw(self):
        """Verify series pw behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "o1", pw=0.5)
        ctx.set_output("O2", "o2", pw=-0.3)
        pw = ctx.get_series_pw("O")
        assert pw["O1"] == 0.5
        assert pw["O2"] == -0.3

    # PURPOSE: clear をテストする
    def test_clear(self):
        """Verify clear behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "will be cleared")
        ctx.clear()
        assert ctx.get_output("O1") is None
        assert ctx.list_outputs() == []

    # PURPOSE: list_outputs をテストする
    def test_list_outputs(self):
        """Verify list outputs behavior."""
        ctx = WFContext()
        ctx.set_output("O3", "x")
        ctx.set_output("O1", "y")
        ctx.set_output("A2", "z")
        assert ctx.list_outputs() == ["A2", "O1", "O3"]

    # PURPOSE: meta をテストする
    def test_meta(self):
        """Verify meta behavior."""
        ctx = WFContext()
        ctx.set_meta("wf_name", "/o+")
        assert ctx.get_meta("wf_name") == "/o+"
        assert ctx.get_meta("missing", "default") == "default"

    # PURPOSE: overwrite_output をテストする
    def test_overwrite_output(self):
        """Verify overwrite output behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "first")
        ctx.set_output("O1", "second")
        assert ctx.get_output("O1") == "second"

    # PURPOSE: to_cone_input をテストする
    def test_to_cone_input(self):
        """Verify to cone input behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "o1")
        ctx.set_output("O2", "o2")
        cone_input = ctx.to_cone_input("O")
        assert cone_input == {"O1": "o1", "O2": "o2"}

    # PURPOSE: export_for_cone をテストする
    def test_export_for_cone(self):
        """Verify export for cone behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "o1", pw=0.5)
        ctx.set_output("O2", "o2")
        path = ctx.export_for_cone("O")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["outputs"]["O1"] == "o1"
        assert data["pw"]["O1"] == 0.5

    # PURPOSE: get_record をテストする
    def test_get_record(self):
        """Verify get record behavior."""
        ctx = WFContext()
        ctx.set_output("O1", "output", pw=0.7, metadata={"test": True})
        rec = ctx.get_record("O1")
        assert rec is not None
        assert rec.output == "output"
        assert rec.pw == 0.7
        assert rec.metadata["test"] is True

    # PURPOSE: Japanese content survives persistence
    def test_japanese_content(self):
        """Japanese content survives persistence."""
        ctx = WFContext()
        ctx.set_output("O1", "深い認識：本質は構造的美以にある")
        ctx2 = WFContext()
        assert ctx2.get_output("O1") == "深い認識：本質は構造的美以にある"

    # PURPOSE: Multiline output survives persistence (shell env var can't do this)
    def test_multiline_output(self):
        """Multiline output survives persistence (shell env var can't do this)."""
        ctx = WFContext()
        multiline = "Line 1\nLine 2\nLine 3: 日本語"
        ctx.set_output("O1", multiline)
        ctx2 = WFContext()
        assert ctx2.get_output("O1") == multiline

    # PURPOSE: Handles corrupted context file gracefully
    def test_corrupted_file_recovery(self, isolated_context):
        """Handles corrupted context file gracefully."""
        path = isolated_context / "hgk_wf_ctx_test_session.json"
        path.write_text("not valid json{{{", encoding="utf-8")
        ctx = WFContext()
        # Should not crash, just start empty
        assert ctx.list_outputs() == []
        ctx.set_output("O1", "recovery")
        assert ctx.get_output("O1") == "recovery"
