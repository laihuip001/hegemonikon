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
ROOT_DIR = Path(__file__).resolve().parents[3]
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
def is_safe_path(target_path: Path, base_dir: Path) -> bool:
    """
    Check if target_path is within base_dir, handling Windows drive/case issues.
    """
    # 1. Simple check (fast path)
    if hasattr(target_path, "is_relative_to"):  # Python 3.9+
        if target_path.is_relative_to(base_dir):
            return True
    else:
        try:
            target_path.relative_to(base_dir)
            return True
        except ValueError:
            pass

    # 2. Resolved check
    t_res = target_path.resolve()
    b_res = base_dir.resolve()

    if hasattr(t_res, "is_relative_to"):
        if t_res.is_relative_to(b_res):
            return True
    else:
        try:
            t_res.relative_to(b_res)
            return True
        except ValueError:
            pass

    # 3. Case-insensitive string check (Windows specific fallback)
    t_str = str(t_res).lower().replace('\\', '/')
    b_str = str(b_res).lower().replace('\\', '/')

    if not b_str.endswith('/'):
        b_str_slash = b_str + '/'
    else:
        b_str_slash = b_str

    if t_str == b_str or t_str.startswith(b_str_slash):
        return True

    return False


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
        
        # Check if path is safe (inside repo)
        if not is_safe_path(target_path, ROOT_DIR):
            results.append(CheckResult(
                name=f"Link: {link_target}",
                passed=False,
                message=f"Unsafe link in {file_path.name}: {link_target} (points outside repo)"
            ))
            continue
        
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

# --- Structure Scan ---
def generate_tree(dir_path: Path, prefix: str = "", is_last: bool = False, is_root: bool = False, current_depth: int = 0, max_depth: int = 4) -> str:
    """Recursively generate directory tree string."""
    output = ""
    if not is_root:
        connector = "└── " if is_last else "├── "
        output += f"{prefix}{connector}{dir_path.name}"
        if dir_path.is_file():
             pass
        elif current_depth >= max_depth:
            output += "/ ...\n"
            return output
        output += "\n"
        
    if dir_path.is_file():
        return output
        
    # Prepare prefix for children
    if is_root:
        new_prefix = prefix
    else:
        new_prefix = prefix + ("    " if is_last else "│   ")
        
    # Get children
    try:
        children = sorted(list(dir_path.iterdir()), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return output
        
    # Filter ignored files
    filtered = []
    ignores = {".git", "__pycache__", ".DS_Store", "node_modules", ".logb", "wandb", ".github", "archive"}
    for child in children:
        if child.name in ignores or child.name.endswith(".pyc") or child.name.endswith(".txn"):
            continue
        filtered.append(child)
        
    count = len(filtered)
    for i, child in enumerate(filtered):
        is_last_child = (i == count - 1)
        output += generate_tree(child, new_prefix, is_last_child, False, current_depth + 1, max_depth)
        
    return output

def scan_structure() -> bool:
    """Update docs/STRUCTURE.md with current directory tree."""
    print("Scanning directory structure...")
    
    # Generate Tree with max_depth=3 for cleanliness
    # .agent/rules etc will be shown but deeply nested files omitted
    tree_content = "M:\\Hegemonikon\\\n" + generate_tree(ROOT_DIR, is_root=True, max_depth=3)
    
    # Wrap in code block
    tree_block = "```text\n" + tree_content.strip() + "\n```"
    
    # 2. Update File
    struct_file = DOCS_DIR / "STRUCTURE.md"
    if not struct_file.exists():
        print(f"❌ Error: {struct_file} not found.")
        return False
        
    content = struct_file.read_text(encoding="utf-8")
    
    pattern = re.compile(
        r"(<!-- STRUCTURE_START -->\n)(.*?)(<!-- STRUCTURE_END -->)", 
        re.DOTALL
    )
    
    if not pattern.search(content):
        print("❌ Error: Structure markers not found in docs/STRUCTURE.md")
        return False
        
    # Fix for Windows paths in regex substitution: escape backslashes
    replacement = tree_block.replace("\\", "\\\\")
    new_content = pattern.sub(f"\\1{replacement}\n\\3", content)
    
    if content != new_content:
        struct_file.write_text(new_content, encoding="utf-8")
        print("✅ Directory tree updated in docs/STRUCTURE.md")
    else:
        print("✅ Directory tree is up to date.")
        
    return True

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "verify":
            success = verify_all()
            sys.exit(0 if success else 1)
        elif cmd == "scan-structure":
            success = scan_structure()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    else:
        print("Usage: python doc_maintenance.py [verify|scan-structure]")
        sys.exit(1)
