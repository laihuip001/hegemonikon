## 2026-02-14 - [Codebase uses hardcoded Windows paths]
**Learning:** This codebase heavily relies on hardcoded absolute Windows paths (e.g., `M:\...`) in scripts like `mekhane/anamnesis/memory_search.py` and `mekhane/peira/scripts/chat-history-kb.py`. This prevents scripts from running or being imported directly in non-Windows environments without modification or mocking.
**Action:** When working on these scripts, always prefer mocking for tests and use relative imports/paths where possible, or use environment variables to override paths.

## 2026-02-15 - [CI uses index-url instead of extra-index-url]
**Learning:** The CI configuration was using `--index-url` for the PyTorch repository, which prevented pip from searching PyPI for standard packages like `pytest`.
**Action:** Always use `--extra-index-url` when adding a secondary package repository like PyTorch's wheel index, unless you specifically want to exclude PyPI.
