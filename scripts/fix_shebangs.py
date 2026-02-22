import os
from pathlib import Path

MEKHANE_ROOT = Path("mekhane")

def fix_shebangs():
    count = 0
    for root, dirs, files in os.walk(MEKHANE_ROOT):
        for file in files:
            if not file.endswith(".py"):
                continue

            path = Path(root) / file
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue

            lines = content.splitlines()
            if len(lines) < 2:
                continue

            # Check if line 1 is PROOF and line 2 is shebang
            if lines[0].startswith("# PROOF:") and lines[1].startswith("#!"):
                # Swap them
                lines[0], lines[1] = lines[1], lines[0]
                new_content = "\n".join(lines)
                if content.endswith("\n"):
                    new_content += "\n"

                path.write_text(new_content, encoding="utf-8")
                print(f"Fixed shebang for: {path}")
                count += 1

    print(f"Total shebangs fixed: {count}")

if __name__ == "__main__":
    fix_shebangs()
