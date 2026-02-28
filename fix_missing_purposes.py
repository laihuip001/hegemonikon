import os

files = {
    "mekhane/dendron/falsification_matcher.py": ["def load_registry", "def check_falsification", "def format_alerts"],
    "mekhane/dendron/doc_staleness.py": ["def warnings("]
}

for filepath, funcs in files.items():
    if not os.path.exists(filepath):
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        for func in funcs:
            if line.strip().startswith(func):
                # check if previous line has # PURPOSE
                if i > 0 and "# PURPOSE" in lines[i-1]:
                    continue
                # Add purpose
                purpose_text = f"    # PURPOSE: Implementation of {func.replace('def ', '').split('(')[0]}\n"
                if line.startswith("    def"):
                    lines.insert(i, purpose_text)
                else:
                    lines.insert(i, f"# PURPOSE: Implementation of {func.replace('def ', '').split('(')[0]}\n")
                break

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
