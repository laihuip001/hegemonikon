import re

with open(".github/workflows/tests.yml", "r") as f:
    content = f.read()

replacement = """              run: |
                  python -m pip install --upgrade pip
                  # Install PyTorch CPU first from proper index
                  pip install torch --index-url https://download.pytorch.org/whl/cpu
                  # Install core test dependencies (CPU-only)
                  pip install pytest pytest-asyncio pytest-timeout pyyaml pydantic lancedb numpy scipy \\
                              networkx pandas tabulate requests httpx schedule \\
                              sentence-transformers
                  # Install project in development mode if setup exists
                  pip install -e ".[test]" 2>/dev/null || true"""

content = re.sub(r"              run: \|\n                  python -m pip install --upgrade pip\n                  # Install core test dependencies \(CPU-only\)\n                  pip install pytest pytest-asyncio pytest-timeout pyyaml pydantic lancedb numpy scipy \\\n                              networkx pandas tabulate requests httpx schedule \\\n                              sentence-transformers torch --index-url https://download\.pytorch\.org/whl/cpu\n                  # Install project in development mode if setup exists\n                  pip install -e \"\.\[test\]\" 2>/dev/null \|\| true", replacement, content)

with open(".github/workflows/tests.yml", "w") as f:
    f.write(content)
