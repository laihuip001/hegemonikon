# Agent Capabilities

## The Agent

The Agent is the main AI functionality within Google Antigravity. It is a multi-step reasoning system powered by frontier LLMs that can reason over code, use tools (including browser), and communicate via tasks and artifacts.

### Core Components

- Reasoning model
- Tools
- Artifacts
- Knowledge
- Customizations (Modes, MCP, Rules/Workflows)

Users can spin up multiple parallel agent conversations and manage them via the Agent Manager.

---

## Reasoning Models

- **Primary Models**: Gemini 3 Pro (high/low), Gemini 3 Flash, Claude Sonnet 4.5 (+thinking), Claude Opus 4.5 (thinking), GPT-OSS.
- **Support Models**:
  - **Nano Banana Pro**: Generative images/mockups.
  - **Gemini 2.5 Pro UI Checkpoint**: Browser actuation.
  - **Gemini 2.5 Flash**: Context summarization.
  - **Gemini 2.5 Flash Lite**: Codebase semantic search.

---

## Conversation-Level Modes

- **Planning**: Deep research and complex tasks via task groups and artifacts.
- **Fast**: Direct execution for simple tasks.
- **Settings**:
  - **Artifact Review Policy**: "Always Proceed" or "Request Review".
  - **Terminal Command Auto Execution**: "Request Review" or "Always Proceed" (with allow/deny lists).
  - **Non-Workspace File Access**: Allows access outside the workspace (use with caution).

---

## Rules & Workflows

- **Rules**: Manually defined constraints (Local in `.agent/rules` or Global in `~/.gemini/GEMINI.md`). Activation via Manual, Always On, Model Decision, or Glob patterns.
- **Workflows**: Structured sequence of steps saved as markdown. Invoked via `/workflow-name`. Can be agent-generated from conversation history.

---

## Skills

Skills are open standards for extending agent capabilities using `SKILL.md` files.

- **Locations**: Workspace (`.agent/skills/`) or Global (`~/.gemini/antigravity/skills/`).
- **Requirements**: `SKILL.md` with YAML frontmatter (name, description).
- **Usage**: Agent discovers skills based on description and activates them when relevant.

---

## Task Groups

Used in planning mode to break down complex problems into modular subtasks. Features:

- Summaries of changes
- Edited file lists
- Progress updates
- Highlighted pending steps (e.g., browser/terminal approvals) for review.

---

## Browser Subagent

A specialized model for browser operations (clicking, scrolling, typing, reading logs/DOM/screenshots).

- **Visual Overlay**: Blue border and action panel shown during actuation.
- **Multi-tasking**: Can act on background tabs while the user works in another tab.
