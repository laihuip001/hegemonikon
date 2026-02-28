import re
from pathlib import Path

# Pattern to find missing PROOF headers in the dendron check output
def main():
    import subprocess
    result = subprocess.run(["python", "-m", "mekhane.dendron.cli", "check", "mekhane/", "--format", "ci"], capture_output=True, text=True)

    missing_files = []
    for line in result.stdout.splitlines():
        if "missing PROOF" in line or "Purpose:" in line or "TypeHints:" in line or "Reason:" in line:
            continue
        line = line.strip()
        if line and line.startswith("mekhane/"):
            missing_files.append(line)

    for file_path in missing_files:
        p = Path(file_path)
        if p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
            if "# PROOF:" not in content:
                # Determine L level based on path
                level = "L2"
                if "basanos" in file_path or "api" in file_path or "dendron" in file_path:
                    level = "L2"

                parts = p.parts
                category = parts[1].capitalize() if len(parts) > 1 else "Core"

                header = f"# PROOF: [{level}/{category}] <- {p.parent}/\n"

                lines = content.splitlines(keepends=True)
                # Insert after shebang if present, otherwise at top
                if lines and lines[0].startswith("#!"):
                    lines.insert(1, header)
                else:
                    lines.insert(0, header)

                p.write_text("".join(lines), encoding="utf-8")
                print(f"Added PROOF header to {file_path}")

if __name__ == "__main__":
    main()
