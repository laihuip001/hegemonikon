# Cognitive Operators: Inner and Outer Products

Synteleia introduces advanced cognitive operators to manage the interaction between the Poiēsis (Generative) and Dokimasia (Evaluative) layers. These operators are represented in CCL using mathematical symbols.

## 1. Inner Product (`·`) — Synthesis

The **Inner Product** represents parallel execution followed by a standard synthesis (merge) of findings.

- **Logic**: 2 Layers → Parallel Execution → Consensus Synthesis → Single Output.
- **CCL Symbol**: `@syn·` or `@poiesis·@dokimasia`.
- **Use Case**: Standard cognitive processing where qualitative insight (O,S,H) and quantitative audit (P,K,A) are combined into a balanced result.
- **Computational Cost**: $N+M$ (Linear sum of agent calls).

## 2. Outer Product (`×`) — Cross-Verification

The **Outer Product** represents an exhaustive cross-verification matrix where the outputs of one layer are scrutinized by the agents of the other layer.

- **Logic**: Layer A (Generative) × Layer B (Evaluative) → MxN Verification Grid.
- **CCL Symbol**: `@syn×` or `@poiesis×@dokimasia`.
- **Use Case**: Exhaustive critical verification. For example, verifying the "Essence" (O) from the Poiēsis layer against the "Boundary" (P) from the Dokimasia layer (O×P).
- **Matrix Examples**:
  - **O×P**: "Is the essence of this thought within the defined scope?"
  - **H×K**: "Is the motivation for this action appropriate for the current timing?"
  - **S×A**: "Is the internal structure logically precise?"
- **Computational Cost**: $N \times M$ (Product of agent calls).

## 3. Symbolic Notation and Implementation

These operators allow for high-fidelity cognitive control. By simply toggling between `·` and `×`, an operator can choose between "Efficiency/Consensus" and "Rigor/Exhaustive Audit".
