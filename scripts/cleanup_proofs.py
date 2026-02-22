import os
from pathlib import Path

MEKHANE_ROOT = Path("mekhane")

def cleanup_proofs():
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
            if not lines:
                continue

            # Identify PROOF lines
            proof_lines = []
            for i, line in enumerate(lines):
                if line.startswith("# PROOF:"):
                    proof_lines.append((i, line))
                if i > 5: # PROOF should be near top
                    break

            if len(proof_lines) <= 1:
                continue

            # If duplicates found
            print(f"Cleaning duplicates in: {path}")

            # Filter out "Auto-generated" if "specific" exists
            # We want to keep the specific one.
            # If both are auto-generated, keep one.
            # If both are specific, keep the first one?

            specific_proofs = [p for p in proof_lines if "Auto-generated" not in p[1]]
            auto_proofs = [p for p in proof_lines if "Auto-generated" in p[1]]

            if specific_proofs:
                # Keep the first specific proof
                target_proof = specific_proofs[0][1]
            elif auto_proofs:
                # Keep the first auto proof
                target_proof = auto_proofs[0][1]
            else:
                # Should not happen based on logic above
                continue

            # Remove ALL existing PROOF lines from the first few lines
            new_lines = []
            proof_inserted = False

            # Check shebang
            has_shebang = lines[0].startswith("#!")

            for i, line in enumerate(lines):
                if line.startswith("# PROOF:"):
                    continue # Skip old proofs

                # Insert target proof at appropriate place
                if not proof_inserted:
                    if has_shebang:
                        if i == 1: # After shebang (line 0)
                            new_lines.append(target_proof)
                            proof_inserted = True
                    else:
                        if i == 0:
                            new_lines.append(target_proof)
                            proof_inserted = True

                new_lines.append(line)

            # Handle case where file was only comments/proofs and we skipped everything?
            # Or if proof needs to be appended if we didn't hit insertion point?
            # With the logic above, if we skip lines 0/1/2 etc, we just append to new_lines.
            # But we need to insert the kept proof.

            # Let's simplify:
            # 1. Remove all PROOF lines.
            # 2. Insert target_proof at line 0 or 1.

            clean_lines = [line for line in lines if not line.startswith("# PROOF:")]

            if clean_lines and clean_lines[0].startswith("#!"):
                clean_lines.insert(1, target_proof) # Insert after shebang
            else:
                clean_lines.insert(0, target_proof) # Insert at top

            new_content = "\n".join(clean_lines)
            if content.endswith("\n"):
                new_content += "\n"

            path.write_text(new_content, encoding="utf-8")
            count += 1

    print(f"Total files cleaned: {count}")

if __name__ == "__main__":
    cleanup_proofs()
