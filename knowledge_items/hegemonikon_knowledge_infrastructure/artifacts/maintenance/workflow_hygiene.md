# Workflow Hygiene and Platform Maintenance

## 1. Overview

To maintain a clean operational environment and prevent "Suggestion Pollution" in the Antigravity platform, periodic maintenance of workflow files and system rules is required.

## 2. Workflow Suggestion Suppression

The Antigravity platform automatically indexes all `.md` files within the `.agent/workflows/` directory as executable slash commands (Workflows). This includes backup files, WIP versions, and archived drafts.

### 2.1. Suppression Protocol

To prevent non-active workflows from appearing in the `/` suggestion menu:

- **Action**: Rename non-active or backup markdown files with the `.bak` extension (e.g., `boot_v3.9_backup.md` -> `boot_v3.9_backup.md.bak`).
- **Effect**: The platform ignores non-`.md` files for workflow indexing, while preserving the content for historical reference or restoration.
- **Batch Processing**: Use the following shell pattern:

  ```bash
  for f in *.md; do mv "$f" "${f}.bak"; done
  ```

## 3. Global Rule (GEMINI.md) Hierarchy

Global rules are maintained in `~/.gemini/GEMINI.md`.

### 3.1. Version Control and Archives

- **Status Quo**: Multiple versions (v2.x, v3.x) and WIP files of `GEMINI.md` often accumulate in `~/.gemini/` or `~/Downloads/`.
- **Hygiene Rule**: All non-current versions of `GEMINI.md` must be moved to `~/.gemini/archive/` to ensure the agent only reads the canonical `~/.gemini/GEMINI.md`.
- **Current Canonical Version (2026-02-07)**: v3.4.0.

## 4. Maintenance History

- **2026-02-07**: Renamed 7 backup/WIP workflows to `.md.bak`. Consolidated 4 legacy `GEMINI.md` files into `~/.gemini/archive/`. Deleted `boot_v4.0_WIP.md`.
