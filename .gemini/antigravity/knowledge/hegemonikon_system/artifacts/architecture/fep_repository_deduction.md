# FEP-Based Repository Structure Deduction

> **Methodology**: Axiomatic Deduction from the Free Energy Principle (FEP).
> **Objective**: Eliminate arbitrariness in the repository root.

## 1. Axiom: Error Minimization

A system that minimizes variational free energy (prediction error) must maintain an internal model and interact with an environment.

## 2. Deductive Steps

### Step 1: System/Actuator Split
**Deduction**: Prediction Error minimization requires a separation between the **Internal Model** (Prediction) and **Action** (Policy).
- **`kernel/`**: The Internal Model, Immutable Truth, Theory.
- **`mekhane/`**: Action, Implementation, Mutable Execution.

### Step 2: Environmental Interface
**Deduction**: Systems interact with an environment via Input (Observations) and Output (Actions).
- **`docs/`**: Collected external information, research, and environmental knowledge.

### Step 3: Observer Necessity
**Deduction**: A system must be understandable to its observers (Human or AI) to facilitate collaborative error minimization.
- **`README.md`**: Entry point for Human observers.
- **`AGENTS.md`**: Entry point for AI observers.

### Step 4: Legal and Technical Necessity
**Deduction**: Systems exist within social and technical substrates.
- **`LICENSE`**: Social/Legal requirement.
- **`requirements.txt` / `.gitignore`**: Technical substrate requirements.

## 3. The Necessary Root Structure

The following structure is "discovered" as necessary; any other files in the root are considered "Existence Errors" and must be moved or deleted.

```text
hegemonikon/
├── README.md        # Entry: Human
├── AGENTS.md        # Entry: AI
├── LICENSE          # Legal
├── requirements.txt # Technical
├── .gitignore       # Technical
├── kernel/          # Theory: Internal Model
├── mekhane/         # Action: Implementation
└── docs/            # Environment: Knowledge
```

## 4. Discovery vs. Design

This derivation proves that the repository structure is not a matter of "design preference" but a logical consequence of FEP. This discovery allows for the automated pruning of non-essential files, directly reducing the cognitive load (complexity) of the system.
