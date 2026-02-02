# Auto-Rollback Mechanism Design

## 1. Overview

The **Auto-Rollback Mechanism** is the tactical implementation of the Recoverability > Autonomy paradigm. It ensures that the system can always return to a stable state if an operation fails validation.

## 2. Methodology: Git-Driven Recovery

Hegemonikón uses Git as the primary engine for state versioning.

- **Checkpoint**: A `git commit` or `git stash` created before an operation.
- **Rollback**: A `git reset --hard` or `git checkout` to the previous commit.

## 3. Operation Flow

1. **Detection**: Identify operation risk (Mid/High).
2. **Snapshot**:
   - `git commit -m "pre-op checkpoint"`
   - Backup of critical non-git untracked state (e.g., in-memory Doxa buffers).
3. **Execution**: Perform tool call / file edit.
4. **Validation**: Check against Guardrails or self-check rules.
5. **Finalization**:
   - **Success**: Keep changes, log results.
   - **Failure**: Trigger `@rollback`.

## 4. Rollback Granularity

- **Micro**: Single file restoration.
- **Meso**: Multi-file commit revert.
- **Macro**: System-wide state restoration (including knowledge base).

---
*Created: 2026-01-31 | v7.5 Strategic Alignment*
