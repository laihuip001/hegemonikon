#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/synedrion/ AI Auditor 抑制コメント自動挿入
"""Auto-insert # noqa suppression comments for AI Auditor findings."""

import re
from pathlib import Path


# PURPOSE: Parse auditor output file
def parse_audit_file(audit_file: Path) -> dict[str, list[tuple[int, str]]]:
    """Parse auditor output file.

    Returns: dict mapping file name to list of (line_number, issue_code)
    """
    findings: dict[str, list[tuple[int, str]]] = {}
    current_file = None

    content = audit_file.read_text(encoding="utf-8")

    for line in content.splitlines():
        # Detect file header (## filename.py)
        if line.startswith("## ") and line.endswith(".py"):
            current_file = line[3:].strip()
        # Detect issue line (- ⚪ **AI-XXX** LNNN: ...)
        elif current_file and "**AI-" in line:
            match = re.search(r"\*\*AI-(\d+)\*\* L(\d+):", line)
            if match:
                code = f"AI-{match.group(1)}"
                line_num = int(match.group(2))
                if current_file not in findings:
                    findings[current_file] = []
                findings[current_file].append((line_num, code))

    return findings


# PURPOSE: Find a file by name in the directory tree
def find_file(file_name: str, base_dir: Path) -> Path | None:
    """Find a file by name in the directory tree."""
    # Try direct path first
    if (base_dir / file_name).exists():
        return base_dir / file_name

    # Search recursively
    for path in base_dir.rglob(file_name):
        return path

    return None


# PURPOSE: Insert # noqa comments for the given issues
def insert_noqa(file_path: Path, issues: list[tuple[int, str]]):
    """Insert # noqa comments for the given issues."""
    if not file_path.exists():
        print(f"  [SKIP] {file_path} not found")
        return 0

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    modified = False
    updated_count = 0

    # Group issues by line
    by_line: dict[int, set[str]] = {}
    for line_num, code in issues:
        if line_num not in by_line:
            by_line[line_num] = set()
        by_line[line_num].add(code)

    for line_num, codes in by_line.items():
        if line_num < 1 or line_num > len(lines):
            continue

        idx = line_num - 1
        line = lines[idx].rstrip("\n\r")

        # Skip if already has noqa
        if "# noqa" in line or "# auditor: ignore" in line:
            continue

        # Add noqa comment
        codes_str = ", ".join(sorted(codes))
        lines[idx] = f"{line}  # noqa: {codes_str}\n"
        modified = True
        updated_count += 1

    if modified:
        file_path.write_text("".join(lines), encoding="utf-8")
        print(
            f"  [OK] {file_path.relative_to(file_path.parents[3])} - {updated_count} lines"
        )

    return updated_count


# PURPOSE: main の処理
def main():
    base_dir = Path("/home/makaron8426/oikos/hegemonikon/mekhane")
    audit_file = Path("/tmp/audit_output.txt")

    if not audit_file.exists():
        print("No audit output file found. Run auditor first.")
        return

    print("Parsing audit output...")
    findings = parse_audit_file(audit_file)

    print(f"Found issues in {len(findings)} files")
    print("\nInserting # noqa comments...")

    total_lines = 0
    found_files = 0
    for file_name, issues in findings.items():
        file_path = find_file(file_name, base_dir)
        if file_path:
            lines_updated = insert_noqa(file_path, issues)
            total_lines += lines_updated
            if lines_updated > 0:
                found_files += 1
        else:
            print(f"  [SKIP] {file_name} not found in tree")

    print(f"\nTotal: {total_lines} lines updated in {found_files} files")
    print("Run auditor again to verify.")


if __name__ == "__main__":
    main()
