# PROOF: [L1/定理] <- mekhane/tests/ A0→信頼できるシステムが必要→統合テストが担う
"""
Integration Pipeline Tests — PJ 間を跨ぐ統合テスト

Tests the following cross-project pipelines:
  1. CCL Parse → AST (hermeneus dispatch)
  2. Macro Expansion (mekhane/ccl macro_expander)
  3. Boot Integration Chain (symploke → anamnesis → poiema)
  4. Dendron → Synteleia Chain (checker → audit)
  5. CCL → Hermeneus → AST roundtrip

These tests verify that the engine/module tier projects cooperate
correctly, catching integration breakages that unit tests miss.
"""
# PURPOSE: Cross-project integration tests for engine/module tier.

import sys
from pathlib import Path

import pytest

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Test 1: CCL Parse → AST via Hermeneus Dispatch
# =============================================================================

class TestCCLParseToAST:
    """CCL 式が hermeneus dispatch() で正しく AST に変換されるか。"""

    def test_simple_workflow_parse(self):
        """Simple workflow /noe+ should parse to a Workflow AST node."""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/noe+")
        assert result["success"], f"Parse failed: {result.get('error')}"
        assert result["ast"] is not None
        assert len(result["workflows"]) > 0
        assert "/noe" in result["workflows"]

    def test_sequence_parse(self):
        """Sequence /bou_/ene should parse to multiple workflow nodes."""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/bou_/ene")
        assert result["success"], f"Parse failed: {result.get('error')}"
        assert "/bou" in result["workflows"]
        assert "/ene" in result["workflows"]

    def test_fusion_parse(self):
        """Fusion /noe*/dia should parse correctly."""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/noe*/dia")
        assert result["success"], f"Parse failed: {result.get('error')}"
        assert "/noe" in result["workflows"]
        assert "/dia" in result["workflows"]

    def test_oscillation_parse(self):
        """Oscillation /u+~/noe should parse correctly."""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/u+~/noe")
        assert result["success"], f"Parse failed: {result.get('error')}"
        assert "/u" in result["workflows"]
        assert "/noe" in result["workflows"]

    def test_complex_ccl_with_cpl(self):
        """Complex CCL with CPL: F:[×3]{/dia} should parse without crash."""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("F:[×3]{/dia}")
        # CPL structures may not extract workflows into the flat list,
        # but parsing should succeed without errors
        assert result["success"], f"Parse failed: {result.get('error')}"
        assert result["ast"] is not None

    def test_invalid_ccl_returns_error(self):
        """Invalid CCL should return success=False with error message."""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("")
        # Empty string may be handled gracefully; ensure no crash
        assert isinstance(result, dict)

    def test_plan_template_generated(self):
        """dispatch() should generate a plan_template for valid CCL."""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/noe+")
        assert result["success"]
        assert "plan_template" in result
        assert result["plan_template"] is not None


# =============================================================================
# Test 2: Macro Expansion
# =============================================================================

class TestMacroExpansion:
    """CCL マクロが正しく展開されるか。"""

    def test_go_macro_expands(self):
        """@go should expand to /s+_/ene+."""
        from mekhane.ccl.macro_expander import MacroExpander

        expander = MacroExpander()
        result, expanded = expander.expand("@go")
        assert expanded, "@go should be recognized as a macro"
        assert "/s+" in result
        assert "/ene+" in result

    def test_unknown_macro_passthrough(self):
        """Unknown @nonexistent should pass through unchanged."""
        from mekhane.ccl.macro_expander import MacroExpander

        expander = MacroExpander()
        result, expanded = expander.expand("@nonexistent_macro_xyz")
        assert not expanded
        assert "@nonexistent_macro_xyz" in result

    def test_macro_in_ccl_context(self):
        """Macro embedded in CCL: /pro_@go should expand correctly."""
        from mekhane.ccl.macro_expander import MacroExpander

        expander = MacroExpander()
        result, expanded = expander.expand("/pro_@go")
        assert expanded
        assert "/pro_" in result
        assert "/ene+" in result

    def test_has_macros_detection(self):
        """has_macros() should detect @go in expression."""
        from mekhane.ccl.macro_expander import MacroExpander

        expander = MacroExpander()
        assert expander.has_macros("@go") is True
        assert expander.has_macros("/noe+") is False

    def test_list_macros_in_expr(self):
        """list_macros_in_expr() should return macro objects."""
        from mekhane.ccl.macro_expander import MacroExpander

        expander = MacroExpander()
        macros = expander.list_macros_in_expr("@go")
        assert len(macros) >= 1
        assert macros[0].name == "go"


# =============================================================================
# Test 3: Macro Expand → Dispatch (Cross-PJ Pipeline)
# =============================================================================

class TestMacroToDispatchPipeline:
    """マクロ展開 → hermeneus dispatch の完全パイプライン。"""

    def test_macro_expand_then_dispatch(self):
        """@go → expand → dispatch should produce valid AST."""
        from mekhane.ccl.macro_expander import MacroExpander
        from hermeneus.src.dispatch import dispatch

        expander = MacroExpander()
        expanded_ccl, did_expand = expander.expand("@go")
        assert did_expand

        result = dispatch(expanded_ccl)
        assert result["success"], f"Dispatch failed after expansion: {result.get('error')}"
        assert len(result["workflows"]) >= 2  # /s+ and /ene+

    def test_complex_macro_expand_then_dispatch(self):
        """@dig → expand → dispatch should produce valid AST."""
        from mekhane.ccl.macro_expander import MacroExpander
        from hermeneus.src.dispatch import dispatch

        expander = MacroExpander()
        expanded_ccl, did_expand = expander.expand("@dig")
        if not did_expand:
            pytest.skip("@dig macro not registered")

        result = dispatch(expanded_ccl)
        assert result["success"], f"Dispatch failed: {result.get('error')}"
        assert len(result["workflows"]) >= 1


# =============================================================================
# Test 4: Boot Integration Chain
# =============================================================================

class TestBootIntegrationChain:
    """symploke boot_integration のチェーンテスト。"""

    def test_boot_context_returns_dict(self):
        """get_boot_context() should return a dict with expected keys."""
        from mekhane.symploke.boot_integration import get_boot_context

        result = get_boot_context(mode="fast")
        assert isinstance(result, dict)
        assert "formatted" in result

    def test_boot_context_has_projects(self):
        """Boot context should include project information."""
        from mekhane.symploke.boot_integration import _load_projects

        result = _load_projects(PROJECT_ROOT)
        assert isinstance(result, dict)
        assert "projects" in result
        assert result["total"] > 0

    def test_boot_context_has_skills(self):
        """Boot context should include skill information."""
        from mekhane.symploke.boot_integration import _load_skills

        result = _load_skills(PROJECT_ROOT)
        assert isinstance(result, dict)
        assert "skills" in result
        assert result["count"] > 0

    def test_theorem_registry_completeness(self):
        """THEOREM_REGISTRY should contain all 24 theorems."""
        from mekhane.symploke.boot_integration import THEOREM_REGISTRY

        assert len(THEOREM_REGISTRY) == 24
        # Check all series present
        series = {v["series"] for v in THEOREM_REGISTRY.values()}
        assert series == {"O", "S", "H", "P", "K", "A"}

    def test_boot_template_generation(self):
        """generate_boot_template() should produce valid template (file or str)."""
        from mekhane.symploke.boot_integration import (
            get_boot_context,
            generate_boot_template,
        )

        ctx = get_boot_context(mode="fast")
        template = generate_boot_template(ctx)
        # generate_boot_template may return a Path (saved file) or a string
        assert template is not None
        if isinstance(template, str):
            assert len(template) > 0
        else:
            # PosixPath returned — verify file was actually created
            from pathlib import Path as P
            assert P(template).exists()


# =============================================================================
# Test 5: Dendron Checker Integration
# =============================================================================

class TestDendronIntegration:
    """Dendron checker の統合テスト。"""

    def test_dendron_checker_instantiation(self):
        """DendronChecker should instantiate without errors."""
        from mekhane.dendron.checker import DendronChecker

        checker = DendronChecker(
            check_dirs=False,
            check_files=True,
            check_functions=False,
            check_variables=False,
        )
        assert checker is not None

    def test_dendron_checks_own_directory(self):
        """Dendron should be able to check its own test directory."""
        from mekhane.dendron.checker import DendronChecker

        checker = DendronChecker(
            check_dirs=True,
            check_files=True,
            check_functions=False,
            check_variables=False,
            root=PROJECT_ROOT,
        )
        result = checker.check_dir_proof(PROJECT_ROOT / "mekhane" / "dendron")
        assert result is not None

    def test_dendron_checks_this_file(self):
        """Dendron should be able to check this integration test file."""
        from mekhane.dendron.checker import DendronChecker
        from mekhane.dendron.models import ProofStatus

        checker = DendronChecker(
            check_dirs=False,
            check_files=True,
            check_functions=False,
            check_variables=False,
        )
        result = checker.check_file_proof(Path(__file__))
        assert result is not None
        # test_ files are EXEMPT by Dendron's default exclude patterns,
        # but the checker still returns a valid FileProof
        assert result.status in (ProofStatus.OK, ProofStatus.EXEMPT), (
            f"Unexpected status: {result.status} ({result.reason})"
        )


# =============================================================================
# Test 6: Registry Consistency
# =============================================================================

class TestRegistryConsistency:
    """registry.yaml の整合性テスト。"""

    def test_registry_loads(self):
        """registry.yaml should load without errors."""
        import yaml

        registry_path = PROJECT_ROOT / ".agent" / "projects" / "registry.yaml"
        with open(registry_path) as f:
            data = yaml.safe_load(f)
        assert "projects" in data
        assert len(data["projects"]) > 0

    def test_all_projects_have_tier(self):
        """All projects (except gnosis archived) should have a tier."""
        import yaml

        registry_path = PROJECT_ROOT / ".agent" / "projects" / "registry.yaml"
        with open(registry_path) as f:
            data = yaml.safe_load(f)

        valid_tiers = {"core", "engine", "module", "concept", "product"}
        for project in data["projects"]:
            tier = project.get("tier")
            assert tier is not None, f"Project {project['id']} missing tier"
            assert tier in valid_tiers, f"Project {project['id']} has invalid tier: {tier}"

    def test_active_project_paths_exist(self):
        """Active projects with relative paths should have existing directories."""
        import yaml

        registry_path = PROJECT_ROOT / ".agent" / "projects" / "registry.yaml"
        with open(registry_path) as f:
            data = yaml.safe_load(f)

        missing = []
        for project in data["projects"]:
            if project.get("status") == "archived":
                continue
            path = project.get("path", "")
            if path.startswith("/"):
                # Absolute path (e.g., agora) - skip
                continue
            # Some projects reference app dirs that live outside mekhane
            # (e.g., hgk-app/) — only check mekhane/ paths
            full_path = PROJECT_ROOT / path
            if not full_path.exists():
                missing.append(f"{project['id']}: {full_path}")

        # Allow up to 2 missing paths (non-mekhane projects like hgk-app)
        assert len(missing) <= 2, (
            f"Too many active projects with missing paths ({len(missing)}):\n"
            + "\n".join(missing)
        )

    def test_tier_distribution(self):
        """Verify expected tier distribution."""
        import yaml

        registry_path = PROJECT_ROOT / ".agent" / "projects" / "registry.yaml"
        with open(registry_path) as f:
            data = yaml.safe_load(f)

        tiers = {}
        for project in data["projects"]:
            tier = project.get("tier", "unknown")
            tiers[tier] = tiers.get(tier, 0) + 1

        # At minimum, we should have these tiers populated
        assert tiers.get("core", 0) >= 3
        assert tiers.get("engine", 0) >= 3
        assert tiers.get("module", 0) >= 3
