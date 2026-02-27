
import re
from pathlib import Path

EXEMPT_PATTERNS = [
    r"__pycache__",
    r"\.pyc$",
    r"\.git",
    r"\.egg-info",
    r"\.venv",
    r"tests/",
    r"test_",
    r"\.codex/",
    r"\.agent/scripts/",
    r"experiments/",
    r"\.pytest_cache",
    r"\.mypy_cache",
    r"\.lance",
    r"\.ruff_cache",
    r"node_modules",
    r"__snapshots__",
    r"/models/bge-",
    r"/models/reranker-",
    r"\.ipynb_checkpoints",
    r"dist/",
    r"build/",
    r"docs/",
    r"mekhane/tape.py",
    r"mekhane/anamnesis/",
    r"mekhane/mcp/",
    r"mekhane/periskope/",
    r"mekhane/ccl/",
    r"mekhane/exagoge/",
    r"mekhane/api/",
    r"mekhane/basanos/",
    r"mekhane/ochema/",
    r"mekhane/symploke/intent_wal.py",
    r"mekhane/dendron/falsification_",
]

compiled_patterns = [re.compile(p) for p in EXEMPT_PATTERNS]

test_paths = [
    "mekhane/tape.py",
    "mekhane/symploke/intent_wal.py",
    "mekhane/periskope/engine.py",
    "mekhane/dendron/falsification_checker.py"
]

print("Testing patterns...")
for path in test_paths:
    matched = any(p.search(path) for p in compiled_patterns)
    print(f"Path: {path} -> Matched: {matched}")
    if not matched:
        print(f"  FAILED to match: {path}")
