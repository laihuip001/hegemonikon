# Prompt-Lang v2.x Master Specification

Prompt-Lang (`.prompt`) is a block-based syntax for defining structured prompts for AI agents.

## 1. Syntax & Directives

### Core Directives
| Directive | Status | Description |
| :--- | :--- | :--- |
| `@role` | Mandatory | Defines the AI's persona. |
| `@goal` | Mandatory | Specifies the primary objective. |
| `@constraints` | Recommended | Lists 3+ items (rules/guardrails). |
| `@format` | Mandatory | Defines output schema (JSON, MD, XML). |
| `@examples` | Recommended | Few-shot pairs. |
| `@rubric` | Optional | Self-scoring dimensions. |
| `@activation` | Optional | Trigger conditions (mode, priority). |
| `@context` | Optional | External resource references. |

### Advanced Mechanisms (v2.1+)
- **@extends (Inheritance)**: Inherit blocks from a base prompt. Child overrides singular fields and merges list/dict fields.
- **@mixin (Synthesis)**: Modular import of fragments. Left-to-right processing.
- **Conflict Resolution**: Singular fields (child overrides), List fields (append), Dict fields (merge).
- **Deletion Operator (!)**: (v2.2) Prefix `!` to remove inherited list items.

## 2. Parser Architecture

The core parser (`prompt_lang.py`) operates as follows:
1. **Parsing**: Text to AST (dataclasses: `Prompt`, `PromptBlock`).
2. **Resolution**: Apply `@extends` and `@mixin`.
3. **Context Resolution**: Fetch external data via files or MCP (`mcp:server.tool`).
4. **Evaluation**: Check environment variables for `@if/@else`.
5. **Expansion**: Compile AST into natural language (Markdown/XML).

## 3. Logic & Infrastructure Library

Standard templates injected into `@constraints` or `@think` blocks:

### 3.1 Decision Gates
- **Speed vs Quality**: Deadline dependent.
- **Refactor vs Rewrite**: Age & Coverage dependent.
- **Security vs Usability**: Sensitivity dependent.

### 3.2 Infrastructure Standards
- **Docker**: Multi-stage, Distroless/Alpine, Non-Root, Secret handled via BuildKit.
- **Kubernetes**: Mandatory Resource Limits, Probes, and Network Policies.
- **Security**: Parameterized Queries, RBAC, Argon2id/Bcrypt.

## 4. MCP Integration

`prompt_lang_mcp_server.py` exposes a `generate` tool which detects domains, selects templates, and outputs valid `.prompt` definitions tailored to requirements.
