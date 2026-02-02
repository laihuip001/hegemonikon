# Implementation: Phase 7 — MCP Server Self-Integration

## 1. Objective
Enable the AI assistant to autonomously execute CCL workflows, compile commands, and audit results without manual CLI intervention, completing the "Self-Integrated Cognitive Loop."

## 2. Component: `mcp_server.py`
The MCP (Model Context Protocol) server exposes Hermēneus functionality to any compatible host (e.g., Antigravity IDE).

### 2.1 Available Tools
| Tool | Function | Parameters |
|:---|:---|:---|
| `hermeneus_execute` | Executes a CCL workflow with optional full verification. | `ccl`, `context`, `verify`, `stream` |
| `hermeneus_compile` | Translates CCL into structured LMQL code. | `ccl`, `target_type` |
| `hermeneus_audit` | Retrieves audit logs and verification reports. | `workflow_id`, `record_id` |
| `hermeneus_list_workflows` | Lists available workflows in `.agent/workflows/`. | N/A |
| `hermeneus_export_session` | Programmatically triggers session export (Cron-backup complement). | `session_name` |

## 3. Architecture
The MCP server acts as a thin wrapper around the `WorkflowExecutor` (Phase 6), utilizing `stdio` for communication. It leverages the `WorkflowRegistry` to dynamically discover available skills.

## 4. Initialization Logic
The server supports an "availability check" during import, ensuring the `mcp` SDK is present. If absent, it fails gracefully, allowing the core Hermēneus package to remain lightweight for non-IDE environments.

---
*Status: Verified (Production Ready) | 2026-02-01*
