import os

# Define headers by module prefix/group
HEADERS = {
    "mekhane/periskope": "# PROOF: [L2/Search] <- mekhane/periskope/ A0→Knowledge→Search functionality",
    "mekhane/basanos/l2": "# PROOF: [L2/Testing] <- mekhane/basanos/l2/ A0→Quality→L2 Verification",
    "mekhane/ochema": "# PROOF: [L2/Routing] <- mekhane/ochema/ A0→Routing→Extension Server",
    "mekhane/api": "# PROOF: [L2/API] <- mekhane/api/ A0→Interface→API Routes",
    "mekhane/mcp": "# PROOF: [L2/MCP] <- mekhane/mcp/ A0→Integration→MCP Server",
    "mekhane/ccl": "# PROOF: [L2/CCL] <- mekhane/ccl/ A0→Control→CCL Linter/Loader",
    "mekhane/dendron": "# PROOF: [L2/Quality] <- mekhane/dendron/ A0→Quality→Falsification Checks",
    "mekhane/symploke": "# PROOF: [L2/Context] <- mekhane/symploke/ A0→Integration→Intent WAL",
    "mekhane/anamnesis": "# PROOF: [L2/Memory] <- mekhane/anamnesis/ A0→Memory→Vertex Embedder",
    "mekhane/exagoge": "# PROOF: [L2/Export] <- mekhane/exagoge/ A0→Export→Main Entry",
    "mekhane/tape.py": "# PROOF: [L2/Core] <- mekhane/tape.py A0→Storage→Tape Mechanism",
}

def get_header(filepath):
    """Determine the correct PROOF header based on file path."""
    # Special case for exact match
    if filepath == "mekhane/tape.py":
        return HEADERS["mekhane/tape.py"]

    # Check directory prefixes
    for prefix, header in HEADERS.items():
        if filepath.startswith(prefix):
            return header

    # Fallback
    return f"# PROOF: [L2/Impl] <- {os.path.dirname(filepath)}/ A0→Impl→Automated fix"

def apply_proofs(missing_file="missing_proofs.txt"):
    """Apply PROOF headers to files listed in missing_file."""
    try:
        with open(missing_file, "r") as f:
            files = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {missing_file} not found.")
        return

    for filepath in files:
        if not os.path.exists(filepath):
            print(f"Skipping missing file: {filepath}")
            continue

        header = get_header(filepath)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Check for existing header (simple check)
            if lines and "# PROOF:" in lines[0]:
                print(f"Skipping {filepath}: PROOF header already exists at line 1.")
                continue
            if len(lines) > 1 and "# PROOF:" in lines[1]:
                print(f"Skipping {filepath}: PROOF header already exists at line 2.")
                continue

            # Check for shebang
            has_shebang = lines and lines[0].startswith("#!")

            # Prepare new content
            new_lines = []
            if has_shebang:
                new_lines.append(lines[0])  # Keep shebang
                new_lines.append(header + "\n")
                new_lines.extend(lines[1:])
                print(f"Applied PROOF to {filepath} (after shebang)")
            else:
                new_lines.append(header + "\n")
                new_lines.extend(lines)
                print(f"Applied PROOF to {filepath} (at top)")

            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    apply_proofs()
