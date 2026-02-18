# Google Antigravity Platform Intelligence

Google Antigravity is an **agentic development platform** that evolves the traditional IDE into an agent-first era. Unlike conventional AI-powered code editors, Antigravity is designed around the concept of multiple asynchronous agents working in parallel across various workspaces.

## Core Philosophy: The Agent-First IDE

Antigravity shifts the focus from a single-thread interaction model to a multi-agent orchestration model.

- **Asynchronicity**: Agents can perform tasks (coding, searching, browser interaction) in the background.
- **Multi-Window Interaction**: The platform consists of specialized windows for code editing, task management, and web actuation.
- **Artifact-Centric**: Communication between agents and the human creator is mediated by rich artifacts rather than just text chat.

## Platform Surfaces

| Surface | Purpose | Primary Interaction |
| :--- | :--- | :--- |
| **Editor** | Direct code manipulation and local AI assistance. | Coding, Tab, Command (Inline) |
| **Agent Manager** | Planning, task orchestration, and artifact review. | Planning mode, Conversation UI |
| **Browser Agent** | Web surface interaction (SCM, Documentation, Testing). | Browser actuation, Recording |

## Key Concepts

- **Agent**: The primary AI modality, capable of multi-codebase operations.
- **Tab & Command**: Inline AI features within the text editor for autocomplete and targeted edits.
- **Artifacts**: Rich output formats created by agents (Markdown, Diffs, Diagrams, Browser Recordings).
- **Workspaces**: Isolated contexts for different projects or task groups.

## Interaction Patterns

- **Cmd + E**: The primary toggle between the **Editor** (focus on implementation) and the **Agent Manager** (focus on coordination).
- **Agent Side Panel**: Provides immediate AI context within the code editor.
- **Conversation View**: A unified history of interactions and decisions.
