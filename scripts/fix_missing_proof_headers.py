#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/fix_missing_proof_headers.py A0→AutoFix
# PURPOSE: 欠落した # PROOF: ヘッダを Python ファイルに自動付与する
"""
Batch-add missing `# PROOF:` headers to Python files in `mekhane/`.

This script iterates over Python files, checks for the presence of `# PROOF:`,
and if missing, inserts a default header based on the file path.

Usage:
    python scripts/fix_missing_proof_headers.py
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def get_category_from_path(path: Path) -> str:
    """Path から PROOF カテゴリを推定"""
    parts = path.parts
    if "dendron" in parts:
        return "[L2/Quality]"
    if "symploke" in parts:
        return "[L2/Infra]"
    if "basanos" in parts:
        return "[L2/Test]"
    if "pks" in parts:
        return "[L2/PKS]"
    if "periskope" in parts:
        return "[L2/Periskope]"
    if "ccl" in parts:
        return "[L1/CCL]"
    if "ochema" in parts:
        return "[L2/Ochema]"
    if "api" in parts:
        return "[L2/API]"
    if "mcp" in parts:
        return "[L2/MCP]"
    return "[L2/Mekhane]"

def fix_file(file_path: Path):
    """ファイルに PROOF ヘッダを追加"""
    try:
        content = file_path.read_text(encoding="utf-8")
        if "# PROOF:" in content:
            return

        category = get_category_from_path(file_path)
        rel_path = file_path.relative_to(PROJECT_ROOT)
        header = f"# PROOF: {category} <- {rel_path} A0→AutoFix"

        # Shebang がある場合はその直後に挿入
        lines = content.splitlines()
        if lines and lines[0].startswith("#!"):
            lines.insert(1, header)
        else:
            lines.insert(0, header)

        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"✅ Added PROOF to: {rel_path}")
    except Exception as e:
        print(f"❌ Failed to fix {file_path}: {e}")

def main():
    target_dir = PROJECT_ROOT / "mekhane"
    print(f"Scanning {target_dir} for missing PROOF headers...")

    count = 0
    for py_file in target_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue # Skip __init__.py often handled differently or strict check ignored

        content = py_file.read_text(encoding="utf-8")
        if "# PROOF:" not in content:
            fix_file(py_file)
            count += 1

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
