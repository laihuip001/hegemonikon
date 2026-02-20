import sys
from pathlib import Path

def main():
    with open("missing_proofs.txt", "r") as f:
        lines = f.readlines()

    files = []
    for line in lines:
        line = line.strip()
        if line.startswith("mekhane/") and line.endswith(".py"):
            files.append(line)

    print(f"Found {len(files)} files to fix.")

    for filepath in files:
        path = Path(filepath)
        if not path.exists():
            print(f"Skipping {filepath} (not found)")
            continue

        content = path.read_text(encoding="utf-8")
        if "# PROOF:" in content.splitlines()[0] or "# PROOF:" in content.splitlines()[1]:
             print(f"Skipping {filepath} (already has header)")
             continue

        # Determine category based on path
        category = "[L2/インフラ]"
        axiom = "A0→基盤→実装"

        if "periskope" in filepath:
            category = "[S2/Mekhanē]"
            axiom = "S2→探求→DeepSearch"
        elif "basanos" in filepath:
            category = "[L2/インフラ]"
            axiom = "A0→テスト→検証"
        elif "ccl" in filepath:
            category = "[L1/Hermēneus]"
            axiom = "S1→言語→CCL"
        elif "mcp" in filepath:
            category = "[L3/MCP]"
            axiom = "S2→接続→MCP"
        elif "api" in filepath:
            category = "[L2/インフラ]"
            axiom = "S2→API→Endpoint"
        elif "ochema" in filepath:
            category = "[S2/Mekhanē]"
            axiom = "S2→Routing→Ochēma"

        # Construct header
        header = f"# PROOF: {category} <- {path.parent}/ {axiom}"

        # Insert header
        if content.startswith("#!"):
            # Insert after shebang
            lines = content.splitlines()
            lines.insert(1, header)
            new_content = "\n".join(lines) + "\n"
        else:
            new_content = header + "\n" + content

        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed {filepath}")

if __name__ == "__main__":
    main()
