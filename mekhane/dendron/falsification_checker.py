# PROOF: [L2/Infra] <- mekhane/dendron/
"""
S7: Falsification Condition Checker

PURPOSE: epistemic_status.yaml に登録された反証条件を自動チェックし、
無効化されるべき主張がないか警告する。

現時点では YAML の整合性チェック + 反証条件の完全性検証を実行。
将来的に: 新論文の消化時に反証条件とのマッチングを自動化する。
"""

import sys
from pathlib import Path

import yaml


# Project root (hegemonikon/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = PROJECT_ROOT / "kernel" / "epistemic_status.yaml"


def load_registry() -> dict:
    """Load the epistemic status registry"""
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found: {REGISTRY_PATH}")
        sys.exit(1)
    
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_completeness(registry: dict) -> list[str]:
    """Check that all patches have required fields"""
    issues = []
    patches = registry.get("patches", {})
    
    required_fields = ["file", "claim", "source", "status", "falsification"]
    valid_statuses = {"empirical", "reference", "analogue", "hypothesis"}
    
    for patch_id, patch in patches.items():
        for field in required_fields:
            if field not in patch or not patch[field]:
                issues.append(f"❌ {patch_id}: missing '{field}'")
        
        status = patch.get("status", "")
        if status not in valid_statuses:
            issues.append(f"⚠️ {patch_id}: invalid status '{status}' (valid: {valid_statuses})")
        
        # Check that the referenced file exists
        file_path = PROJECT_ROOT / patch.get("file", "")
        if patch.get("file") and not file_path.exists():
            issues.append(f"⚠️ {patch_id}: file not found '{patch['file']}'")
    
    return issues


def check_file_references(registry: dict) -> list[str]:
    """Verify that claims exist in referenced files at specified lines"""
    issues = []
    patches = registry.get("patches", {})
    
    for patch_id, patch in patches.items():
        file_path = PROJECT_ROOT / patch.get("file", "")
        line_num = patch.get("line")
        
        if not file_path.exists() or not line_num:
            continue
        
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
            if line_num > len(lines):
                issues.append(f"⚠️ {patch_id}: line {line_num} exceeds file length ({len(lines)})")
            else:
                # Check if the line contains anything related to the claim
                context = "\n".join(lines[max(0, line_num-3):line_num+3])
                source = patch.get("source", "")
                # Try multiple matching strategies for source name
                source_parts = [
                    source.split("(")[0].strip(),  # Before parentheses
                    source.split("&")[0].strip(),   # Before ampersand
                    source.split(",")[0].strip(),   # Before comma
                ]
                found = any(
                    part and part.lower() in context.lower()
                    for part in source_parts
                    if len(part) > 3  # Skip very short fragments
                )
                if not found:
                    issues.append(
                        f"ℹ️ {patch_id}: source '{source}' not found near line {line_num} "
                        f"(may have shifted)"
                    )
        except Exception as e:
            issues.append(f"❌ {patch_id}: error reading file: {e}")
    
    return issues


def summary_stats(registry: dict) -> dict:
    """Generate summary statistics"""
    patches = registry.get("patches", {})
    status_counts = {}
    for patch in patches.values():
        s = patch.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
    return {
        "total_patches": len(patches),
        "status_distribution": status_counts,
    }


def main():
    registry = load_registry()
    
    print("=" * 60)
    print("S7: Falsification Condition Check")
    print("=" * 60)
    
    # Stats
    stats = summary_stats(registry)
    print(f"\nTotal patches: {stats['total_patches']}")
    print(f"Status distribution: {stats['status_distribution']}")
    
    # Completeness check
    print("\n--- Completeness Check ---")
    comp_issues = check_completeness(registry)
    if comp_issues:
        for issue in comp_issues:
            print(f"  {issue}")
    else:
        print("  ✅ All patches have required fields")
    
    # File reference check
    print("\n--- File Reference Check ---")
    ref_issues = check_file_references(registry)
    if ref_issues:
        for issue in ref_issues:
            print(f"  {issue}")
    else:
        print("  ✅ All file references valid")
    
    # Overall
    total_issues = len(comp_issues) + len(ref_issues)
    print(f"\n{'✅' if total_issues == 0 else '⚠️'} Total issues: {total_issues}")
    
    return total_issues


if __name__ == "__main__":
    sys.exit(main())
