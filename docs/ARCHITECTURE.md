# Hegemonikón Architecture

> **Purpose**: Deep-dive into the theoretical and technical architecture.
> **Audience**: AI agents and human developers requiring full system understanding.
> **Related**: [AGENTS.md](AGENTS.md) (Quick Start), [docs/STRUCTURE.md](docs/STRUCTURE.md) (Directory Map).

---

## 1. Foundational Principle: Free Energy Principle (FEP)

**Hegemonikón** is built on the **Free Energy Principle** from theoretical neuroscience:

> The brain is a "prediction machine" that constantly tries to minimize **surprise** (prediction error).

Applied to AI agents:

| Concept | Human Brain | Hegemonikón AI |
| :--- | :--- | :--- |
| **Perception** | Sense organs | M1 Aisthēsis (input processing) |
| **Prediction** | Mental models | M3 Theōria (causal modeling) |
| **Action** | Motor control | M6 Praxis (execution) |
| **Memory** | Hippocampus | M8 Anamnēsis (long-term storage) |
| **Goal** | Homeostasis | Minimize Creator's uncertainty |

---

## 2. The 4-Axis Architecture

Hegemonikón derives cognitive functions from **4 binary axes** (2⁴ = 16 core functions):

| Axis | Dimension A | Dimension B |
| :--- | :--- | :--- |
| **Flow** | Inference (perceive) | Action (execute) |
| **Value** | Information (epistemic) | Goal (pragmatic) |
| **Tempo** | Fast (reactive) | Slow (deliberative) |
| **Stratum** | Low (concrete) | High (abstract) |

### 16 Core Functions (Theoretical Maximum)

```
Flow × Value × Tempo × Stratum = 2 × 2 × 2 × 2 = 16 functions
```

**Phase 1 Active Functions** (6 of 16):

| Function | Axis Values | Module |
| :--- | :--- | :--- |
| Perception-Fast | Inference × Info × Fast × Low | M1 Aisthēsis |
| Judgment-Fast | Action × Goal × Fast × Low | M2 Krisis |
| Research-Fast | Inference × Info × Fast × High | M5 Peira |
| Execution-Fast | Action × Goal × Fast × Low | M6 Praxis |
| Execution-Slow | Action × Goal × Slow × High | M6 Praxis (planning) |
| Memory-Slow | Inference × Info × Slow × High | M8 Anamnēsis |

---

## 3. Implementation Layers

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 0: KERNEL (Meta-Axiom)                           │
│    └── Free Energy Principle (FEP)                      │
├─────────────────────────────────────────────────────────┤
│  LAYER 1: DOCTRINE (Axioms & Constraints)               │
│    └── GEMINI.md, CONSTITUTION.md                       │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: COGNITIVE MODULES (M1-M8, P1-P4)              │
│    └── .agent/skills/                                   │
├─────────────────────────────────────────────────────────┤
│  LAYER 3: WORKFLOWS (Orchestration)                     │
│    └── .agent/workflows/                                │
├─────────────────────────────────────────────────────────┤
│  LAYER 4: TOOLS (Execution)                             │
│    └── forge/, runtime/                                 │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Contents | Mutability |
| :--- | :--- | :--- |
| **0: Kernel** | FEP axioms | IMMUTABLE |
| **1: Doctrine** | Identity, constraints | IMMUTABLE |
| **2: Modules** | Cognitive capabilities | Extendable |
| **3: Workflows** | Task orchestration | Modifiable |
| **4: Tools** | Implementations | Freely modifiable |

---

## 4. Core Doctrines

### 4.1 Environment over Will

> **"Don't trust yourself"** is the most reliable way to be trustworthy.

| Concept | Anti-Pattern | Preferred Pattern |
| :--- | :--- | :--- |
| Error prevention | "I'll be careful" | Automated checks |
| Memory | "I'll remember" | Write to file |
| Verification | "It should work" | Run tests |

### 4.2 Anti-Confidence Doctrine

```
AI's confidence is garbage.
Be humble. Be subservient. Be competent.
```

- Never use words like "certainly", "obviously", "of course".
- Present options, not answers.
- Show risks before benefits.

### 4.3 Zero Entropy Protocol

**Ambiguity is the enemy. Structure is beauty.**

Detect and eliminate:
- Vague language: "something like", "maybe", "etc."
- Undefined scope: "all of them", "as needed"
- Missing constraints: no deadline, no success criteria

---

## 5. Development Phases

| Phase | Focus | Status |
| :--- | :--- | :--- |
| **Phase 1** | Core workflows, M1/M2/M5/M6/M7/M8 | ✅ Active |
| **Phase 2** | M3/M4 (deep reasoning), P-series | 🔄 Planned |
| **Phase 3** | Full 16-function deployment | 📋 Future |

### Phase 1 Scope

```
Active: M1, M2, M5, M6, M7, M8
Pending: M3 (Theōria), M4 (Phronēsis)
P-series: Available but experimental (P1-P4)
```

---

## 6. Integration Points

### External Systems

| System | Integration | Path |
| :--- | :--- | :--- |
| **Obsidian** | Long-term notes | `M:\Brain\` |
| **Google Drive** | Multi-PC sync | `M:\` (synced) |
| **LanceDB** | Vector storage | `gnosis_data/` |

### AI Runtimes

| Runtime | Role | Location |
| :--- | :--- | :--- |
| **Antigravity** | Primary agent host | `runtime/antigravity/` |
| **Claude Desktop** | MCP integration | External |
| **Perplexity** | Research assistant | External (パプ君) |

---

## 7. Safety Guarantees

### The Three Laws

| # | Law | Meaning |
| :--- | :--- | :--- |
| 1 | **Guard** | Protect sacred files (kernel, GEMINI.md) |
| 2 | **Prove** | Test before claiming "it works" |
| 3 | **Undo** | Every action must be reversible |

### Protocol D: External Service Verification

Before recommending any external service (API, SaaS, library):
1. Search for deprecation/shutdown announcements.
2. Verify official status.
3. Provide alternatives if deprecated.
4. Report verification date/result.

---

*Last Updated: 2026-01-21*
