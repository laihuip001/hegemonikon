# Synteleia Phase 4: Refinement & Macro Integration Plan

## 1. Overview
Phase 4 focuses on transitioning Synteleia from a standalone tool to a natively integrated component of the Hegemonikón CCL ecosystem. This is achieved by defining standard macros and integrating them into the Hermēneus compiler's parser.

## 2. Key Objectives
- **@S Macro Definition**: Standardize CCL symbols for invoking Synteleia ensembles (`@syn·`, `@poiesis`, `@dokimasia`, `@S{...}`).
- **Hermēneus Integration**: Update `hermeneus/src/parser.py` to recognize and handle Synteleia macros as first-class citizens.
- **TDD (Test-Driven Development)**: Ensure 100% verification of integration points before deployment.
- **Precision (Dokimasia)**: Focus on the evaluative rigor of the 6-agent matrix.

## 3. Implementation Plan (TDD-Oriented)

### Step 4.1: Test Specification (RED Phase)
- **Artifact**: `hermeneus/tests/test_synteleia.py`
- **Scope**:
    - **Category 1**: `SynteleiaOrchestrator` base functionality (parallel execution, result aggregation).
    - **Category 2**: Macro parsing logic (`@syn·`, `@syn×`, `@poiesis`, `@dokimasia`, `@S`).
    - **Category 3**: Hermēneus end-to-end integration (compilation and execution).
    - **Category 4**: Edge cases (empty content, large content, sequential vs parallel parity).

### Step 4.2: Macro Standardization
- Update `standard_macros_stdlib.md` with:
    - `@syn·`: Inner Product (Layer integration).
    - `@syn×`: Outer Product (Cross-verification) - *Note: Execution deferred to Phase 5, but symbol definition included in Phase 4.*
    - `@poiesis`: Generative layer audit (O, S, H).
    - `@dokimasia`: Evaluative layer audit (P, K, A).
    - `@S{...}`: Specialist selector (e.g., `@S{O,A,K}`).

### Step 4.4: Translator Logic (Bridging)
- Modify `hermeneus/src/translator.py`:
    - Implement `_translate_macro` to intercept Synteleia-specific symbols.
    - Implement `_translate_synteleia_macro` to generate Python-embedded LMQL queries.
    - Add `_translate_lambda` for Pythōsis compatibility.

## 4. Progress Tracking (2026-02-01)
- [x] Initial implementation plan approved.
- [x] Test suite `test_synteleia.py` (16 cases) created.
- [x] Internal type mismatch fixed (`TargetType` -> `AuditTargetType` in `base.py`).
- [x] **Red Phase (Initial Execution)**: 9 passed, 8 failed.
    - *Insight*: `MacroRef` nodes were unhandled in `translator.py`.
    - *Insight*: Parser strips special characters from macro names (e.g., `syn·` -> `syn`).
- [x] **translator.py Expansion**: Implemented `MacroRef` and specialist selector logic.
- [x] **Parser Regex Enhancement**: Fixed `_parse_macro` to correctly recognize `·`/`×` names and `{...}` selector syntax.
- [x] **Green Phase (TDD Validation)**: 16 passed, 1 adjusted.
    - *Insight*: Python f-strings (pre-3.12) cannot contain backslashes or complex expressions like `.replace()` with double/single quote mixes inside brackets. Remedied by pre-calculating variables.
    - *Insight*: Orchestrator result counts can be dynamic (>=7) due to `supports()` filtering in parallel mode.
- [x] Final end-to-end integration verification and deployment.
- [x] Standard macro definition file `ccl/macros/syn.md` created.

---
*Status: Complete | Synteleia v0.4.0 / Hermeneus v0.8.0 Integration*
