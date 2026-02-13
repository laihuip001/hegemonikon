#!/usr/bin/env python3
"""Tests for boot_integration template generation and postcheck."""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.boot_integration import (
    MODE_REQUIREMENTS,
    generate_boot_template,
    postcheck_boot_report,
)


def _make_mock_result(handoff_count: int = 3, ki_count: int = 2) -> dict:
    """Create mock boot context result for testing."""
    handoffs = []
    for i in range(handoff_count):
        handoffs.append({
            "primary_task": f"Test Handoff Task {i+1}",
            "title": f"handoff_{i+1}.md",
        })

    ki_items = []
    for i in range(ki_count):
        ki_items.append({
            "ki_name": f"KI-{i+1:03d}",
            "summary": f"Summary of knowledge item {i+1} covering topic X and topic Y",
        })

    return {
        "handoffs": {
            "latest": handoffs[0] if handoffs else None,
            "related": handoffs[1:] if len(handoffs) > 1 else [],
            "count": handoff_count,
        },
        "ki": {
            "ki_items": ki_items,
            "count": ki_count,
        },
        "persona": {"sessions": 42},
        "pks": {"count": 0, "formatted": ""},
        "safety": {"errors": 0, "formatted": ""},
        "digestor": {"count": 0, "formatted": ""},
        "attractor": {"series": [], "formatted": ""},
        "formatted": "",
    }


# PURPOSE: Template generation tests
class TestGenerateBootTemplate:
    """Template generation tests."""

    # PURPOSE: template_creates_file をテストする
    def test_template_creates_file(self):
        """Verify template creates file behavior."""
        result = _make_mock_result(handoff_count=10, ki_count=5)
        path = generate_boot_template(result)
        assert path.exists(), f"Template file not created: {path}"
        content = path.read_text(encoding="utf-8")
        assert "# Boot Report" in content
        path.unlink()

    # PURPOSE: template_has_fill_markers をテストする
    def test_template_has_fill_markers(self):
        """Verify template has fill markers behavior."""
        result = _make_mock_result(handoff_count=10, ki_count=5)
        path = generate_boot_template(result)
        content = path.read_text(encoding="utf-8")
        fill_count = content.count("<!-- FILL -->")
        assert fill_count > 0, "No FILL markers in template"
        path.unlink()

    # PURPOSE: template_has_required_markers をテストする
    def test_template_has_required_markers(self):
        """Verify template has required markers behavior."""
        result = _make_mock_result(handoff_count=10, ki_count=5)
        path = generate_boot_template(result)
        content = path.read_text(encoding="utf-8")
        required_count = content.count("<!-- REQUIRED")
        expected = len(MODE_REQUIREMENTS["detailed"]["required_sections"])
        assert required_count >= expected, (
            f"REQUIRED markers {required_count} < expected {expected}"
        )
        path.unlink()

    # PURPOSE: template_has_handoff_sections をテストする
    def test_template_has_handoff_sections(self):
        """Verify template has handoff sections behavior."""
        result = _make_mock_result(handoff_count=10, ki_count=5)
        path = generate_boot_template(result)
        content = path.read_text(encoding="utf-8")
        import re
        handoff_sections = len(re.findall(r"^### Handoff \d+:", content, re.MULTILINE))
        assert handoff_sections == 10, f"Expected 10 Handoff sections, got {handoff_sections}"
        path.unlink()

    # PURPOSE: When fewer than 5 KIs are available, create placeholders
    def test_template_fills_ki_placeholders(self):
        """When fewer than 5 KIs are available, create placeholders."""
        result = _make_mock_result(handoff_count=2, ki_count=2)
        path = generate_boot_template(result)
        content = path.read_text(encoding="utf-8")
        import re
        ki_sections = len(re.findall(r"^### KI \d+:", content, re.MULTILINE))
        assert ki_sections == 5, f"Expected 5 KI sections (2 real + 3 placeholder), got {ki_sections}"
        path.unlink()

    # PURPOSE: template_has_checklist をテストする
    def test_template_has_checklist(self):
        """Verify template has checklist behavior."""
        result = _make_mock_result()
        path = generate_boot_template(result)
        content = path.read_text(encoding="utf-8")
        assert "- [ ]" in content, "No checklist items in template"
        path.unlink()


# PURPOSE: Postcheck validation tests
class TestPostcheckBootReport:
    """Postcheck validation tests."""

    # PURPOSE: missing_file_fails をテストする
    def test_missing_file_fails(self):
        """Verify missing file fails behavior."""
        result = postcheck_boot_report("/tmp/nonexistent_boot_report.md", mode="detailed")
        assert not result["passed"]
        assert "File not found" in result["formatted"]

    # PURPOSE: A raw template with FILL markers should FAIL
    def test_unfilled_template_fails(self):
        """A raw template with FILL markers should FAIL."""
        mock_result = _make_mock_result(handoff_count=10, ki_count=5)
        path = generate_boot_template(mock_result)
        result = postcheck_boot_report(str(path), mode="detailed")
        assert not result["passed"], "Raw template should FAIL postcheck"
        # Verify unfilled_sections check fails
        unfilled_check = next(c for c in result["checks"] if c["name"] == "unfilled_sections")
        assert not unfilled_check["passed"], "Unfilled sections should be detected"
        path.unlink()

    # PURPOSE: A fully filled template should PASS all checks
    def test_filled_template_passes(self):
        """A fully filled template should PASS all checks."""
        mock_result = _make_mock_result(handoff_count=10, ki_count=5)
        path = generate_boot_template(mock_result)
        content = path.read_text(encoding="utf-8")

        # Fill all markers
        content = content.replace("<!-- FILL -->", "This section has been filled with meaningful content.")
        # Mark all checklist items as done
        content = content.replace("- [ ]", "- [x]")
        # Add Intent-WAL section (required for /boot and /boot+ postcheck)
        content += "\n## Intent-WAL\nintent_wal:\n  session_goal: Test implementation of security fixes\n"
        # Pad to meet min_chars
        while len(content) < MODE_REQUIREMENTS["detailed"]["min_chars"]:
            content += "\nAdditional content to meet minimum character requirements."

        path.write_text(content, encoding="utf-8")
        result = postcheck_boot_report(str(path), mode="detailed")

        for check in result["checks"]:
            print(f"  {'✅' if check['passed'] else '❌'} {check['detail']}")

        assert result["passed"], f"Filled template should PASS: {result['formatted']}"
        path.unlink()

    # PURPOSE: Standard mode should have lower requirements than detailed
    def test_standard_mode_has_lower_requirements(self):
        """Standard mode should have lower requirements than detailed."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            # Content that passes standard (6 required sections)
            content = "# Boot Report\n\n"
            content += "## Handoff サマリー\n<!-- REQUIRED: Handoff -->\n\n"
            content += "### Handoff 1: Task A\n> Summary of task A.\n\n"
            content += "### Handoff 2: Task B\n> Summary of task B.\n\n"
            content += "### Handoff 3: Task C\n> Summary of task C.\n\n"
            content += "## 開発中プロジェクト\n<!-- REQUIRED: Projects -->\n\n"
            content += "| PJ | Status |\n|---|---|\n| Agora | 🟢 |\n\n"
            content += "## Safety\n<!-- REQUIRED: Safety -->\n\n"
            content += "Errors: 4, Warnings: 65\n\n"
            content += "## EPT\n<!-- REQUIRED: EPT -->\n\n"
            content += "Coverage: 83%\n\n"
            content += "## Quota\n<!-- REQUIRED: Quota -->\n\n"
            content += "Prompt: 100%, Flow: 100%\n\n"
            content += "## タスク提案\n<!-- REQUIRED: tasks -->\n\n"
            content += "1. Do task X\n2. Do task Y\n"
            # Pad to 1000+ chars
            while len(content) < 1100:
                content += "\nExtra content for minimum length."
            f.write(content)
            f.flush()

            result = postcheck_boot_report(f.name, mode="standard")
            # Standard should check fewer requirements
            assert len(result["checks"]) == 7  # +1 for intent_wal check
            Path(f.name).unlink()

    # PURPOSE: Fast mode has minimal requirements
    def test_fast_mode_passes_easily(self):
        """Fast mode has minimal requirements."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("# Boot Report\n\n- [x] Done\n")
            f.flush()
            result = postcheck_boot_report(f.name, mode="fast")
            # Fast mode: unfilled=0 (pass), required=0/0 (pass), chars=0 (pass),
            # handoff=0 (pass), checklist=1/1 (pass)
            assert result["passed"], f"Fast mode should pass easily: {result['formatted']}"
            Path(f.name).unlink()


# PURPOSE: Run all tests and report results
def run_tests():
    """Run all tests and report results."""
    import traceback

    test_classes = [TestGenerateBootTemplate, TestPostcheckBootReport]
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
