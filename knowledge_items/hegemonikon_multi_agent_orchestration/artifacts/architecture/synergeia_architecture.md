# Synergeia Architecture

## 1. Overview

The Synergeia system operates as a coordinator that parses CCL expressions and allocates sub-tasks to the most appropriate execution threads based on their specialized capabilities and current load.

## 2. Temporal Layering (Sync vs Async)

Hegemonikón distinguishes between different temporal layers of cognitive execution to optimize for tool strengths and latency requirements.

| Layer | Temporal Scale | Primary Tools | Execution Paradigm |
| :--- | :--- | :--- | :--- |
| **Workflow (WF)** | Seconds to Minutes | Claude CLI, Codex, Gemini CLI | **Synchronous**: Immediate feedback loop, typically orchestrated via `/ene+`. |
| **Macro / Strategy** | 30 Minutes to Duration | **Jules**, Multi-agent Swarms | **Asynchronous**: Batch execution, Fire-and-Forget, typically triggered via `/u+` or scheduled events. |

### 2.1. Jules as a Strategic Specialist

Jules is designed for long-running, complex architectural transformations or exhaustive peer reviews.

- **Asynchronous Flow**: Tasks take 30+ minutes. Results integrated via PRs.
- **Massive Parallelism**: Pool strategy (6 accounts, 18 keys) handles high-throughput strategic tasks.

## 3. Operational Flow

1. **CCL Parsing**: Analyzing dependencies and identifying parallelizable segments.
2. **Thread Allocation**: Assigning tasks using operators like `@thread` or `@delegate`.
3. **Execution Coordination**: Managing execution through a coordinator (e.g., n8n or OpenManus).
4. **Aggregation**: Joining results from parallel (`||`) or sequential (`|>`) flows.

## 4. Distributed Operators

- `|>` (Pipeline): Sequential handoff between threads.
- `||` (Parallel): Concurrent independent execution.
- `@batch`: Asynchronous parallel processing.
- `@thread[agent]`: Explicitly target a specific engine.
- `@delegate[agent]`: Full delegation of long-running tasks.

## 5. Execution Environment Isolation

To handle multi-account scaling—particularly for Jules—the system implements:

1. **Config Directory Isolation**: Unique configuration directory per account (e.g., `~/.jules/accounts/01`).
2. **Environment Variable Injection**: `JULES_CONFIG_DIR` points to the correct account state.
3. **Concurrency Control**: Resource locks and cooldown timers ensure fair rotation.

## 6. Communication Channels

- **File System**: Persistent state transfer via Git or shared drives.
- **REST/WebSocket**: Real-time interaction between coordinator and agents.
- **Message Queues**: Asynchronous coordination via n8n or Temporal.

---
*Consolidated: 2026-02-06. Sources: strategic_layering.md, synergeia_architecture.md.*
