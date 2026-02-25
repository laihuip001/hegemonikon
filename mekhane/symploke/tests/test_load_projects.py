#!/usr/bin/env python3
# PROOF: [L2/品質] <- mekhane/symploke/tests/boot_integration の最適化検証
"""Test for _load_projects function in boot_integration.py."""

import sys
import tempfile
import yaml
from pathlib import Path

# Add project root to path (assuming mekhane/symploke/tests is 3 levels deep from root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mekhane.symploke.boot_integration import _load_projects

def test_load_projects_optimization():
    """Verify that _load_projects correctly loads and categorizes projects."""
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        registry_dir = root / ".agent" / "projects"
        registry_dir.mkdir(parents=True)

        projects_data = {
            "projects": [
                {
                    "id": "mekhane",
                    "name": "Mekhane",
                    "status": "active",
                    "path": "mekhane/api",
                    "phase": "Phase 5",
                    "summary": "Core system"
                },
                {
                    "id": "ccl",
                    "name": "CCL",
                    "status": "active",
                    "path": "ccl/parser",
                    "phase": "Phase 3",
                    "summary": "Language foundation"
                },
                {
                    "id": "old_stuff",
                    "name": "Old Stuff",
                    "status": "archived",
                    "path": "old/",
                    "phase": "Archived",
                    "summary": "Legacy code"
                },
                {
                    "id": "dormant_stuff",
                    "name": "Dormant Stuff",
                    "status": "dormant",
                    "path": "dormant/",
                    "phase": "Paused",
                    "summary": "Sleeping"
                },
            ]
        }

        registry_file = registry_dir / "registry.yaml"
        with open(registry_file, "w", encoding="utf-8") as f:
            yaml.dump(projects_data, f)

        result = _load_projects(root)

        # Verify counts
        assert result["total"] == 4, f"Expected total 4, got {result['total']}"
        assert result["active"] == 2, f"Expected active 2, got {result['active']}"
        assert result["dormant"] == 1, f"Expected dormant 1, got {result['dormant']}"

        # Verify projects list integrity
        assert len(result["projects"]) == 4

        # Verify categories (implied by formatted output)
        formatted = result["formatted"]
        print(formatted) # For debug if test fails

        assert "Mekhane" in formatted
        assert "CCL" in formatted
        assert "Old Stuff" in formatted
        assert "Dormant Stuff" in formatted

        # Check categories headings
        assert "[Mekhane モジュール]" in formatted
        assert "[理論・言語基盤]" in formatted
        assert "[補助]" in formatted

        # Check summary line
        assert "Active 2 / Dormant 1 / Archived 1" in formatted

if __name__ == "__main__":
    try:
        test_load_projects_optimization()
        print("Test passed!")
    except ImportError:
        print("Could not import dependencies, environment might be missing PyYAML")
        sys.exit(1)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
