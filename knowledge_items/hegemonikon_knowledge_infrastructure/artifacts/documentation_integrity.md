# Infrastructure Protocol: Documentation Integrity (原本維持)

> **"Don't touch the original. Change the copy. Preserve the system."**

## 1. The Principle: 原本をいじるな (Don't touch the original)

In any high-complexity refactoring context (especially those involving character limits like the 12KB rule), the canonical source file is at high risk of corruption or partial deletion (as seen in the v3.3.0 "Deterioration" incident).

### 1.1. Core Rules

1. **Zero-Inplace Refactoring**: Never refactor a core kernel file (`GEMINI.md`) or a mission-critical workflow (`sop.md`) in-place.
2. **Mandatory Mirroring**: Create a WIP copy (e.g., `*_WIP.md`) or update a Knowledge Item (KI) with the draft before modifying the destination.
3. **Reference Point**: Keep the original open or available in a stable directory (e.g., `~/ダウンロード/` or `~/backup/`) until the new version is verified as a superior "Refinement" (洗練).

## 2. KI as a Transitionary Workspace (Dendron Integration)

The Hegemonikón Knowledge Infrastructure serves as the **Safe Environment** for logical transformations.

### 2.1. The Refactoring Workflow

- **State Capture**: Before starting, summarize the current source file in a Knowledge Item artifact.
- **Drafting**: Perform the "Wash-away Refactoring" within the KI or a dedicated Dendron note.
- **Verification**: Check the draft against the "Axiom Visibility Test" (Do all 60 elements remain intact?).
- **Deployment**: Only after verification, use `write_to_file` to update the canonical kernel file.

### 2.2. The Gold Standard (Beautiful Refinement)

During the v3.3.0 restoration, a **project-local `.gemini/GEMINI.md`** was discovered within the `oikos/hegemonikon` workspace. Measuring only **1,623 bytes (58 lines)**, it serves as the definitive proof of concept for "Wash-away Refactoring." It achieves extreme density by acting as a high-level index that delegates details to the Rules and Skills layers.

## 3. Mirror Locations

| File Type | Primary Source | Safe Mirror (Transitionary) |
| :--- | :--- | :--- |
| **Kernel** | `~/.gemini/GEMINI.md` | `hegemonikon_core_system/artifacts/architecture/...` |
| **Workflows**| `.agent/workflows/*.md` | `hegemonikon_core_system/artifacts/workflows/...` |
| **Skills** | `.agent/skills/.../SKILL.md` | `hegemonikon_core_system/artifacts/identity/...` |

---
*Codified 2026-02-05 following the user's directive regarding Dendron and documentation safety.*
