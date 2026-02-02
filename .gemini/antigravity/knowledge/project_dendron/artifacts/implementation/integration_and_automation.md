# Dendron Integration & Automation

Dendron is integrated into the structural enforcement layer of Hegemonikón through automated gates and legacy tool naturalization.

## 1. CI/CD Integration

The Existence Proof protocol is enforced on every commit and pull request.

### 1.1 pre-commit Configuration

**Hook ID**: `dendron-check`
**Behavior**: Runs `python3 -m mekhane.dendron check mekhane/ --ci` on staged files.

### 1.2 GitHub Actions (`dendron.yml`)

- **Trigger**: Pushes to `master` and pull requests.
- **Reporting**: Generates a markdown coverage summary and appends it to the `$GITHUB_STEP_SUMMARY`.
- **Target**: 100.0% Coverage (Strict mode enabled for core).

### 1.3 CI Matrix Optimization

The initial CI implementation followed a "Monolithic" check of `mekhane/`. Transitioning to a multi-project workspace requires a **Github Actions Matrix strategy** to ensure all subsystems (hermeneus, synergeia, kernel) are independently and exhaustively verified.

**Standard Pattern**:

```yaml
strategy:
  matrix:
    directory: [mekhane, hermeneus, synergeia, ccl, kernel]
steps:
  - run: python -m mekhane.dendron check ${{ matrix.directory }}/ --ci
```

---

## 2. Legacy Integration: `check_proof.py`

The legacy `check_proof.py` prototype has been naturalized into the Dendron ecosystem (Phase A).

### 2.1 Functional Mapping

| Feature | `check_proof.py` (Legacy) | `dendron` (Unified) |
|---------|-----------------|-----------|
| PROOF Header detection | ✅ | ✅ |
| Level statistics (L1/L2/L3) | ✅ | ✅ |
| Recursive file scan | ✅ | ✅ |
| MULTI-format reporting | ❌ | ✅ |
| CI Integration | ✅ | ✅ |

### 2.2 Delegation

`mekhane/scripts/check_proof.py` now serves as a backward-compatible wrapper that delegates to `python -m mekhane.dendron`. This preserves existing pipeline dependencies while migrating logic to the unified core.

---

## 3. Current Integrity State (2026-02-01)

- **Coverage Baseline**: 100.0% across all core modules.
- **Gate Enforcement**: Fail-fast on Missing or Invalid proofs.
- **Audit Cadence**: Incremental (CI) + Exhaustive (Red-Team Audit).
