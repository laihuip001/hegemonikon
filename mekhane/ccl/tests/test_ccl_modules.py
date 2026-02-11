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

# PURPOSE: Test suite validating pattern cache correctness
class TestPatternCache:
    """PatternCache (Layer 3 heuristic) のテスト"""

    # PURPOSE: Verify cache behaves correctly
    @pytest.fixture
    def cache(self):
        """Verify cache behavior."""
        return PatternCache()

    # ── KEYWORD_MAP ──
    # PURPOSE: Verify keyword map exists behaves correctly
    def test_keyword_map_exists(self, cache):
        """Verify keyword map exists behavior."""
        assert len(cache.KEYWORD_MAP) > 0

    # PURPOSE: Verify modifier map exists behaves correctly
    def test_modifier_map_exists(self, cache):
        """Verify modifier map exists behavior."""
        assert len(cache.MODIFIER_MAP) > 0

    # PURPOSE: Verify structure map exists behaves correctly
    def test_structure_map_exists(self, cache):
        """Verify structure map exists behavior."""
        assert len(cache.STRUCTURE_MAP) > 0

    # ── generate ──
    # PURPOSE: Verify generate analysis behaves correctly
    def test_generate_analysis(self, cache):
        """Verify generate analysis behavior."""
        result = cache.generate("分析してください")
        assert result is not None
        assert "/s" in result

    # PURPOSE: Verify generate execution behaves correctly
    def test_generate_execution(self, cache):
        """Verify generate execution behavior."""
        result = cache.generate("実行する")
        assert result is not None
        assert "/ene" in result

    # PURPOSE: Verify generate deep behaves correctly
    def test_generate_deep(self, cache):
        """Verify generate deep behavior."""
        result = cache.generate("認識を深く考える")
        assert result is not None
        assert "/noe" in result

    # PURPOSE: Verify generate judgment behaves correctly
    def test_generate_judgment(self, cache):
        """Verify generate judgment behavior."""
        result = cache.generate("判定する")
        assert result is not None
        assert "/dia" in result

    # PURPOSE: Verify generate question behaves correctly
    def test_generate_question(self, cache):
        """Verify generate question behavior."""
        result = cache.generate("問いを探求する")
        assert result is not None
        assert "/zet" in result

    # PURPOSE: Verify generate will behaves correctly
    def test_generate_will(self, cache):
        """Verify generate will behavior."""
        result = cache.generate("目標を達成したい")
        assert result is not None
        assert "/bou" in result

    # PURPOSE: Verify generate tool behaves correctly
    def test_generate_tool(self, cache):
        """Verify generate tool behavior."""
        result = cache.generate("方法を生成する")
        assert result is not None

    # PURPOSE: Verify generate no match behaves correctly
    def test_generate_no_match(self, cache):
        """Verify generate no match behavior."""
        result = cache.generate("xyz random gibberish 12345")
        assert result is None

    # ── With Modifiers ──
    # PURPOSE: Verify generate with deepen behaves correctly
    def test_generate_with_deepen(self, cache):
        """Verify generate with deepen behavior."""
        result = cache.generate("詳細に分析する")
        assert result is not None
        assert "+" in result

    # PURPOSE: Verify generate with condense behaves correctly
    def test_generate_with_condense(self, cache):
        """Verify generate with condense behavior."""
        result = cache.generate("要約して分析する")
        assert result is not None
        assert "-" in result

    # PURPOSE: Verify generate with meta behaves correctly
    def test_generate_with_meta(self, cache):
        """Verify generate with meta behavior."""
        result = cache.generate("分析のメタ分析")
        assert result is not None
        assert "^" in result

    # ── With Structure ──
    # PURPOSE: Verify generate sequence behaves correctly
    def test_generate_sequence(self, cache):
        """Verify generate sequence behavior."""
        result = cache.generate("分析して実行する")
        assert result is not None
        assert "_" in result or "/" in result

    # PURPOSE: Verify generate oscillation behaves correctly
    def test_generate_oscillation(self, cache):
        """Verify generate oscillation behavior."""
        result = cache.generate("判定を往復する")
        assert result is not None
        assert "~" in result or "/dia" in result

    # PURPOSE: Verify generate fusion behaves correctly
    def test_generate_fusion(self, cache):
        """Verify generate fusion behavior."""
        result = cache.generate("判定を同時に融合")
        assert result is not None
        assert "*" in result or "/dia" in result

    # ── Loop Pattern ──
    # PURPOSE: Verify generate loop behaves correctly
    def test_generate_loop(self, cache):
        """Verify generate loop behavior."""
        result = cache.generate("分析を3回繰り返す")
        assert result is not None
        assert "F:" in result
        assert "3" in result


# ═══ WorkflowSignature ══════════════════

# PURPOSE: Test suite validating workflow signature correctness
class TestWorkflowSignature:
    """WorkflowSignature データクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        sig = WorkflowSignature(
            workflow="/test",
            ccl_signature="/noe_/dia",
            description="Test workflow",
            has_side_effects=False,
        )
        assert sig.workflow == "/test"
        assert sig.has_side_effects is False


# PURPOSE: Test suite validating workflow signatures correctness
class TestWorkflowSignatures:
    """Built-in WORKFLOW_SIGNATURES のテスト"""

    # PURPOSE: Verify boot exists behaves correctly
    def test_boot_exists(self):
        """Verify boot exists behavior."""
        assert "/boot" in WORKFLOW_SIGNATURES

    # PURPOSE: Verify bye exists behaves correctly
    def test_bye_exists(self):
        """Verify bye exists behavior."""
        assert "/bye" in WORKFLOW_SIGNATURES

    # PURPOSE: Verify eat exists behaves correctly
    def test_eat_exists(self):
        """Verify eat exists behavior."""
        assert "/eat" in WORKFLOW_SIGNATURES

    # PURPOSE: Verify s exists behaves correctly
    def test_s_exists(self):
        """Verify s exists behavior."""
        assert "/s" in WORKFLOW_SIGNATURES

    # PURPOSE: Verify dia exists behaves correctly
    def test_dia_exists(self):
        """Verify dia exists behavior."""
        assert "/dia" in WORKFLOW_SIGNATURES

    # PURPOSE: Verify noe exists behaves correctly
    def test_noe_exists(self):
        """Verify noe exists behavior."""
        assert "/noe" in WORKFLOW_SIGNATURES

    # PURPOSE: Verify all have ccl behaves correctly
    def test_all_have_ccl(self):
        """Verify all have ccl behavior."""
        for name, sig in WORKFLOW_SIGNATURES.items():
            assert sig.ccl_signature, f"{name} has no CCL signature"

    # PURPOSE: Verify all have description behaves correctly
    def test_all_have_description(self):
        """Verify all have description behavior."""
        for name, sig in WORKFLOW_SIGNATURES.items():
            assert sig.description, f"{name} has no description"

    # PURPOSE: Verify count behaves correctly
    def test_count(self):
        """Verify count behavior."""
        assert len(WORKFLOW_SIGNATURES) >= 10


# PURPOSE: Test suite validating signature registry correctness
class TestSignatureRegistry:
    """SignatureRegistry のテスト"""

    # PURPOSE: Verify registry behaves correctly
    @pytest.fixture
    def registry(self):
        """Verify registry behavior."""
        return SignatureRegistry()

    # PURPOSE: Verify get with slash behaves correctly
    def test_get_with_slash(self, registry):
        """Verify get with slash behavior."""
        sig = registry.get("/boot")
        assert sig is not None
        assert sig.workflow == "/boot"

    # PURPOSE: Verify get without slash behaves correctly
    def test_get_without_slash(self, registry):
        """Verify get without slash behavior."""
        sig = registry.get("boot")
        assert sig is not None

    # PURPOSE: Verify get nonexistent behaves correctly
    def test_get_nonexistent(self, registry):
        """Verify get nonexistent behavior."""
        sig = registry.get("nonexistent")
        assert sig is None

    # PURPOSE: Verify get ccl behaves correctly
    def test_get_ccl(self, registry):
        """Verify get ccl behavior."""
        ccl = registry.get_ccl("/s")
        assert ccl is not None
        assert "/" in ccl

    # PURPOSE: Verify get ccl nonexistent behaves correctly
    def test_get_ccl_nonexistent(self, registry):
        """Verify get ccl nonexistent behavior."""
        ccl = registry.get_ccl("nonexistent")
        assert ccl is None

    # PURPOSE: Verify list pure behaves correctly
    def test_list_pure(self, registry):
        """Verify list pure behavior."""
        pure = registry.list_pure()
        assert len(pure) >= 1
        for sig in pure:
            assert sig.has_side_effects is False

    # PURPOSE: Verify list impure behaves correctly
    def test_list_impure(self, registry):
        """Verify list impure behavior."""
        impure = registry.list_impure()
        assert len(impure) >= 1
        for sig in impure:
            assert sig.has_side_effects is True

    # PURPOSE: Verify add from yaml behaves correctly
    def test_add_from_yaml(self, registry, tmp_path):
        """Verify add from yaml behavior."""
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

    # PURPOSE: Verify add from yaml nonexistent behaves correctly
    def test_add_from_yaml_nonexistent(self, registry, tmp_path):
        """Verify add from yaml nonexistent behavior."""
        registry.add_from_yaml(tmp_path / "nonexistent.md")
        # Should not raise

    # PURPOSE: Verify add from yaml no signature behaves correctly
    def test_add_from_yaml_no_signature(self, registry, tmp_path):
        """Verify add from yaml no signature behavior."""
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

# PURPOSE: Test suite validating step correctness
class TestStep:
    """Step データクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        s = Step(timestamp="2026-01-01", op="/noe", status="running", note="test")
        assert s.op == "/noe"
        assert s.status == "running"


# PURPOSE: Test suite validating session correctness
class TestSession:
    """Session データクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
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


# PURPOSE: Test suite validating c c l tracer correctness
class TestCCLTracer:
    """CCLTracer のテスト"""

    # PURPOSE: Verify tracer behaves correctly
    @pytest.fixture
    def tracer(self, tmp_path):
        """Verify tracer behavior."""
        return CCLTracer(base_path=tmp_path)

    # PURPOSE: Verify init behaves correctly
    def test_init(self, tracer):
        """Verify init behavior."""
        assert tracer.current_session is None

    # PURPOSE: Verify start session behaves correctly
    def test_start_session(self, tracer):
        """Verify start session behavior."""
        session_id = tracer.start("/noe+_/dia")
        assert session_id is not None
        assert tracer.current_session is not None

    # PURPOSE: Verify start creates directory behaves correctly
    def test_start_creates_directory(self, tracer, tmp_path):
        """Verify start creates directory behavior."""
        session_id = tracer.start("/noe")
        session_dir = tmp_path / session_id
        assert session_dir.exists()

    # PURPOSE: Verify step behaves correctly
    def test_step(self, tracer):
        """Verify step behavior."""
        tracer.start("/noe+")
        tracer.step("/noe", status="running")
        assert len(tracer.current_session.steps) >= 1

    # PURPOSE: Verify step success behaves correctly
    def test_step_success(self, tracer):
        """Verify step success behavior."""
        tracer.start("/noe+_/dia")
        tracer.step("/noe", status="success", note="Completed")
        assert tracer.current_session.steps[-1]["status"] == "success"

    # PURPOSE: Verify end session behaves correctly
    def test_end_session(self, tracer, tmp_path):
        """Verify end session behavior."""
        session_id = tracer.start("/noe")
        tracer.step("/noe", "success")
        tracer.end("completed")
        # end() clears current_session, check persisted state
        import json
        state = json.loads((tmp_path / session_id / "state.json").read_text())
        assert state["status"] == "completed"
        assert state["end_time"] is not None

    # PURPOSE: Verify end creates summary behaves correctly
    def test_end_creates_summary(self, tracer, tmp_path):
        """Verify end creates summary behavior."""
        session_id = tracer.start("/noe+")
        tracer.step("/noe", "success")
        tracer.end()
        summary = tmp_path / session_id / "summary.md"
        assert summary.exists()

    # PURPOSE: Verify end saves state behaves correctly
    def test_end_saves_state(self, tracer, tmp_path):
        """Verify end saves state behavior."""
        session_id = tracer.start("/noe")
        tracer.step("/noe", "success")
        tracer.end()
        state_file = tmp_path / session_id / "state.json"
        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["status"] == "completed"

    # PURPOSE: Verify load session behaves correctly
    def test_load_session(self, tracer, tmp_path):
        """Verify load session behavior."""
        session_id = tracer.start("/test")
        tracer.step("/test", "success")
        tracer.end()

        # Create new tracer and load
        tracer2 = CCLTracer(base_path=tmp_path)
        loaded = tracer2.load_session(session_id)
        assert loaded is True
        assert tracer2.current_session is not None

    # PURPOSE: Verify load nonexistent behaves correctly
    def test_load_nonexistent(self, tracer):
        """Verify load nonexistent behavior."""
        loaded = tracer.load_session("nonexistent-session-id")
        assert loaded is False

    # PURPOSE: Verify multiple steps behaves correctly
    def test_multiple_steps(self, tracer):
        """Verify multiple steps behavior."""
        tracer.start("/noe+_/dia_/ene")
        tracer.step("/noe", "running")
        tracer.step("/noe", "success")
        tracer.step("/dia", "running")
        tracer.step("/dia", "success")
        assert len(tracer.current_session.steps) >= 4
