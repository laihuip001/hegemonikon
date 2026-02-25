#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/ A0→Implementation→bump_version
"""
bump_version.py — Markdown Frontmatter Version Bumper

Usage:
    python scripts/bump_version.py <path> --part {major,minor,patch}
    python scripts/bump_version.py <path> --set "1.2.3"

Safety:
    - Creates backup (.bak) before modification.
    - Preserves comments (uses regex instead of yaml dump).
"""

import argparse
import re
import shutil
import sys
from pathlib import Path
from packaging.version import Version

def parse_args():
    parser = argparse.ArgumentParser(description="Bump version in markdown frontmatter")
    parser.add_argument("path", type=Path, help="Path to markdown file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--part", choices=["major", "minor", "patch"], help="Bump part")
    group.add_argument("--set", dest="set_version", help="Set explicit version")
    return parser.parse_args()

def bump_part(current_ver: str, part: str) -> str:
    try:
        v = Version(current_ver)
    except Exception:
        # Fallback for simple parsing if packaging fails or non-standard
        # Assuming x.y.z
        pts = current_ver.split(".")
        if len(pts) < 3:
            pts.extend(["0"] * (3 - len(pts)))
        v_nums = [int(p) if p.isdigit() else 0 for p in pts]
    else:
        v_nums = [v.major, v.minor, v.micro]

    if part == "major":
        v_nums[0] += 1
        v_nums[1] = 0
        v_nums[2] = 0
    elif part == "minor":
        v_nums[1] += 1
        v_nums[2] = 0
    elif part == "patch":
        v_nums[2] += 1
    
    return f"{v_nums[0]}.{v_nums[1]}.{v_nums[2]}"

def main():
    args = parse_args()
    target_path = args.path.resolve()

    if not target_path.exists():
        print(f"Error: File not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    content = target_path.read_text(encoding="utf-8")
    
    # Regex to find version: "x.y.z" or version: x.y.z
    # Non-greedy match inside frontmatter?
    # Frontmatter is between first two ---
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print("Error: No frontmatter found", file=sys.stderr)
        sys.exit(1)
    
    fm_content = match.group(1)
    # Look for 'version: ...'
    v_pattern = re.compile(r'^version:\s*["\']?([0-9a-zA-Z\.]+)["\']?\s*$', re.MULTILINE)
    v_match = v_pattern.search(fm_content)
    
    if not v_match:
        print("Error: 'version' field not found in frontmatter", file=sys.stderr)
        sys.exit(1)
    
    current_ver = v_match.group(1)
    print(f"Current version: {current_ver}")
    
    if args.set_version:
        new_ver = args.set_version
    else:
        new_ver = bump_part(current_ver, args.part)
    
    print(f"New version:     {new_ver}")
    
    # Backup
    backup_path = target_path.with_suffix(".md.bak")
    shutil.copy2(target_path, backup_path)
    print(f"Backup saved to: {backup_path}")
    
    # Replace in content
    # We replace the *captured group* range in original string?
    # Or just replace usage of regex.
    # Be careful not to replace 'min_version' if regex is loose.
    # Pattern ^version ensures keys starting with version.
    
    # Safer replacement:
    new_fm = v_pattern.sub(f'version: "{new_ver}"', fm_content, count=1)
    
    # Reconstruct content
    new_content = content.replace(f"---\n{fm_content}\n---", f"---\n{new_fm}\n---", 1)
    
    target_path.write_text(new_content, encoding="utf-8")
    print(f"Updated {target_path}")

if __name__ == "__main__":
    main()
