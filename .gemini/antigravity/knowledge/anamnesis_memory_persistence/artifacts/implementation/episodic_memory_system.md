# Episodic Memory System: Backup, Export, and Handoff

This document integrates the technical specifications for managing Hegemonikón's episodic memory, ensuring that session experiences are preserved across transient IDE states.

## 1. Automated Episodic Backup
A tactical backup system synchronizes "Working Memory" buffers from the Antigravity IDE to the permanent `mneme/` repository.

### Infrastructure
- **Script**: `episodic_backup.sh` (using `rsync`).
- **Source**: `/.gemini/antigravity/brain/` and `knowledge/`.
- **Destination**: `/mneme/.antigravity/`.
- **Automation**: Managed via `crontab`, running hourly.
- **Stats**: Typically captures ~300+ brain files (5MB+) per session.

---

## 2. High-Fidelity Chat Export (`export_chats.py`)
The primary mechanism for "subjective" memory preservation, extracting chat logs from the IDE via DOM traversal.

### v4.5 "Progressive Collection" Architecture
- **Infrastructure**: CDP connection (9222) via Playwright.
- **Virtual Scroll Clipping Solution**: Uses a **"Scroll-While-Collect"** loop.
- **Deduplication**: Content-hashing prevents duplicate entries from overlapping scroll frames.
- **Fidelity**: Yields captured messages leap from ~5 (static snapshot) to **189+ messages** (progressive collection).
- **Hardening**: Automatically normalizes excessive blank lines produced by UI table conversions.

### Operational Repository
- **Seihon (Authority)**: `mneme/.hegemonikon/sessions/`.
- **User Access**: Symlinked to `mneme/sessions/`.
- **Watch Mode**: A "Gold Standard" recovery workflow that auto-exports whenever the active conversation changes.

---

## 3. Walkthrough & Task Export
Ensures the "How" and "What" of a session (tool outputs and checklist status) are preserved.

- **Utility**: `walkthrough_export.py`.
- **Targets**: `walkthrough.md`, `task.md`, `implementation_plan.md`.
- **Purpose**: Provides a structured, high-fidelity alternative if DOM-based export misses specific tool execution details.

---

## 4. Session Handoff v2.2
The SBAR-framed summary generated at the end of each session.

- **Convergence Check**: Uses FEP metrics (Task Uncertainty `V[]` and Will Change Rate `|/bou'|`) to audit session readiness for closure.
- **De-contextualization**: Extracts "Meaningful Moments" and "Wisdom" into universal principles for storage in the `H4 Doxa` layer.

---
*Consolidated: 2026-02-01 | Replaces automated_episodic_backup, episodic_export_and_handoff_v2, and walkthrough_export_logic.*
