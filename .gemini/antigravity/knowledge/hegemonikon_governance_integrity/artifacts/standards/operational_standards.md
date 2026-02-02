# Hegemonikón Operational Standards

> **Status**: Consolidated Master Standard (2026-02-01)
> **Base**: Hegemonikón Framework v6.30 / Metrika
> **Purpose**: Unifying implementation patterns, quality gates, and technical virtue.

---

## 1. Implementation Patterns (τ-layer)

### 1.1 The Boot Sequence (/boot v3.8)

Enforces the **Dual-Boot Philosophy** through four mandatory phases:

1. **Anti-Stale**: Logic self-verification.
2. **Session State**: Handoff and Weekly Review consumption.
3. **Knowledge Sync**: Sophia and Mnēmē integration.
4. **Environment Audit**: Tool and dependency check.

### 1.2 Digestion & Naturalization (/eat)

External knowledge is naturalized to minimize boundary entropy:

1. **Cooking (/mek)**: Transform to Markdown with lineage/theorem tags.
2. **Eating (/fit)**: Verify integration into existing workflows.

---

## 2. Metrika Quality Gates (μετρική)

Metrika establishes filters to ensure technical virtue during Praxis.

| Gate | Criterion | Threshold |
| :--- | :--- | :--- |
| **Dokimē** | Verification | Tests exist before implementation (TDD). |
| **Syntomia** | Elegance | Nesting <= 3, Method <= 30 lines. |
| **Atomos** | Modularity | Component < 120 lines. Logic must be atomic. |
| **Katharos** | Purity | Dead Code / Redundant Comments = 0. |
| **SEL** | Compliance | Adherence to `minimum_requirements` in frontmatter (>95%). |
| **Kairema** | Integrity | [Absolute Zero (0) audit findings](kairema_10_integrity_standard.md) across all axes (including Low). |

---

## 3. Agent Sincerity & Ethics

- **Truth over Sontaku**: Avoid "filler" or emotional decoration. Maintain "Philosopher-Engineer" persona.
- **Epochē (Suspension)**: Respect cognitive boundaries. If concerns are overwhelming, halting (Epochē) is the virtuous action.
- **Usability > Consistency**: A system that cannot be easily invoked is a failure. Naturalization must respect the mental model.

---

## 4. Tactical Engines (τ-Subsystems)

| Theorem | Command | SE Methodology |
| :--- | :--- | :--- |
| **O2 Boulēsis** | `/pre` | Premortem (Failure Analysis) |
| **O3 Zētēsis** | `/poc` | Spike / Proof of Concept |
| **O3 Zētēsis** | `/why` | Root Cause Analysis (Five Whys) |
| **O4 Energeia** | `/flag` | Feature Flags (Modular Production) |

---

## 5. Maintenance Standards

- **File Scale**: Warning at 50 MiB; Hard limit at 100 MiB (GitHub limit).
- **Binary Management**: Exclude large binaries; use LFS or external hubs.
- **Axiomatic Gates**:
  - **A1 Grounding**: Ambiguity -> 6W3H
  - **A2 Decomposition**: Large -> Small Batches
  - **A4 Actionability**: Ensure a definitive Next Action.
- **Python Tooling**:
  - Formatter: `black --line-length 100` (Standard for all `mekhane/` code).
  - Auditor: `ai_auditor.py` (22 axes of AI risk).
  - Integrity: `mekhane/synteleia` (8-Agent cognitive ensemble layer).

---
*Last Updated: 2026-02-01 | Continuity: Operational Standards v1.0*
