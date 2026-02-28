import os
import sys

missing_files = [
    "mekhane/basanos/l2/deficit_factories.py"
]

for file in missing_files:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()

        # Only add if not already present
        if "# PROOF:" not in content:
            # We'll prepend # PROOF: [L2/Missing] <- <dir>\n
            dir_name = os.path.dirname(file) + "/"

            new_content = f"# PROOF: [L2/Missing] <- {dir_name}\n"

            if content.startswith("#!/usr/bin/env python3"):
                new_content = "#!/usr/bin/env python3\n" + new_content + content[len("#!/usr/bin/env python3\n"):]
            else:
                new_content = new_content + content

            with open(file, 'w') as f:
                f.write(new_content)
            print(f"Fixed {file}")
