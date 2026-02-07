# Google Antigravity 公式ドキュメント完全版

> **取得日時**: 2026-02-05
> **バージョン**: 1.16.5
> **ソース**: <https://antigravity.google/docs>

---

## 目次

1. [Home](#home)
2. [Get Started](#get-started)
3. [Agent](#agent)
4. [Models](#models)
5. [Agent Modes / Settings](#agent-modes--settings)
6. [Rules / Workflows](#rules--workflows)
7. [Skills](#skills)
8. [Task Groups](#task-groups)
9. [Browser Subagent](#browser-subagent)
10. [Strict Mode](#strict-mode)
11. [Sandbox Mode](#sandbox-mode)
12. [MCP](#mcp)
13. [Artifacts](#artifacts)
14. [Task List](#task-list)
15. [Implementation Plan](#implementation-plan)
16. [Walkthrough](#walkthrough)
17. [Screenshots](#screenshots)
18. [Browser Recordings](#browser-recordings)
19. [Knowledge](#knowledge)
20. [Editor](#editor)
21. [Tab](#tab)
22. [Command](#command)
23. [Agent Side Panel](#agent-side-panel)
24. [Review Changes (Editor)](#review-changes-editor)
25. [Agent Manager](#agent-manager)
26. [Workspaces](#workspaces)
27. [Playground](#playground)
28. [Inbox](#inbox)
29. [Conversation View](#conversation-view)
30. [Browser Subagent View](#browser-subagent-view)
31. [Panes](#panes)
32. [Review Changes (Manager)](#review-changes-manager)
33. [Changes Sidebar](#changes-sidebar)
34. [Terminal](#terminal)
35. [Files](#files)
36. [Browser](#browser)
37. [Chrome Extension](#chrome-extension)
38. [Allowlist / Denylist](#allowlist--denylist)
39. [Separate Chrome Profile](#separate-chrome-profile)
40. [Plans](#plans)
41. [Settings](#settings)
42. [FAQ](#faq)

---

## Home

Google Antigravity is an agentic development platform, evolving the IDE into the agent-first era. Antigravity enables developers to operate at a higher, task-oriented level managing agents across workspaces, while retaining a familiar AI IDE experience at its core.

Antigravity extracts agents into their own surface and provides them the tools needed to autonomously operate across the editor, terminal, and browser emphasizing verification and higher-level communication via tasks and artifacts. This capability enables agents to plan and execute more complex, end-to-end software tasks, elevating all aspects of development, from building features, UI iteration, and fixing bugs to research and generating reports.

### Main Features

- **AI-powered IDE**: All standard AI features like Agent, Tab, and Command.
- **Asynchronous Agents**: Local agents working in parallel across workspaces.
- **Agent Manager**: A new view built around planning mode, conversation, and artifact review.
- **Multi-window**: Product includes Editor, Manager, and Browser.
- **Browser Agent**: Can actuate the browser for dev tasks like dashboard reads, SCM actions, and UI testing.

---

## Get Started

### Download

Visit [antigravity.google/download](https://antigravity.google/download).

**Supported Platforms:**

- macOS (Monterey+)
- Windows 10 (64-bit)
- Linux (glibc >= 2.28)

### Basic Navigation

| Action | Shortcut |
|--------|----------|
| Agent Manager | Cmd + E from Editor |
| Editor | "Focus Editor" from Agent Manager or Cmd + E |

---

## Agent

The Agent is the main AI functionality within Google Antigravity. It is a multi-step reasoning system powered by frontier LLMs that can reason over code, use tools (including browser), and communicate via tasks and artifacts.

### Core Components

- Reasoning model
- Tools
- Artifacts
- Knowledge
- Customizations (Modes, MCP, Rules/Workflows)

Users can spin up multiple parallel agent conversations and manage them via the Agent Manager.

---

## Models

### Reasoning Models

| Model | Description |
|-------|-------------|
| Gemini 3 Pro (high/low) | Primary reasoning |
| Gemini 3 Flash | Fast reasoning |
| Claude Sonnet 4.5 (+thinking) | Alternative reasoning |
| Claude Opus 4.5 (thinking) | Deep reasoning |
| GPT-OSS | Open source option |

### Additional Models

| Model | Purpose |
|-------|---------|
| Nano Banana Pro | Generative images/mockups |
| Gemini 2.5 Pro UI Checkpoint | Browser actuation |
| Gemini 2.5 Flash | Context summarization |
| Gemini 2.5 Flash Lite | Codebase semantic search |

---

## Agent Modes / Settings

### Conversation-Level Modes

| Mode | Description |
|------|-------------|
| **Planning** | Deep research and complex tasks via task groups and artifacts |
| **Fast** | Direct execution for simple tasks |

### Settings

| Setting | Options |
|---------|---------|
| Artifact Review Policy | "Always Proceed" or "Request Review" |
| Terminal Command Auto Execution | "Request Review" or "Always Proceed" (with allow/deny lists) |
| Non-Workspace File Access | Allows access outside the workspace (use with caution) |

---

## Rules / Workflows

### Rules

Manually defined constraints for agent behavior.

**Locations:**

- **Local**: `.agent/rules/`
- **Global**: `~/.gemini/GEMINI.md`

**Activation Methods:**

- Manual
- Always On
- Model Decision
- Glob patterns

### Workflows

Structured sequence of steps saved as markdown. Invoked via `/workflow-name`. Can be agent-generated from conversation history.

---

## Skills

Skills are open standards for extending agent capabilities using SKILL.md files.

### Locations

- **Workspace**: `.agent/skills/`
- **Global**: `~/.gemini/antigravity/skills/`

### Requirements

SKILL.md with YAML frontmatter containing:

- `name`: Skill identifier
- `description`: What the skill does

Agent discovers skills based on description and activates them when relevant.

---

## Task Groups

Used in planning mode to break down complex problems into modular subtasks.

### Features

- Summaries of changes
- Edited file lists
- Progress updates
- Pending steps highlighting (browser/terminal approvals)

---

## Browser Subagent

A specialized model for browser operations.

### Capabilities

- Clicking
- Scrolling
- Typing
- Reading logs/DOM/screenshots

### Features

- **Visual Overlay**: Blue border and action panel shown during actuation
- **Multi-tasking**: Can act on background tabs while the user works in another tab

---

## Strict Mode

Enhanced security controls for agent operations.

### Features

| Feature | Description |
|---------|-------------|
| URL Control | Enforces Allowlist/Denylist for Read URL tool and markdown images |
| Review Policies | Terminal, Browser JS, and Artifact review are all locked to "Request Review" |
| File System | Respects .gitignore and disables access outside the workspace |

---

## Sandbox Mode

Kernel-level isolation for terminal commands on macOS using Seatbelt.

### Features

- Enable/disable sandboxing per workspace
- Restrictions on file system access
- Restrictions on network access
- Violation handling and reporting

---

## MCP

Model Context Protocol integration, allowing the editor to connect to local tools and external services.

### Supported Integrations

**Databases:**

- Supabase
- BigQuery

**Productivity Apps:**

- GitHub
- Linear
- Notion

---

## Artifacts

Artifacts are anything the agent creates to communicate work or thinking.

### Types

- Markdown documents
- Diffs
- Diagrams

### Purpose

Emphasis on asynchronous communication and user feedback.

---

## Task List

A markdown-based task list used by the agent to monitor progress on complex goals.

### Phases

1. Research
2. Implementation
3. Verification

---

## Implementation Plan

How the agent architects changes.

### Workflow

1. Agent creates implementation plan
2. Users can review and comment
3. "Proceed" to allow the agent to implement

---

## Walkthrough

Summarizes completed implementations, reminding the user of changes made.

### Contents

- Summary of changes
- Screenshots (for browser tasks)
- Recordings (for UI interactions)

---

## Screenshots

The browser subagent captures pages or elements for user review.

**Format**: Saved as image artifacts

---

## Browser Recordings

Playback of agent actions in the browser.

**Format**: Saved as recording artifacts for review

---

## Knowledge

Persistent memory system (Knowledge Items) that captures insights and patterns across sessions.

### Purpose

Inform the agent's future responses based on learned context.

---

## Editor

VS Code-based entry point with AI features.

### Features

- Tab suggestions
- Integrated source control
- Agent panel

---

## Tab

Core navigation and completion tools.

| Feature | Description |
|---------|-------------|
| **Supercomplete** | File-wide suggestions |
| **Tab-to-Jump** | Logical navigation |
| **Tab-to-Import** | Auto-importing dependencies |

---

## Command

Trigger natural language requests for inline code completions or terminal commands.

**Shortcut**: CMD/CTRL + I

---

## Agent Side Panel

Panel used for conversations, attaching images, and switching agent modes/models.

---

## Review Changes (Editor)

Review file diffs and comment on changes directly within the editor's Agent panel.

---

## Agent Manager

High-level view for overseeing multiple workspaces and agents.

**Status**: Currently in public preview

---

## Workspaces

Working across multiple folder-based workspaces and starting new conversations.

---

## Playground

Independent workspaces for instant exploration.

### Features

- Quick experimentation
- Can be persisted into dedicated workspaces later

---

## Inbox

Centralized hub to track all conversations and pending approvals.

### Approval Types

- Terminal commands
- Browser use
- File changes

---

## Conversation View

Centered view for following agent progress.

### Features

- "Following" toggle
- Real-time updates

---

## Browser Subagent View

Side panel that reveals detailed subagent actions.

### Shows

- Click locations
- Screenshots
- DOM state

---

## Panes

Open and manage resizable, splittable windows.

### Content Types

- Files
- Artifacts
- Knowledge items

---

## Review Changes (Manager)

Manager-specific interface for reviewing diffs.

### Source Control Features

- Staging
- Committing
- Diff viewing

---

## Changes Sidebar

Monitor artifacts and file modifications within a conversation via the Changes Sidebar in the agent manager.

---

## Terminal

Terminal support in the manager window.

**Shortcut**: Cmd/Ctrl + J

**Note**: Attaches to the local workspace while agent terminals run in the editor.

---

## Files

File panes can be opened in the manager.

### Features

- View files
- Leave comments for the agent directly on specific points

---

## Browser

Antigravity's ability to control a Chrome browser through a subagent.

### Features

- Uses a separate browser profile for isolation
- Custom Chrome path specification if not auto-detected

---

## Chrome Extension

The Antigravity Browser Extension is required for web interaction.

### Installation

- Automatic installation on first browser use
- Manual installation available for troubleshooting

---

## Allowlist / Denylist

Security model for URL access.

| Type | Description |
|------|-------------|
| **Denylist** | Dangerous URLs blocked via server-side BadUrlsChecker |
| **Allowlist** | Trusted URLs can be added locally |

---

## Separate Chrome Profile

The agent's browser uses an isolated profile.

### Purpose

Keep personal cookies and accounts safe.

### Settings

- Change profile storage location
- Manage profile data

---

## Plans

Different usage tiers and their rate limits.

### Tiers

- Google AI Ultra
- Google AI Pro
- Free tier

**Note**: All plans include access to Gemini 3 Pro and Gemini 3 Flash.

---

## Settings

Access configuration options.

**Shortcut**: Cmd + ,

### Notable Options

- "Enable Telemetry" toggle under Account section

---

## FAQ

### Authentication

- Preferring @gmail.com accounts
- Google Workspace accounts supported

### Age Requirements

- Must be 18+

### Supported Countries

Extensive list of supported countries and territories across all continents.

---

*Document generated from antigravity.google/docs on 2026-02-05*
