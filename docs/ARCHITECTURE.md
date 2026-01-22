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

## 2. The 12-Function Architecture

Hegemonikón derives cognitive functions from a **2-tier axiom structure**:

### Core Axioms (Level 1)

| Axiom | Dimension A | Dimension B |
| :--- | :--- | :--- |
| **Flow** | Inference (perceive) | Action (execute) |
| **Value** | Information (epistemic) | Goal (pragmatic) |

### Choice Axioms (Level 1.5)

| Axiom | Dimension A | Dimension B |
| :--- | :--- | :--- |
| **Tempo** | Fast (reactive) | Slow (deliberative) |
| **Stratum** | Low (concrete) | High (abstract) |
| **Agency** | Self | Environment |
| **Valence** | Approach (+) | Avoid (-) |

### 12 Core Functions

```
P-series (Pure Theorems):  2 × 2 = 4 functions  ← Core × Core
M-series (Extended Theorems): 2 × 4 = 8 functions  ← Core × Choice
Total: 2² + 2³ = 12 functions
```

**M-series (Active in Phase 1)**:

| Function | Module | Role |
| :--- | :--- | :--- |
| Perception | M1 Aisthēsis | Input processing |
| Judgment | M2 Krisis | Priority decision |
| Theory | M3 Theōria | Causal modeling |
| Wisdom | M4 Phronēsis | Practical reasoning |
| Research | M5 Peira | Exploration |
| Execution | M6 Praxis | Action execution |
| Verification | M7 Dokimē | Testing |
| Memory | M8 Anamnēsis | Long-term storage |

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
| **Phase 1** | M-series (M1-M8) | ✅ Active |
| **Phase 2** | P-series (P1-P4) | 📄 Planned |
| **Phase 3** | Full 12-function integration | 📋 Future |

### Phase 1 Scope

```
Active: M1, M2, M3, M4, M5, M6, M7, M8
Planned: P1, P2, P3, P4
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
