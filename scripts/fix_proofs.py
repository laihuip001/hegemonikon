import os
import subprocess
from pathlib import Path

def fix_proofs():
    # Run dendron check and capture output
    result = subprocess.run(
        ["python", "-m", "mekhane.dendron.cli", "check", "mekhane/", "--ci", "--format", "ci"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.split('\n') + result.stderr.split('\n')
    missing_files = []

    for line in lines:
        line = line.strip()
        if line.startswith("mekhane/") and line.endswith(".py"):
            missing_files.append(line)

    for filepath in missing_files:
        path = Path(filepath)
        if not path.exists():
            print(f"File not found: {filepath}")
            continue

        parent_dir = path.parent.name
        proof_header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent_dir}/ A0->Auto->AddedByCI\n"

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if proof already exists
        if "PROOF:" in content:
            print(f"Skipping {filepath}, already has PROOF")
            continue

        # Add proof header
        # Handle cases where there is a shebang or encoding declaration
        if content.startswith("#!") or content.startswith("# -*-"):
            first_newline = content.find('\n')
            if first_newline != -1:
                content = content[:first_newline+1] + proof_header + content[first_newline+1:]
            else:
                content = content + "\n" + proof_header
        else:
            content = proof_header + content

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed {filepath}")

if __name__ == "__main__":
    fix_proofs()
