import os
from pathlib import Path

MEKHANE_ROOT = Path("mekhane")

INTENT_WAL_PROOF = "# PROOF: [L2/Mekhane] <- mekhane/symploke/intent_wal.py O1→Zet→IntentWAL"

def fix_proofs():
    count = 0
    for root, dirs, files in os.walk(MEKHANE_ROOT):
        for file in files:
            if not file.endswith(".py"):
                continue

            path = Path(root) / file

            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Skipping {path}: {e}")
                continue

            if content.startswith("# PROOF:"):
                continue

            # Special case for intent_wal.py
            if file == "intent_wal.py" and "symploke" in str(path):
                proof = INTENT_WAL_PROOF
            else:
                # Generic PROOF
                rel_path = path.relative_to(Path("."))
                proof = f"# PROOF: [L2/Mekhane] <- {rel_path} Auto-generated existence proof"

            # Prepend PROOF
            new_content = proof + "\n" + content
            path.write_text(new_content, encoding="utf-8")
            print(f"Fixed PROOF for: {path}")
            count += 1

    print(f"Total fixed: {count}")

if __name__ == "__main__":
    fix_proofs()
