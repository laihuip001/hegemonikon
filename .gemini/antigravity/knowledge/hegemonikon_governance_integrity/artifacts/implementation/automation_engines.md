# Automation: Integrity & Enforcement Engines

## 1. Quality Gate Engine (`quality_gate.py`)

Handles automated verification of Metrika, Chreos, and Palimpsest standards.

### 1.1 Core Gates

- **Metrika**: Static analysis for complexity (Syntomia) and atomicity (Atomos).
- **Chreos**: Debt validation (TODO logic).
- **Palimpsest**: Identification of HACKs and magic numbers.

### 1.2 Multi-Layer Architecture

- **Δ Layer (Strategy)**: Manual checklists in the workflow.
- **τ Layer (Operational)**: Runtime alerts/linting.
- **ε Layer (Verification)**: Automated static analysis via `quality_gate.py`.

---

## 2. PROOF Header Injector (`proof_injector.py`)

Automates Structural Enforcement by ensuring all files have a valid PROOF header.

### 2.1 Logic Layers

- **L1/Axiom**: `fep_agent.py`, etc.
- **L2/System**: Configs, loggers.
- **L3/Utility**: Tests and minor tools.

### 2.2 Process

1. Detect shebang.
2. Check for existing PROOF header.
3. Map file name pattern to Level.
4. Perform atomic injection.

### 2.3 Verification

Always verify injection using `dendron check . --coverage`.

---
*Implementation Doc: 2026-02-01 | Engine Series: Mekhanē*
