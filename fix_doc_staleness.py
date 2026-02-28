import os

filepath = "mekhane/dendron/doc_staleness.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip().startswith("def warnings"):
        lines.insert(i, "    # PURPOSE: Returns staleness warnings for the document\n")
        break

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(lines)
