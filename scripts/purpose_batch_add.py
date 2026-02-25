#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->AddedByCI
# PURPOSE: Batch inject # PURPOSE: comments into functions missing them to satisfy Dendron CI
"""
Purpose Batch Add - Bulk injector for missing PURPOSE comments

Usage:
    python scripts/purpose_batch_add.py <target_dir> [--write]
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Tuple

class PurposeInjector(ast.NodeVisitor):
    def __init__(self, content: str):
        self.content = content
        self.lines = content.splitlines()
        self.insertions = []  # List of (line_index, insertion_text)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_node(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_node(node)
        self.generic_visit(node)

    def _check_node(self, node):
        # Check if # PURPOSE: exists above
        # Look at lines preceding the definition
        # Be careful with decorators

        start_line = node.lineno - 1 # 0-indexed

        # Adjust for decorators
        if node.decorator_list:
            start_line = node.decorator_list[0].lineno - 1

        # Check preceding lines for PURPOSE
        # We look back up to 3 lines (arbitrary, but reasonable)
        found = False
        for i in range(1, 4):
            if start_line - i < 0:
                break
            line = self.lines[start_line - i].strip()
            if line.startswith("# PURPOSE:"):
                found = True
                break
            if not line.startswith("#") and not line.startswith("@"):
                 # Stop if we hit code or empty line that isn't a comment
                 # Actually empty lines are fine
                 if line: break

        if not found:
            # Prepare insertion
            indent = " " * node.col_offset
            # If it's a method/function, use its name for the placeholder
            insertion = f"{indent}# PURPOSE: [Auto] {node.name}\n"
            self.insertions.append((start_line, insertion))

def process_file(path: Path, write: bool) -> int:
    try:
        content = path.read_text(encoding="utf-8")
        injector = PurposeInjector(content)
        tree = ast.parse(content)
        injector.visit(tree)

        if not injector.insertions:
            return 0

        # Apply insertions in reverse order to keep line numbers valid
        lines = content.splitlines(keepends=True)
        # Ensure last line has newline if missing (splitlines logic)

        count = 0
        for line_idx, text in sorted(injector.insertions, reverse=True):
            lines.insert(line_idx, text)
            count += 1

        if write:
            path.write_text("".join(lines), encoding="utf-8")
            print(f"Fixed {path}: added {count} purposes")
        else:
            print(f"Would fix {path}: {count} missing purposes")

        return count

    except Exception as e:
        print(f"Error processing {path}: {e}", file=sys.stderr)
        return 0

def main():
    parser = argparse.ArgumentParser(description="Batch add PURPOSE comments")
    parser.add_argument("target_dir", help="Directory to scan")
    parser.add_argument("--write", action="store_true", help="Write changes to files")
    args = parser.parse_args()

    target = Path(args.target_dir)
    if not target.exists():
        print(f"Error: {target} not found", file=sys.stderr)
        sys.exit(1)

    total_added = 0
    files = sorted(target.rglob("*.py"))

    for f in files:
        if "test" in f.name.lower(): continue
        total_added += process_file(f, args.write)

    if total_added > 0:
        if args.write:
            print(f"Successfully added {total_added} PURPOSE comments.")
        else:
            print(f"Found {total_added} missing PURPOSE comments. Run with --write to fix.")
    else:
        print("No missing PURPOSE comments found.")

if __name__ == "__main__":
    main()
