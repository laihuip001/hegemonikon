# Risk Tag System Specification

## 1. Overview

The **Risk Tag System** (codified 2026-01-31) provides the quantitative basis for Recoverable Autonomy. It maps system operations to discrete risk levels, enabling the automated graduation of safety protocols.

## 2. Risk Levels & Responses

| Level | Symbol | Definition | Response Pattern |
| :--- | :--- | :--- | :--- |
| **Low** | 🟢 | Reversible, low impact, single file edits. | Autonomous execution + soft enforcement (@antiskip). |
| **Mid** | 🟡 | Reversible, medium impact, multi-file or logic changes. | Self-supervision (@premortem) + Git snapshot + decision log (Doxa) + @schema. |
| **High** | 🔴 | Irreversible or systemic impact, critical configs. | External/Council supervision (@council) + Full state snapshot + Explicit approval + @guardrails. |

## 3. Operation Mapping (Core)

- **Filesystem**:
  - `view_file` (Low)
  - `write_to_file` (Mid - if existing, High - if systemic)
  - `delete_knowledge` (High)
- **Logic**:
  - `mode change` (Mid)
  - `system_config` (High)

## 4. Recoverability Logic

- **Checkpointing**: Every Mid-level operation triggers a Git commit. Every High-level operation triggers a full state dump.
- **Rollback**: Restores the last known "Mid/High" checkpoint.

---
*Created: 2026-01-31 | v7.5 Strategic Alignment*
