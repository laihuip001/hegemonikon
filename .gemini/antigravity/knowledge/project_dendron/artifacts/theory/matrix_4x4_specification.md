# Dendron 4x4 Verification Matrix

The Dendron 4x4 Matrix is the definitive logical framework for ensuring "Existence Proof" and "Zero Arbitrariness" in the Hegemonikón codebase. It cross-references the granularity of code elements with the depth of verification.

## 1. The Two Axes

### Axis A: Granularity (Dendron Layers)

- **L0: Directory**: The container logic.
- **L1: File**: The module/unit logic.
- **L2: Block**: Functions and Classes (Docstrings).
- **L3: Token**: Individual symbols and variables.

### Axis B: Meta Layers (Verification Depth)

- **Surface**: Declarative proof (Does the PROOF header/docstring exist and is it valid?).
- **Structural**: Dependency proof (Is it correctly linked in the import/call graph?).
- **Functional**: Utility proof (Is it actually used, or is it dead/redundant code?).
- **Empirical**: Resistance proof (Does removing it actually break the system?).

## 2. The 16 Verification Cells

| Granularity | Surface (Cell) | Structural (Cell) | Functional (Cell) | Empirical (Cell) |
| :--- | :--- | :--- | :--- | :--- |
| **L0 Dir** | 1. PROOF.md exists | 2. Dir Relationship | 3. Redundant Dirs | 4. Dir Deletion test |
| **L1 File** | 5. # PROOF: header | 6. Import Analysis | 7. Unused Files | 8. File Deletion test |
| **L2 Block** | 9. docstring PROOF: | 10. Call Graph | 11. Dead Code | 12. Func Deletion test |
| **L3 Token** | 13. Naming/Conventions | 14. Variable Refs | 15. Unused Vars | 16. Var Deletion test |

## 3. Implementation Status (as of 2026-02-01)

### Phase 1: Surface & Basic Struct (Active)

- **Cells 1, 5**: Fully implemented in `mekhane.dendron.checker`.
- **Cells 9, 13**: High priority implementation (L2/L3 parsing).
- **Cell 6**: High priority (Import validation).

### Phase 2: Structural & Functional (Roadmap)

- Focus on AST-based call graph analysis to detect dead code (Cell 11) and unused variables (Cell 15).

### Phase 3: Empirical (Future)

- Automated "Chaos Engineering" for code existence. The system stashes changes, deletes a component, runs tests, and verifies failure (validating necessity).

## 4. Philosophic Impact

This matrix transforms Dendron from a documentation linter into a **Deterministic Existence Validator**. It ensures that every single token in the codebase has a traceable, non-redundant, and empirically verified reason for being.
