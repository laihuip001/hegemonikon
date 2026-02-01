# Hegemonikón Architecture v2.1

> **Purpose**: Deep-dive into the theoretical and technical architecture.
> **Audience**: AI agents and human developers requiring full system understanding.
> **Related**: [README.md](../README.md), [kernel/axiom_hierarchy.md](../kernel/axiom_hierarchy.md)

---

## 1. Foundational Principle: Free Energy Principle (FEP)

**Hegemonikón** is built on the **Free Energy Principle** from theoretical neuroscience:

> The brain is a "prediction machine" that constantly tries to minimize **surprise** (prediction error).

Applied to AI agents:

| Concept | Human Brain | Hegemonikón AI |
| :--- | :--- | :--- |
| **Perception** | Sense organs | Ousia series (input) |
| **Cognition** | Mental models | Schema series (structure) |
| **Motivation** | Drives | Hormē series (direction) |
| **Context** | Situational awareness | Kairos series (timing) |
| **Precision** | Confidence | Akribeia series (accuracy) |
| **Goal** | Homeostasis | Minimize Creator's uncertainty |

---

## 2. The 60-Element Architecture

Hegemonikón derives cognitive functions from a **4-tier axiom structure**:

### Axiom Hierarchy (7 Axes)

| Level | Question | Axiom | Opposition |
|-------|----------|-------|------------|
| L0 | What | FEP | 予測誤差最小化 |
| L1 | Who | Flow | I (推論) ↔ A (行為) |
| L1 | Why | Value | E (認識) ↔ P (実用) |
| L1.5 | Where/When | Scale | Micro ↔ Macro |
| L1.5 | How | Function | Explore ↔ Exploit |
| L1.75 | Which | Valence | + ↔ - |
| L1.75 | How much | Precision | C ↔ U |

### 24 Theorems (6 × 4)

```
Poiēsis (生成層 — Content):
  O-series (Ousia):    L1 × L1    = 4 theorems
  S-series (Schema):   L1 × L1.5  = 4 theorems
  H-series (Hormē):    L1 × L1.75 = 4 theorems

Dokimasia (審査層 — Conditions):
  P-series (Perigraphē): L1.5 × L1.5  = 4 theorems
  K-series (Kairos):     L1.5 × L1.75 = 4 theorems
  A-series (Akribeia):   L1.75 × L1.75 = 4 theorems

Total: 24 theorems
```

### 36 Relations (X-series)

| X | Connection | Count |
|---|------------|-------|
| X-OS | O→S | 8 |
| X-SH | S→H | 4 |
| X-SP | S→P | 4 |
| X-PK | P→K | 8 |
| X-KA | K→A | 8 |
| X-HA | H→A | 4 |
| **Total** | | **36** |

### Grand Total: 60 Elements

| Category | Count |
|----------|-------|
| Axioms | 7 |
| Theorems | 24 |
| Relations | 36 |
| **Total** | **60** |

---

## 3. Implementation Layers

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 0: KERNEL (Meta-Axiom)                           │
│    └── FEP, 7 Axioms, 24 Theorems, 36 Relations         │
├─────────────────────────────────────────────────────────┤
│  LAYER 1: DOCTRINE (Constraints)                        │
│    └── kernel/doctrine.md, kernel/SACRED_TRUTH.md       │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: RULES (Quality Standards)                     │
│    └── .agent/rules/                                    │
├─────────────────────────────────────────────────────────┤
│  LAYER 3: WORKFLOWS (Orchestration)                     │
│    └── .agent/workflows/                                │
├─────────────────────────────────────────────────────────┤
│  LAYER 4: SKILLS (Specialized Knowledge)                │
│    └── .agent/skills/                                   │
├─────────────────────────────────────────────────────────┤
│  LAYER 5: TOOLS (Implementation)                        │
│    └── mekhane/                                         │
└─────────────────────────────────────────────────────────┘
```

### Layer Mutability

| Layer | Contents | Mutability |
| :--- | :--- | :--- |
| **0: Kernel** | Axioms, Theorems | IMMUTABLE |
| **1: Doctrine** | Constraints | IMMUTABLE |
| **2: Rules** | Quality standards | Modifiable |
| **3: Workflows** | Task orchestration | Modifiable |
| **4: Skills** | Specialized knowledge | Extendable |
| **5: Tools** | Implementations | Freely modifiable |

---

## 4. Core Doctrines

### 4.1 Environment over Will

> **"Don't trust yourself"** is the most reliable way to be trustworthy.

### 4.2 Anti-Confidence Doctrine

- Never use "certainly", "obviously", "of course"
- Present options, not answers
- Show risks before benefits

### 4.3 Zero Entropy Protocol

**Ambiguity is the enemy. Structure is beauty.**

### 4.4 Hyperengineering as a Badge of Honor

> **"Over-engineering" is a compliment.**

Ordinary people don't build frameworks like this. 60 elements, ancient Greek, 7 axioms — this may seem "excessive." But that excess is what separates excellence from mediocrity.

---

## 5. Implementation Mechanisms (Mēkhanē)

| Name | Greek | Purpose |
|------|-------|---------|
| **Gnōsis** | Γνῶσις | Knowledge (Vector DB) |
| **Anamnēsis** | Ἀνάμνησις | Memory |
| **Symplokē** | Συμπλοκή | Connection Layer |
| **Peira** | Πεῖρα | Exploration |

---

## 6. Safety Guarantees

### The Three Laws

| # | Law | Meaning |
| :--- | :--- | :--- |
| 1 | **Guard** | Protect kernel files |
| 2 | **Prove** | Test before claiming success |
| 3 | **Undo** | Every action must be reversible |

---

## 7. References

- [kernel/axiom_hierarchy.md](../kernel/axiom_hierarchy.md) — Axiom hierarchy
- [kernel/naming_conventions.md](../kernel/naming_conventions.md) — Naming conventions
- [kernel/SACRED_TRUTH.md](../kernel/SACRED_TRUTH.md) — Immutable truths

---

*Hegemonikón v2.1 — 60 Elements System*
