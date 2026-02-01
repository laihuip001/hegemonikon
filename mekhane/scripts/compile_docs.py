# PROOF: [L3/ユーティリティ] O4→運用スクリプトが必要→compile_docs が担う
import os
from pathlib import Path

# Configuration
SOURCE_ROOT = Path("M:/Hegemonikon")
OUTPUT_FILE = SOURCE_ROOT / "hegemonikon_full_docs.txt"

# Ignore these directories and patterns
IGNORE_DIRS = {
    "node_modules",
    "Raw",
    "archive",
    "runtime",
    ".git",
    ".gemini",
    ".history",
    "__pycache__",
    "site-packages",
}

# Only include markdown files
INCLUDE_EXTS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
}  # Added config files for context if needed, but stick to MD per request?
# User said "Main documents", option 3 was "All Markdown files". Let's stick to .md and important configs.
STRICT_EXTS = {".md"}


def main():
    print(f"📦 Scanning {SOURCE_ROOT}...")

    files_collected = []

    for root, dirs, files in os.walk(SOURCE_ROOT):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        # Also skip specific exclusion patterns if 'node_modules' is in the path just in case
        if any(ignored in Path(root).parts for ignored in IGNORE_DIRS):
            continue

        for file in files:
            if Path(file).suffix.lower() in STRICT_EXTS:
                full_path = Path(root) / file
                files_collected.append(full_path)

    print(f"📄 Found {len(files_collected)} files. Compiling...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Write Header
        outfile.write(f"# HEGEMONIKON FULL DOCUMENTATION DUMP\n")
        outfile.write(f"# Generated: {os.path.basename(__file__)}\n")
        outfile.write(f"# Root: {SOURCE_ROOT}\n")
        outfile.write(f"# Files: {len(files_collected)}\n")
        outfile.write("=" * 80 + "\n\n")

        for fpath in sorted(files_collected):
            try:
                rel_path = fpath.relative_to(SOURCE_ROOT)
                content = fpath.read_text(encoding="utf-8", errors="replace")

                outfile.write(f"\n\n{'='*80}\n")
                outfile.write(f"FILE_PATH: {rel_path}\n")
                outfile.write(f"{'='*80}\n\n")
                outfile.write(content)
                print(f"  + Added: {rel_path}")

            except Exception as e:
                print(f"  ! Error reading {fpath}: {e}")
                outfile.write(f"\n[ERROR READING FILE: {fpath} - {e}]\n")

    print(f"\n✅ Compilation Complete!")
    print(f"📁 Output: {OUTPUT_FILE}")
    print(f"📊 Total Size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
