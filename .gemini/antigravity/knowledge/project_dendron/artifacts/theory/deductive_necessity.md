# Dendron: Existence as Deductive Necessity

> **Axiom**: In a system minimizing variational free energy, every component must have a functional necessity (Ousia). An artifact without necessity is "existence error."

## 1. The Core Principle: Logical Deduction

Dendron (Existence Proof) is more than a metadata convention; it is a mechanism for **deducing implementation from premises**.

### 1.1 From Axiom to Implementation

A valid Existence Proof follows a rigorous chain:
1.  **A0 (Axiom)**: e.g., FEP (Free Energy Principle).
2.  **Theorem**: Derived from A0 (e.g., "The system must maintain an internal model").
3.  **Policy**: A decision to implement the theorem (e.g., "We will create a `kernel/` directory").
4.  **Artifact**: The physical file.

In this paradigm, a file is "justified" only if its absence would break the logical chain back to the axiom.

## 2. Global vs. Local Verification

### 2.1 The Batch Nature of Deduction

The user observed that "Dendron is suited for batch processing." This is because a **Deductive Chain** often spans multiple files and directories.
-   **Global Verification**: Verifies the entire graph (Axiom → Kernel → Mekhane → File). This solves "Orphan" problems where a file has a PROOF label but no logical connection to the system.
-   **Local Optimization**: Performed during file creation or editing. We accept "local" justification (referencing the immediate parent) to maintain implementation velocity, acknowledging that full global verification happens during batch audits.

## 3. The Evolutionary Shift: Labeling to Linking

The graduation from Dendron v1 to v2 marks a shift in cognitive algebra:
-   **v1 (Labeling)**: `# PROOF: [L1/定理]` — "I claim I am a theorem."
-   **v2 (Linking)**: `# PROOF: [L1/定理] <- parent` — "I am a theorem derived from [parent]."

This mandatory linking turns the codebase from a collection of justified files into a **verifiable tree of existence**.
