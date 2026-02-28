with open("mekhane/basanos/l2/deficit_factories.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("# PROOF: 41/41"):
        new_lines.append("# PROOF: [L2/Schema] <- mekhane/basanos/l2/\n")
    else:
        new_lines.append(line)

with open("mekhane/basanos/l2/deficit_factories.py", "w") as f:
    f.writelines(new_lines)
