import re

with open('.github/workflows/tests.yml', 'r') as f:
    content = f.read()

# Replace the single pip install command with two separate ones
new_content = re.sub(
    r'(pip install pytest pytest-asyncio pytest-timeout pyyaml pydantic lancedb numpy scipy \\)\n(\s+networkx pandas tabulate requests httpx schedule \\)\n(\s+sentence-transformers )torch --index-url https://download.pytorch.org/whl/cpu',
    r'pip install torch --index-url https://download.pytorch.org/whl/cpu\n                  \1\n\2\n\3',
    content
)

with open('.github/workflows/tests.yml', 'w') as f:
    f.write(new_content)
