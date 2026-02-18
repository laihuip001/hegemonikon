# Agent Manager

## Overview

The Agent Manager is a high-level view (currently in public preview) for overseeing multiple workspaces and autonomous agents. It focus on coordination, long-term memory, and complex planning.

---

## Workspace Management

- **Workspaces**: Folder-based contexts for projects.
- **Playground**: Independent workspace for instant exploration; can be persisted later.
- **Inbox**: Centralized hub to track all conversations and pending approvals (terminal, browser, etc.).

---

## Views & Panes

- **Conversation View**: Centered view for following agent progress. Features a **"Following"** toggle to keep the view locked to the agent's current step.
- **Browser Subagent View**: Dedicated side panel showing click locations, screenshots, and detailed DOM/log information.
- **Panes**: Resizable and splittable windows for viewing files, artifacts, and knowledge items simultaneously.
- **Terminal**: Local workspace terminal accessible via `Cmd/Ctrl + J`. Note: Agent-specific terminals run in the Editor.

---

## Review & Monitoring

- **Changes Sidebar**: Monitor artifacts and file modifications within a specific conversation.
- **Review Manager**: Interface for reviewing diffs, staging, and committing changes.
- **File Comments**: Users can leave persistent comments for the agent directly on specific lines of code within the file panes.
