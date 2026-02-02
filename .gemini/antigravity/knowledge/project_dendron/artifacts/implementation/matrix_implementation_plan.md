# Dendron 4x4 Matrix Implementation Plan

This document outlines the phased implementation of the 16-cell verification matrix.

## 1. Implementation Roadmap

### Phase 1: Surface Extension (L2 & L3)

**Objective**: Parse block-level and token-level proofs.

- **Task 1.1**: AST parsing for docstrings in `checker.py`.
- **Task 1.2**: Regex-based verification for `PROOF:` strings inside docstrings (Cell 9).
- **Task 1.3**: Naming convention validator (Cell 13).

### Phase 2: Structural Validation (L1)

**Objective**: Ensure files are correctly linked.

- **Task 2.1**: Import crawler. Check if the parent dir referenced in `# PROOF: <- parent` actually contains the file or imports it (Cell 6).
- **Task 2.2**: Cross-reference directory `PROOF.md` with contained files (Cell 2).

### Phase 3: Functional & Dead Code

**Objective**: Detect redundant code.

- **Task 3.1**: Integrate `vulture` or custom AST crawler to detect dead functions (Cell 11).
- **Task 3.2**: Detect unused files (Cell 7).

### Phase 4: Empirical Sandbox

**Objective**: Validate necessity through failure.

- **Task 4.1**: Scripted deletion experiment. Git stash -> rm target -> pytest -> report -> stash pop (Cells 4, 8, 12, 16).

## 2. CI Strategy

As specified in [Integration and Automation](./integration_and_automation.md), the CI will transition to a matrix strategy to handle these checks independently:

```yaml
strategy:
  matrix:
    layer: [surface, structural, functional]
    depth: [L0, L1, L2, L3]
```

## 3. Priority Order

1. **Surface L2/L3**: 100% visibility of necessity claims.
2. **Structural L1**: Verification of claims.
3. **Functional L2**: Cleanup of the codebase.
4. **Empirical**: Final hardening.
