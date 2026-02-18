# Hegemonikón: Core Architecture (v4.0)

## 1. Overview

Hegemonikón is an environment-agnostic cognitive system that prioritizes **Deductive Momentum** (Beauty) through the isomorphism of Active Inference (FEP), Category Theory, and optimization mathematics. It separates persistent intelligence (Oikos) from volatile local environments.

## 2. Directory Topology (Oikos Structure)

The "Oikos" (Household) structure decouples the "Brain" from the "Body".

- **oikos/**: Primary environmental container.
- **hegemonikon/**: Core runtime, scripts, and skills (Git-managed).
- **mneme/**: Memory layer (Non-Git/Volatile).
  - `.hegemonikon/sessions/`: Conversation logs and handoffs.
  - `.hegemonikon/indices/`: Vector search indices (Sophia).
- **.gemini/antigravity/knowledge/**: Persistent Knowledge Items (KIs).

## 3. Governance: The 12KB Rule & Hub Model

To manage the **12,000 character platform limit** for Rules, the system employs a **Parent-Child Scoping (Hub Model)**.

| Scope | Location | Content / Role |
| :--- | :--- | :--- |
| **Global Kernel** | `~/.gemini/GEMINI.md` | Immutable identity, mission, and behavioral principles. |
| **Workspace Specs** | `.agent/rules/*.md` | Project-specific technical specifications and naming conventions. |

### 3.1. Wash-away Refinement (洗練)

Refinement focuses on **Information Density** over simple byte reduction. Hierarchical Refactoring (Hub-and-Spoke) ensures 100% information preservation while maintaining granular accessibility. This was successfully executed for the core workflows (`/boot`, `/bye`, `/sop`, `/dia`, `/noe`, `/mek`) in February 2026, achieving a ~50% total size reduction while maintaining or increasing logic depth.

- **See**: [refactoring_protocols.md](../workflows/refactoring_protocols.md) for details on the "Kame-san" approach and anti-degradation standards.

### 3.2. Mirror Strategy (原本をいじるな)

To protect the Global Kernel, edits are performed on mirrored copies (`_WIP.md`) and validated before being swapped with the source material.

## 4. Mathematical Foundations (Project Kalon)

### 4.1. Arche: Beauty as Deductive Momentum

Beauty is the product of **Relation Compression** and **Deductive Potential**. A beautiful axiom compresses data into a single point from which further structures are derived (Theorem-Axiom Isomorphism).

- **FEP (Free Energy Principle)** = The Cognitive Axiom.
- **Category Theory** = The Structural Axiom.

### 4.2. Refined CCL Operators

CCL (Cognitive Control Language) operators are mapped to a 4-dimensional tensor space:

- **Intensity** (`+` / `-`): Vector Magnitude / Scalar Gradient.
- **Temporal** (`'` / `∫`): Calculus over session time.
- **Phase** (`/` / `\`): Geometric Algebra (Inner / Outer Product).
- **Abstraction** (`^` / `√`): Category Theory ascent.

## 5. Optimization Engine (Project Aristos)

Implements algorithms to maximize CCL efficiency:

- **Graph Theory**: Modeling workflows as multi-dimensional graphs.
- **Genetic Algorithms (GA)**: Optimizing derivative selectors.
- **Game Theory**: Strategic decision-making in multi-agent environments.

## 6. L2 Purpose Baseline (Project Dendron)

The teleological layer of the system. Every component must have a declared existence purpose, verified via L2 Surface audits (e.g., verifying `mekhane/fep` and `tekhne_registry.py`).

---
*Updated: 2026-02-06. Consolidated: architecture/system_design.md, architecture/v4_architecture_update.md, architecture/rule_limitations_and_refactoring.md.*
