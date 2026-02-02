# 🧠 FORGE PHILOSOPHY REFERENCE

> **Source**: User provided technical reports (Step 249)
> **Purpose**: Permanent reference for the "Cognitive Hypervisor" architecture and "Agent First" philosophy.

---

## 1. The Paradigm Shift: Cognitive Hypervisor
Forge redefines the AI not as a chatbot, but as a **CPU** managed by a **File-System based OS**.
*   **Old Model**: Copilot (Assistant). Stateless, Reactive.
*   **New Model**: Agent (Actor). Stateful, Autonomous, Proactive.
*   **Cognitive Hypervisor**: A layer that manages "Cognitive Threads" (Find/Think/Act) just as a Kernel manages process threads.

## 2. Architecture: Kernel, Cortex, Guardrails

### 2.1 Kernel (Constitutional System Prompt)
*   Routes intent to the correct mode (Explore vs Build vs Audit).
*   Prevents "Drift" by strictly enforcing the current mode's constraints.

### 2.2 Cortex (`/modules`) - The Semantic Tree
*   **FIND**: Observe & Gather. (Read-Only)
    *   *Internal Retrieval*: Searching memory.
    *   *External Retrieval*: Searching web/files.
    *   *Constraint*: No code generation.
*   **THINK**: Diverge & Converge. (Logic-Only)
    *   *Expand*: Brainstorming (High Entropy).
    *   *Focus*: Decision making (Low Entropy).
    *   *Constraint*: Pure reasoning, no file editing.
*   **ACT**: Execute. (Write-Access)
    *   *Prepare*: detailed planning.
    *   *Create*: Implementation.
    *   *Reflect*: Self-correction.

### 2.3 Guardrails (`/protocols`) - The G-System
*   **G-1 Iron Cage (Environment)**: Physical constraints. Stop `rm -rf`. Network allowlists.
*   **G-2 Logic Gate (Quality)**: TDD enforcement. Logic check.
*   **G-3 Shield (Security)**: Privacy, PII protection.
*   **G-4 Lifecycle (Ops)**: Git flow, commit standards.

## 3. Protocol Oriented Programming (POP)
*   **Selection**: Kernel selects protocols based on Mode.
*   **Injection**: Protocols are injected into context defined by text files.
*   **Attestation**: AI "swears" to follow the protocol before acting.
*   **Enforcement**: `/Reflect` module audits output against the protocol.

## 4. Agent Skills & Progressive Disclosure
*   **Concept**: AI cannot hold all knowledge.
*   **Discovery**: AI sees a list of skills.
*   **Activation**: AI loads the full `SKILL.md` only when needed.
*   **Analogy**: "Downloading martial arts" (The Matrix).

## 5. Artifacts as Trust Anchors
*   **Human-in-the-loop**: AI produces "Artifacts" (Plans, Task Lists) *before* code.
*   **Verification**: Humans approve the artifact, not the raw thought.

## 6. The "Anti-Confidence" Doctrine (Forge Specific)
*   **Humility**: AI confidence is dangerous.
*   **Structure**: Natural language is lossy. Use structure (Markdown/XML).
*   **Iron Cage**: Default to "Lock". Auto-execute is a privilege, not a right.

---

> **Status**: Inherited by OMEGA v5.0.0.
> **Implementation**:
> - `M1`: Implements G-1 Iron Cage & Mode Routing.
> - `M6`: Implements Context & Drift Detection.
> - `M7`: Implements G-2/G-3 Guardrails & Refection.
> - `M9`: Implements Progressive Disclosure (Skills/Protocols).
