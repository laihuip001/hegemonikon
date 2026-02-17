# Hegemonikón Integration Patterns for Opus 4.6

The unique capabilities of Opus 4.6 provide several optimization paths for the Hegemonikón system.

## 1. Context Engineering (CE) Optimization

### 1.1 One-Shot World-Context

With the **1M token context**, the `/boot` workflow can transition from a tiered, incremental loading process to a comprehensive "One-Shot World-Context" injection.

- **Pattern**: Inject the entire current state of Mnēme and Sophia into the system prompt for deep reasoning sessions (`/effort max`).
- **Benefit**: Zero loss of context across the multi-agent stack.

### 1.2 Context Compaction for Long Missions

Hegemonikón's long-running tasks (like `/eat` on large archives or complex `/mek` refactoring) should leverage **Context Compaction**.

- **Implementation**: Set a threshold at 50k tokens to trigger summaries. This ensures the "Active Intent" (Boulēsis) is preserved while old logs are archived into summary nodes.

## 2. Multi-Agent Orchestration

### 2.1 Synergeia Agent Teams

Opus 4.6's **Agent Teams** pattern matches the Hegemonikón "Tiered Specialist" model.

- **Pattern**: Use the "Lead Agent" to define the task architecture, then spawn "Specialist Agents" (e.g., GH-01 for Code, HG-02 for Architecture) as parallel sub-instances.
- **Coordination**: Use the shared filesystem/Syncthing mesh as the "Ground Truth Area" while agents communicate via an orchestrator node.

### 2.2 Adaptive Thinking for Task Gating

The `/effort` parameter allows for granular resource management.

- **Low Effort**: Use for `/check`, simple file edits, or status updates.
- **Medium/High Effort**: Default for standard `/mek` and `/tak` tasks.
- **Max Effort**: Reserved for `/noe` (Noesis), complex architectural diorthosis, or resolving high-entropy conflicts.

## 3. Computer Use & Tooling

### 3.1 Visual Ground-Truth Loop (VGT-Loop)

Leverage improved **Computer Use** (72.7% on OSWorld) for automated FileMaker or RDP validation.

- **Strategy**: Have the agent autonomously open RDP windows, take screenshots via `xfce4-screenshooter`, and verify the visual state of the MICKS Business System layouts against the documentation.

## 4. Zero-Entropy Preprocessing

The model's improved ability to "plan before acting" and "catch its own mistakes" should be used to enforce stricter **Zero-Entropy Preprocessing**.

- **Standard**: Every `/tak` command must be preceded by an autonomous `Adaptive Thinking` phase where the model simulates the outcome and checks for edge cases before any file write.
