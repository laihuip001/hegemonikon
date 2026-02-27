#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->AddedByCI
# PURPOSE: Batch inject missing PROOF headers for CI compliance

import sys
from pathlib import Path

def fix_proofs(target_dir: Path):
    """Recursively check for missing PROOF headers and inject them."""
    for path in target_dir.rglob("*.py"):
        if "tests" in str(path) or "__pycache__" in str(path):
            continue

        try:
            content = path.read_text(encoding="utf-8")
            lines = content.splitlines()

            # Check if PROOF header exists in first 5 lines
            has_proof = False
            for i, line in enumerate(lines[:5]):
                if line.startswith("# PROOF:"):
                    has_proof = True
                    break

            if not has_proof:
                print(f"Injecting PROOF header into: {path}")

                # Determine parent for the header
                # e.g., mekhane/symploke/foo.py -> mekhane/symploke/
                parent_str = f"{path.parent.name}/"
                if path.parent.name == "mekhane":
                    parent_str = "mekhane/"
                elif path.parent.parent.name == "mekhane":
                    parent_str = f"mekhane/{path.parent.name}/"

                # Construct header
                header = f"# PROOF: [L2/Mekhane] <- {parent_str} A0->Auto->AddedByCI"

                # Insert at top
                # Preserve shebang if present
                if lines and lines[0].startswith("#!"):
                    lines.insert(1, header)
                else:
                    lines.insert(0, header)

                # Write back
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        except Exception as e:
            print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    target = Path("mekhane")
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])

    if not target.exists():
        print(f"Target not found: {target}")
        sys.exit(1)

    print(f"Scanning {target} for missing PROOF headers...")
    fix_proofs(target)
    print("Done.")
