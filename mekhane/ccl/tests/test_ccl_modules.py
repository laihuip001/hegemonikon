#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ccl/tests/
# PURPOSE: CCL Pattern Cache, Workflow Signature, Output Schema, Tracer の包括テスト
"""CCL Module Tests — Batch 2"""

import json
import pytest
from pathlib import Path

from mekhane.ccl.pattern_cache import PatternCache
from mekhane.ccl.workflow_signature import (
    WorkflowSignature,
    SignatureRegistry,
    WORKFLOW_SIGNATURES,
)
from mekhane.ccl.tracer import CCLTracer, Step, Session


# ═══ PatternCache ═══════════════════════

class TestPatternCache:
    """PatternCache (Layer 3 heuristic) のテスト"""

    @pytest.fixture
    def cache(self):
        return PatternCache()

    # ── KEYWORD_MAP ──
    def test_keyword_map_exists(self, cache):
        assert len(cache.KEYWORD_MAP) > 0

    def test_modifier_map_exists(self, cache):
        assert len(cache.MODIFIER_MAP) > 0

    def test_structure_map_exists(self, cache):
        assert len(cache.STRUCTURE_MAP) > 0

    # ── generate ──
    def test_generate_analysis(self, cache):
        result = cache.generate("分析してください")
        assert result is not None
        assert "/s" in result

    def test_generate_execution(self, cache):
        result = cache.generate("実行する")
        assert result is not None
        assert "/ene" in result

    def test_generate_deep(self, cache):
        result = cache.generate("認識を深く考える")
        assert result is not None
        assert "/noe" in result

    def test_generate_judgment(self, cache):
        result = cache.generate("判定する")
        assert result is not None
        assert "/dia" in result

    def test_generate_question(self, cache):
        result = cache.generate("問いを探求する")
        assert result is not None
        assert "/zet" in result

    def test_generate_will(self, cache):
        result = cache.generate("目標を達成したい")
        assert result is not None
        assert "/bou" in result

    def test_generate_tool(self, cache):
        result = cache.generate("方法を生成する")
        assert result is not None

    def test_generate_no_match(self, cache):
        result = cache.generate("xyz random gibberish 12345")
        assert result is None

    # ── With Modifiers ──
    def test_generate_with_deepen(self, cache):
        result = cache.generate("詳細に分析する")
        assert result is not None
        assert "+" in result

    def test_generate_with_condense(self, cache):
        result = cache.generate("要約して分析する")
        assert result is not None
        assert "-" in result

    def test_generate_with_meta(self, cache):
        result = cache.generate("分析のメタ分析")
        assert result is not None
        assert "^" in result

    # ── With Structure ──
    def test_generate_sequence(self, cache):
        result = cache.generate("分析して実行する")
        assert result is not None
        assert "_" in result or "/" in result

    def test_generate_oscillation(self, cache):
        result = cache.generate("判定を往復する")
        assert result is not None
        assert "~" in result or "/dia" in result

    def test_generate_fusion(self, cache):
        result = cache.generate("判定を同時に融合")
        assert result is not None
        assert "*" in result or "/dia" in result

    # ── Loop Pattern ──
    def test_generate_loop(self, cache):
        result = cache.generate("分析を3回繰り返す")
        assert result is not None
        assert "F:" in result
        assert "3" in result


# ═══ WorkflowSignature ══════════════════

class TestWorkflowSignature:
    """WorkflowSignature データクラスのテスト"""

    def test_create(self):
        sig = WorkflowSignature(
            workflow="/test",
            ccl_signature="/noe_/dia",
            description="Test workflow",
            has_side_effects=False,
        )
        assert sig.workflow == "/test"
        assert sig.has_side_effects is False


class TestWorkflowSignatures:
    """Built-in WORKFLOW_SIGNATURES のテスト"""

    def test_boot_exists(self):
        assert "/boot" in WORKFLOW_SIGNATURES

    def test_bye_exists(self):
        assert "/bye" in WORKFLOW_SIGNATURES

    def test_eat_exists(self):
        assert "/eat" in WORKFLOW_SIGNATURES

    def test_s_exists(self):
        assert "/s" in WORKFLOW_SIGNATURES

    def test_dia_exists(self):
        assert "/dia" in WORKFLOW_SIGNATURES

    def test_noe_exists(self):
        assert "/noe" in WORKFLOW_SIGNATURES

    def test_all_have_ccl(self):
        for name, sig in WORKFLOW_SIGNATURES.items():
            assert sig.ccl_signature, f"{name} has no CCL signature"

    def test_all_have_description(self):
        for name, sig in WORKFLOW_SIGNATURES.items():
            assert sig.description, f"{name} has no description"

    def test_count(self):
        assert len(WORKFLOW_SIGNATURES) >= 10


class TestSignatureRegistry:
    """SignatureRegistry のテスト"""

    @pytest.fixture
    def registry(self):
        return SignatureRegistry()

    def test_get_with_slash(self, registry):
        sig = registry.get("/boot")
        assert sig is not None
        assert sig.workflow == "/boot"

    def test_get_without_slash(self, registry):
        sig = registry.get("boot")
        assert sig is not None

    def test_get_nonexistent(self, registry):
        sig = registry.get("nonexistent")
        assert sig is None

    def test_get_ccl(self, registry):
        ccl = registry.get_ccl("/s")
        assert ccl is not None
        assert "/" in ccl

    def test_get_ccl_nonexistent(self, registry):
        ccl = registry.get_ccl("nonexistent")
        assert ccl is None

    def test_list_pure(self, registry):
        pure = registry.list_pure()
        assert len(pure) >= 1
        for sig in pure:
            assert sig.has_side_effects is False

    def test_list_impure(self, registry):
        impure = registry.list_impure()
        assert len(impure) >= 1
        for sig in impure:
            assert sig.has_side_effects is True

    def test_add_from_yaml(self, registry, tmp_path):
        wf = tmp_path / "custom.md"
        wf.write_text("""---
ccl_signature: "/noe_/dia_/ene"
description: Custom workflow
has_side_effects: false
---

# Custom WF
""")
        registry.add_from_yaml(wf)
        sig = registry.get("/custom")
        assert sig is not None
        assert sig.ccl_signature == "/noe_/dia_/ene"

    def test_add_from_yaml_nonexistent(self, registry, tmp_path):
        registry.add_from_yaml(tmp_path / "nonexistent.md")
        # Should not raise

    def test_add_from_yaml_no_signature(self, registry, tmp_path):
        wf = tmp_path / "plain.md"
        wf.write_text("""---
description: No CCL signature
---

# Plain WF
""")
        registry.add_from_yaml(wf)
        sig = registry.get("/plain")
        assert sig is None


# ═══ CCLTracer ══════════════════════════

class TestStep:
    """Step データクラスのテスト"""

    def test_create(self):
        s = Step(timestamp="2026-01-01", op="/noe", status="running", note="test")
        assert s.op == "/noe"
        assert s.status == "running"


class TestSession:
    """Session データクラスのテスト"""

    def test_create(self):
        s = Session(
            session_id="test-123",
            expression="/noe+",
            start_time="2026-01-01",
            end_time=None,
            status="running",
            steps=[],
        )
        assert s.session_id == "test-123"
        assert s.end_time is None


class TestCCLTracer:
    """CCLTracer のテスト"""

    @pytest.fixture
    def tracer(self, tmp_path):
        return CCLTracer(base_path=tmp_path)

    def test_init(self, tracer):
        assert tracer.current_session is None

    def test_start_session(self, tracer):
        session_id = tracer.start("/noe+_/dia")
        assert session_id is not None
        assert tracer.current_session is not None

    def test_start_creates_directory(self, tracer, tmp_path):
        session_id = tracer.start("/noe")
        session_dir = tmp_path / session_id
        assert session_dir.exists()

    def test_step(self, tracer):
        tracer.start("/noe+")
        tracer.step("/noe", status="running")
        assert len(tracer.current_session.steps) >= 1

    def test_step_success(self, tracer):
        tracer.start("/noe+_/dia")
        tracer.step("/noe", status="success", note="Completed")
        assert tracer.current_session.steps[-1]["status"] == "success"

    def test_end_session(self, tracer, tmp_path):
        session_id = tracer.start("/noe")
        tracer.step("/noe", "success")
        tracer.end("completed")
        # end() clears current_session, check persisted state
        import json
        state = json.loads((tmp_path / session_id / "state.json").read_text())
        assert state["status"] == "completed"
        assert state["end_time"] is not None

    def test_end_creates_summary(self, tracer, tmp_path):
        session_id = tracer.start("/noe+")
        tracer.step("/noe", "success")
        tracer.end()
        summary = tmp_path / session_id / "summary.md"
        assert summary.exists()

    def test_end_saves_state(self, tracer, tmp_path):
        session_id = tracer.start("/noe")
        tracer.step("/noe", "success")
        tracer.end()
        state_file = tmp_path / session_id / "state.json"
        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["status"] == "completed"

    def test_load_session(self, tracer, tmp_path):
        session_id = tracer.start("/test")
        tracer.step("/test", "success")
        tracer.end()

        # Create new tracer and load
        tracer2 = CCLTracer(base_path=tmp_path)
        loaded = tracer2.load_session(session_id)
        assert loaded is True
        assert tracer2.current_session is not None

    def test_load_nonexistent(self, tracer):
        loaded = tracer.load_session("nonexistent-session-id")
        assert loaded is False

    def test_multiple_steps(self, tracer):
        tracer.start("/noe+_/dia_/ene")
        tracer.step("/noe", "running")
        tracer.step("/noe", "success")
        tracer.step("/dia", "running")
        tracer.step("/dia", "success")
        assert len(tracer.current_session.steps) >= 4
