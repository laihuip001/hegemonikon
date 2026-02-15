## 2026-02-14 - [Codebase uses hardcoded Windows paths]
**Learning:** This codebase heavily relies on hardcoded absolute Windows paths (e.g., `M:\...`) in scripts like `mekhane/anamnesis/memory_search.py` and `mekhane/peira/scripts/chat-history-kb.py`. This prevents scripts from running or being imported directly in non-Windows environments without modification or mocking.
**Action:** When working on these scripts, always prefer mocking for tests and use relative imports/paths where possible, or use environment variables to override paths.
