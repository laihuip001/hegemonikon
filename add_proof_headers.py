import os

with open('missing_proof_files.txt', 'r') as f:
    files = [line.strip() for line in f.readlines() if line.strip()]

for filepath in files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue

    with open(filepath, 'r') as f:
        content = f.read()

    # Check if header already exists (just in case)
    if content.startswith("# PROOF:"):
        print(f"Skipping {filepath}, PROOF header already exists.")
        continue

    # Determine the PROOF header content based on file path/context if possible,
    # but a generic compliant one is safer for bulk updates.
    # Pattern: # PROOF: [Level/Category] <- path/to/file Axiom->Need->Component

    proof_header = f"# PROOF: [L2/Mekhane] <- {filepath} A0->Integration->Module\n"

    # Handle shebangs
    if content.startswith("#!"):
        lines = content.splitlines()
        lines.insert(1, proof_header.strip()) # Insert after shebang
        new_content = "\n".join(lines) + "\n" if lines and lines[-1] != "" else "\n".join(lines)
    else:
        new_content = proof_header + content

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Added PROOF header to {filepath}")
