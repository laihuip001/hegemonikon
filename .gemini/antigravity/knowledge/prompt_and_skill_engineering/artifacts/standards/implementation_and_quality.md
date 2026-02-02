# Implementation & Quality Standards (v2.5)

This document codifies the architectural, logic, and testing standards for skills, workflows, and artifacts within the Hegemonikón ecosystem.

## 1. Architectural Standards (3-Layer SSOT)

Hegemonikón follows a strict separation of concerns to ensure cognitive consistency.

| Layer | Responsibility | Purpose |
| :--- | :--- | :--- |
| **Index (KI)** | Discovery | Selection criteria, use cases, high-level navigation. |
| **Orchestrator (Workflow)** | Interaction | Session management, input/output validation. |
| **Logic Engine (Skill)** | Specification | **Core theorem logic, processing phases, detailed rules.** |

### 1.1 Parent-Child Inheritance Pattern

- **Skill (Parent)**: Abstract Base. SSOT for logic and theorem definitions.
- **Workflow (Child)**: Concrete Implementer. Step-by-step procedures and templates.

### 1.2 Mandatory Step 0 (Execution Proof)

All workflows must implement `Step 0`:

1. **Read Skill**: Load the governing `SKILL.md`.
2. **Verify Protocol**: Confirm Anti-Skip Protocol is active.
3. **Audit**: Ensure no concrete detail was lost during refactoring.

## 2. SE 5 Principles (Software Engineering for Hegemonikón)

Integrated into `/mek` v6.5, these guide iterative development.

1. **Iteration First (反復原則)**: First generation is a "Draft". Follow with `/dia-` immediately.
2. **Fail Fast & Early (早期失敗原則)**: Identify likely failure causes before committing to long sequences.
3. **Visual Logic Rule (可視化原則)**: Structures must be visible and audit-ready. Use visual anchors.
4. **Time-boxing (タイムボックス原則)**: Limit cognitive load by setting explicit time bounds. Steps in `/mek` are annotated with estimated durations (e.g., ⏱️ 5分).
5. **Reverse Setup (逆位置原則)**: Define the "End State" and "Goal" before the "Method". Establish success criteria first.

## 3. Skill-WF Integration (The "Bridge")

Every `SKILL.md` must include a `## Related Modes` section to bridge the gap between Workflow interface modes and Skill reasoning logic.

### 3.1 Mapping Matrix (Priority)

- **a3-gnome**: `/gno` (disc, extr, analogy_*, personify).
- **p1-khora**: `/kho` (scope, boundary, a3, platform).
- **s3-stathmos**: `/sta` (robust, delta, security, rela).
- **a2-krisis**: `/dia` (adv, steelman, epo, root).
- **s1-metron**: `/met` (fermi, kiss, units, check).

### 3.2 SE-6 Scalable Foundation

Integration is managed via `theorem_map.yaml` (SSOT) and `bidirectional_linker.py` (Automation), ensuring 100% invariant satisfaction across all 24 priority Theorem Skills.

## 4. Developer Wisdom: Testing & Debugging

- **Reliable Mock Injection**: Override methods on the instance using `lambda` to avoid lifecycle failures.
- **Dynamic Side Effects**: Use `side_effect` functions that respect input shape.
- **Namespace Management**: Reserve `test_` prefix for unit tests; utilities (e.g., `fast_fetch.py`) should not use it.
- **Graceful Degradation**: Use `HAS_DEPS` checks for binary dependencies (e.g., `html2text`).

## 5. Skill Design Convention (2026-02-01)

Principles extracted from comprehensive insight mining.

### 5.1 Convention-First Design

> **「設計がぶれないよう、最初に『スキル設計規約』を明文化すべき」**

Before implementing a new skill, document its:

- **Purpose**: What cognitive function does it serve?
- **Trigger conditions**: When should it activate?
- **Output format**: What should the skill produce?

### 5.2 Principles Over Procedures (手順より原則)
>
> **「手順」ではなく「原則」を教える方法論である。**

Skills should prioritize teaching the "Why" and the "Governing Theorem" over a blind sequence of steps. This ensures that the AI can adapt the logic to novel situations rather than failing on edge cases.

### 5.3 Efficiency is Quality
>
> **1,000トークンの構造化依頼 > 2,000トークンの冗長依頼**

A high-integrity prompt is measured by its structural density, not its length. Redundancy beyond the necessary baseline (Refinement threshold) introduces noise and increases boundary entropy.

---
*Updated: 2026-02-01 | Implementation & Quality Standards v2.6*
