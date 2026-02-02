# Testing: Synergeia Integration Suite

To ensure the reliability of the "Cognitive Enclosure," a dedicated integration test suite was implemented in `synergeia/tests/test_integration.py`.

## 1. Test Coverage

The suite covers three major integration axes:

### A. Hermeneus & Macro Integration

- **Import Verification**: Ensures `HERMENEUS_AVAILABLE` is True and the compiler is correctly linked.
- **Macro Loading**: Verifies that `STANDARD_MACROS` are successfully loaded from `ccl/macros/` (e.g., `think`, `scoped`).
- **Compilation Fidelity**: Tests that `execute_hermeneus` correctly uses these macros to produce LMQL code.

### B. FEP-Based Optimization

- **Selector Activation**: Confirms `FEP_SELECTOR_AVAILABLE` is True.
- **Dynamic Routing**: Validates that different CCL expressions are routed to the optimal thread based on complexity:
  - High Complexity (`/noe+ >> ...`) → `antigravity`
  - Medium Complexity (`/s+ _ /ene`) → `claude`
- **Fallback Logic**: Ensures the system reverts to rule-based selection if FEP is disabled or fails.

### C. End-to-End Pipeline

- **Integrated Flow**: Tests the full path from raw CCL input, through FEP selection, to Hermeneus compilation.
- **State Verification**: Verifies that the generated LMQL contains specific constructs like `convergence_loop` for relevant inputs.

## 2. Test Execution

The tests are executed using standard `pytest`:

```bash
cd hegemonikon
source .venv/bin/activate
pytest synergeia/tests/test_integration.py -v
```

## 3. Results (2026-02-01)

- **Status**: ✅ 100% Pass
- **Verification**: All cross-project bridges (Synergeia ↔ Hermeneus ↔ Kernel) are verified as operational.

## 4. Structural Integrity (Dendron Verification)

As of 2026-02-01, Synergeia has achieved 100% structural verification via the Dendron v2.4 auditor.

- **Coverage**: 100.0% (7/7 files with verified PROOF tags).
- **Lineage**: Deductive Necessity confirmed via parent references (`<- synergeia/`).
- **Semantic Consistency**: Verified via the "Obsessive Audit" protocol (Round 6).

---
*Reference: mekhane.dendron check synergeia/ --ci*
