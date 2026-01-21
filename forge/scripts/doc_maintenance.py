"""
Module: doc_maintenance.py
Description: Automated maintenance for AI-optimized documentation (AGENTS.md, etc.)

Part of Hegemonikón Forge layer.
"""

from __future__ import annotations

import sys
import re
from pathlib import Path
from typing import NamedTuple

# --- Constants ---
ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / "docs"

CRITICAL_FILES = [
    "AGENTS.md",
    "llms.txt",
    "docs/STRUCTURE.md",
    "docs/ARCHITECTURE.md",
    ".ai/guidelines.md"
]

# --- Classes ---
class CheckResult(NamedTuple):
    name: str
    passed: bool
    message: str

# --- Functions ---
def check_critical_files() -> list[CheckResult]:
    """Verify existence of critical documentation files."""
    results = []
    print("Checking critical files...")
    for rel_path in CRITICAL_FILES:
        path = ROOT_DIR / rel_path
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {rel_path}")
        
        results.append(CheckResult(
            name=f"Exist: {rel_path}",
            passed=exists,
            message=f"Missing file: {rel_path}" if not exists else "OK"
        ))
    return results

def check_link_validity(file_path: Path) -> list[CheckResult]:
    """Verify local links in a markdown file."""
    results = []
    if not file_path.exists():
        return [CheckResult(f"LinkCheck: {file_path.name}", False, "File not found")]

    print(f"Checking links in {file_path.name}...")
    content = file_path.read_text(encoding="utf-8")
    
    # Match markdown links: [text](path)
    # Ignore http/https links
    link_pattern = re.compile(r'\[.*?\]\((?!http)(.*?)\)')
    
    for match in link_pattern.finditer(content):
        link_target = match.group(1).split('#')[0] # Ignore anchors
        if not link_target:
            continue
            
        target_path = (file_path.parent / link_target).resolve()
        
        target_path = (file_path.parent / link_target).resolve()
        
        # Note: Skipped strict relative_to(ROOT_DIR) check due to Windows drive mapping issues
        
        exists = target_path.exists()
        status = "✅" if exists else "❌"
        # print(f"  {status} {link_target}") # Verbose
        
        if not exists:
            results.append(CheckResult(
                name=f"Link: {link_target}",
                passed=False,
                message=f"Broken link in {file_path.name}: {link_target}"
            ))
            
    return results

def verify_all() -> bool:
    """Run all verification checks."""
    all_results = []
    
    # 1. Existence Check
    all_results.extend(check_critical_files())
    
    # 2. Link Check (llms.txt only for now)
    all_results.extend(check_link_validity(ROOT_DIR / "llms.txt"))
    
    # Report
    print("\n=== Verification Summary ===")
    failures = [r for r in all_results if not r.passed]
    
    if failures:
        print(f"\n❌ FAILED: {len(failures)} issues found.")
        for f in failures:
            print(f"  - {f.message}")
        return False
    else:
        print("\n✅ PASSED: All checks passed.")
        return True

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        success = verify_all()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python doc_maintenance.py verify")
        sys.exit(1)
