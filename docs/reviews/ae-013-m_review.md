# AE-013.M Review: Simplicity Audit of mekhane/symploke

> **Status:** Critical Issues Found
> **Reviewer:** Simplicity Gatekeeper (Macro)
> **Principle:** YAGNI (You Aren't Gonna Need It) & DRY (Don't Repeat Yourself)

## Summary

The `mekhane/symploke` module suffers from significant "Script Rot" and duplicated complexity. It mixes ad-hoc scripts with enterprise patterns, resulting in:
1.  **Hardcoded Absolute Paths**: Rendering the code non-portable.
2.  **Redundant Logic**: Multiple implementations of search and API client logic.
3.  **Code Duplication**: Near-identical index implementations.
4.  **Circular Dependencies**: Specialist definitions.
5.  **Import Hacks**: Widespread use of `sys.path.insert`.

## Findings

### 1. Unused Imports & Dead Code (High Severity)

- **`mekhane/symploke/boot_integration.py`**:
    - `from pathlib import Path`: Unused in function body (only used for `sys.path` hack).
- **`mekhane/symploke/handoff_search.py`**:
    - `from datetime import datetime, timedelta`: Imported but unused.
- **`mekhane/symploke/jules_client.py`**:
    - `import functools`: Unused.
    - `parse_state`: Legacy alias function. Remove.
- **`mekhane/symploke/run_remaining.py`**:
    - Appears to be a one-off script with hardcoded API keys. Duplicates `run_specialists.py`. **Delete.**
- **`mekhane/symploke/search_helper.py`**:
    - Redundant implementation of `mekhane/symploke/search/engine.py`. **Delete.**

### 2. Unnecessary Nesting & Import Hacks (Medium Severity)

- **Sys Path Hacks**:
    - Almost every script (`boot_integration.py`, `handoff_search.py`, `insight_miner.py`, `kairos_ingest.py`, `persona.py`, `run_specialists.py`, `search_helper.py`, `seed_data.py`, `sophia_backlinker.py`, `sophia_ingest.py`) uses `sys.path.insert(0, ...)` to import project modules.
    - **Fix**: Use relative imports within the package or install the package in editable mode (`pip install -e .`). Remove sys path hacks.
- **Inner Imports**:
    - `mekhane/symploke/factory.py`: `import hnswlib_adapter` inside function.
    - `mekhane/symploke/sophia_backlinker.py`: `import networkx` inside try/except.
    - `mekhane/symploke/sophia_ingest.py`: `EmbeddingAdapter` inside function.
    - **Fix**: Move imports to top-level or use dependency injection.

### 3. Excessive Abstraction & Duplication (Critical Severity)

- **Index Duplication**:
    - `mekhane/symploke/indices/chronos.py`
    - `mekhane/symploke/indices/gnosis.py`
    - `mekhane/symploke/indices/kairos.py`
    - `mekhane/symploke/indices/sophia.py`
    - These 4 files are 90% identical (implementing `ingest`, `search`, `_embed`).
    - **Fix**: Merge into a single `SymplokeIndex` class configured via `SourceType` or strategy pattern.
- **Redundant Search Logic**:
    - `search_helper.py` implements a simplified search that duplicates `mekhane/symploke/search/engine.py`.
    - **Fix**: Delete `search_helper.py` and use `SearchEngine`.
- **Redundant Client Logic**:
    - `run_specialists.py` implements its own `create_session` using `aiohttp` instead of using `JulesClient` from `jules_client.py`.
    - **Fix**: Refactor `run_specialists.py` to use `JulesClient`.

### 4. YAGNI / Anti-Patterns (Critical Severity)

- **Hardcoded Absolute Paths**:
    - `mekhane/symploke/handoff_search.py`: `/home/laihuip001/...`
    - `mekhane/symploke/persona.py`: `/home/laihuip001/...`
    - `mekhane/symploke/search_helper.py`: `/home/laihuip001/...`
    - `mekhane/symploke/sophia_backlinker.py`: `/home/laihuip001/...`
    - `mekhane/symploke/sophia_ingest.py`: `/home/laihuip001/...`
    - **Fix**: Use environment variables or relative paths from project root.
- **Circular Dependencies**:
    - `mekhane/symploke/specialist_prompts.py` <-> `phaseX_specialists.py`.
    - `specialist_prompts.py` defines `SpecialistDefinition` but also imports lists of specialists that use `SpecialistDefinition`.
    - **Fix**: Move `SpecialistDefinition` and `Archetype` to a separate `types.py` module to break the cycle.
- **Config Overloading**:
    - `mekhane/symploke/config.py`: `VectorStoreConfig` contains fields for all adapters (`hnsw`, `faiss`).
    - **Fix**: Use specific config classes or a dict for adapter params.

## Recommendations

1.  **Consolidate Indices**: Create `mekhane/symploke/indices/generic_index.py` and deprecate specific implementations.
2.  **Remove Hardcoded Paths**: Replace with `os.environ.get("SYMPLOKE_HOME", ...)` or `Path.home() / ...`.
3.  **Use JulesClient**: Rewrite `run_specialists.py` to import `JulesClient`.
4.  **Clean Imports**: Remove `sys.path.insert` and fix circular dependencies by extracting types.
5.  **Delete Dead Scripts**: Remove `run_remaining.py` and `search_helper.py`.
