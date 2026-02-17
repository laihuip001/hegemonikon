# Forge Path Regularization

Last updated: 2026-02-05

## 1. Context: The Windows-Era Legacy

Historically, certain research and knowledge assets were stored in a directory named `forge/`, often referenced with Windows-style drive letters (e.g., `M:\Hegemonikon\forge\`). This "Forge" structure served as the primary repository for raw scraped data and automation scripts.

## 2. Regularization (Linux Environment)

In the current Debian/Linux environment, the `forge/` directory has been officially deprecated and regularized into the Hegemonikón directory tree.

### Mapping

| Legacy Path (Windows) | New Path (Linux) | Role |
| :--- | :--- | :--- |
| `M:\Hegemonikon\forge\Raw\aidb\` | `mekhane/gnosis/` (as vector chunks) | AIDB Source Data |
| `M:\Hegemonikon\forge\scripts\` | `mekhane/peira/scripts/` | Collection & Maintenance Scripts |
| `forge/Raw/arxiv/` | `mekhane/gnosis/raw/arxiv/` | Future arXiv Repository |

## 3. Findings from 2026-02-05 Cleanup

A system-wide search for "Forge" and "M:\" references revealed the following:

- **Active Handoffs**: `docs/handoff/aidb-phase6-handover.md` was updated to reflect new Linux paths and include the `/eat` integration task.
- **Historical Records**: References in `docs/archive/`, `docs/research/archived/`, and `mneme/excavated/` are kept as-is to preserve session history logic.
- **Conceptual Usage**: In `kernel/meta/gnosis.md`, the term "Forge" is retained as an **abstract module** (Hegemonikon = Gnōsis × Skills × Forge), representing "Action" or "Behavior" rather than a file path.

## 4. Maintenance Rule

- **Do NOT** create new folders named `forge/` at the root.
- **Always** use relative paths within `mekhane/` or `kernel/` to maintain the **Zero Design** principle of platform portability.
