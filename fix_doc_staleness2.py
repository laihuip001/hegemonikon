import os

filepath = "mekhane/dendron/doc_staleness.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "PURPOSE: Implementation of warnings" in line or "PURPOSE: Returns staleness warnings" in line:
        continue
    if line.strip().startswith("@property"):
        new_lines.append("    # PURPOSE: Returns staleness warnings for the document\n")
        new_lines.append(line)
    else:
        new_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
