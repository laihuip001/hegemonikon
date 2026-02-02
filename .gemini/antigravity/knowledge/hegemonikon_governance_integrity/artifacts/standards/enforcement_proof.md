# Enforcement & Proof Standards (Agentic Zero-Trust)

## 1. SE 5 Principles (Structural Enforcement)

Structural Enforcement (SE) is the practice of imposing constraints on the AI to eliminate laziness and cognitive skipping.

1. **Iteration (反復)**: Wash generations through refinement cycles.
2. **Fail Fast (即時失敗)**: Halt sequences immediately upon defect detection.
3. **Timeboxing (時間枠)**: Explicitly bound cognitive resources.
4. **Structural Constraints (構造的制約)**: Use "Forms" and "Templates" instead of free-form instructions.
5. **Existence Proof (存在証明)**: Every artifact must justify its own existence via the PROOF protocol (Verified via **Project Dendron**).
6. **Universal Audit (普遍的監査)**: Every cognitive step and output must be subject to a multi-perspective verification (Operator, Logic, Completeness).

---

## 2. PROOF Protocol (Existence Proof)
 
 Every file must lead with a PROOF header justifying its existence and relationship to core axioms.
 
### 2.1 The "Git of Meaning" Analogy
**Dendron** (the Existence Proof tool) is defined as the **"Git of Meaning"**. Just as Git tracks "How/When/Who," Dendron tracks "**Why**." 
- **Institutionalization**: In the AI-driven era, code implementation is abundant (Hormē), but the "Reason for Being" (Ousia) must be explicitly governed and justified.

### 2.2 Existence Responsibility (存在責任)
>
> **命題: 証明の深さ ∝ ファイルの「存在責任」の重さ**

- **L1 (Axiomatic/Core)**: Deep deductive proof required. Highest responsibility.
- **L2 (Infrastructure/System)**: Functional necessity within the architecture.
- **L3 (Utility/Testing)**: Specific task-based or verification purpose.

### 2.3 Syntax: The Deductive Arrow (<-)
As of **Dendron v2 (2026-02-01)**, every PROOF header must explicitly link to its logical parent to verify the deductive chain.

**Format**: `# PROOF: [Level/Category] <- Parent`

**Note**: The implementation allows trailing text after the parent or header to accommodate explanatory context (e.g., `# PROOF: [L1/定理] A0→...`).

To ensure that existence reasons do not "decay" or get "buried" in large implementations, the repository utilizes a **Visibility Layer** (`projects.yaml`) and a **Red-Team Oversight** protocol.

### 2.3.1 Proactive Red-Team Audits (/mek+)
Beyond static checks, critical components (like Dendron itself) undergo "persistent" (執拗) human-AI cooperative audits. The CCL operator `/mek+` triggers a multi-perspective red-team evaluation, identifying logical bypasses or conceptual decay that regex-based checkers cannot detect.
- **Status**: All active projects must maintain 100% PROOF coverage (Milestone achieved by Project Hermēneus on 2026-02-01).
- **Enforcement**: Projects with stale justification (>7-21 days) are flagged during the `/boot` sequence.

---

## 3. Graduated Enforcement (Zero-Trust)

We scale enforcement based on criticality using specific Trigger Macros.

| Level | Mode | Implementation | Trigger Macro |
| :--- | :--- | :--- | :--- |
| 🟢 **Low** | **Soft** | Anti-Skip Protocol (Checkboxes). | `@antiskip` |
| 🟡 **Medium** | **Medium** | JSON Schema & Mandatory Templates. | `@schema` |
| 🔴 **High** | **Hard** | External Validators / Guardrails AI. | `@guardrails` |

---

## 4. Graduated Supervision

| Level | Mode | Strategy | Trigger Macro |
| :--- | :--- | :--- | :--- |
| 🟢 **Low** | **Self** | Internal reflection via `/dia`. | `@selfcheck` |
| 🟡 **Medium** | **Joint** | Joint review + Premortem (`/pre`). | `@premortem` |
| 🔴 **High** | **External** | Council audit (`/syn`) or human approval. | `@council` |

---

## 5. Implementation Rules

- **Anti-Skip Protocol**: Mandatory checkboxes for complex multi-step tasks.
- **Complexity Points (CP)**: Mandated complexity ranges to prevent laziness (v6.45).
- **Internalized Aesthetic Principle**: Prioritize "Internalized Aesthetic" over crude rule-binding. True integrity arises from semantic necessity.

---
*Standard Version: 2026-02-01 | Architecture: Structural Enforcement v1.4*
