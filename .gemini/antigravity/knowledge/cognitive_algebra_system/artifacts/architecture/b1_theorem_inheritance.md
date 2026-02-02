# B1: Theorem Inheritance (Deductive Traceability)

> **Version**: 1.1 (2026-02-01)
> **Goal**: Achieve "Deductively Restorable Structure" (B1 Paradigm).
> **Refined**: Removed `level` field to avoid redundancy with `axiom_hierarchy.md`.

## 1. The `extends` Paradigm

Hegemonikón theorems are not arbitrary; they are derived from core axioms. The **B1 Paradigm** mandates the explicit declaration of this heritage in every kernel file to ensure that the entire cognitive architecture can be reconstructed from first principles.

### Frontmatter Schema

```yaml
extends:
  axioms: [List of Axioms]   # e.g., [L0.FEP, L1.Flow, L1.Value]
  generation: "Formula"     # e.g., "L1 × L1.5"
```

---

## 2. Deductive Chain Mapping

The 6 Series (O, S, H, P, K, A) are mapped to axioms and levels accordingly:

| Series | Generation | Primary Axioms |
| :--- | :--- | :--- |
| **Ousia (O)** | L1 × L1 | L0.FEP, L1.Flow, L1.Value |
| **Schema (S)** | L1 × L1.5 | L0.FEP, L1.Flow, L1.Value, L1.5.Scale, L1.5.Function |
| **Hormē (H)** | L1 × L1.75 | L0.FEP, L1.Flow, L1.Value, L1.75.Valence, L1.75.Precision |
| **Perigraphē (P)** | L1.5 × L1.5 | L0.FEP, L1.5.Scale, L1.5.Function |
| **Kairos (K)** | L1.5 × L1.75 | L0.FEP, L1.5.Scale, L1.5.Function, L1.75.Valence, L1.75.Precision |
| **Akribeia (A)** | L1.75 × L1.75 | L0.FEP, L1.75.Valence, L1.75.Precision |

---

## 3. Design Rationale

- **Recoverability over Autonomy**: Ensures that if any high-level theorem (e.g., A4 Epistēmē) is compromised, it can be re-derived from L0/L1 roots.
- **Pythonic Wisdom**: Direct application of class inheritance concepts (`class Theorem(Axiom):`) to cognitive architecture.
- **MECE Axioms**: Axiom lists specifically use the `L0.FEP` format for unique identification.
- **Structural Enforcement**: The `extends` field serves as a "B1-Badge". Any new derivative or proposed theorem must provide its `extends` chain to be admitted into the canonical kernel.
