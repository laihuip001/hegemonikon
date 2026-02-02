# Implementation: Session Export Reliability System

## 1. Context
The "Agent Skip" problem was identified where the AI assistant occasionally skips the manual chat export step in the `/bye` workflow, leading to session loss. A structural solution was implemented to ensure 100% persistence.

## 2. Double-Export Strategy
Two parallel mechanisms ensure that session data is never lost:

### 2.1 Cron-Based Auto-Export (`auto_export.sh`)
A shell script was created and scheduled via Cron to run every hour. 
- **Script**: `mekhane/anamnesis/auto_export.sh`
- **Schedule**: `0 * * * *` (Hourly)
- **Logic**: Checks if the Antigravity CDP port (9222) is active. If so, it runs `export_chats.py --all` to preserve all active sessions.

### 2.2 MCP Programmatic Tool (`hermeneus_export_session`)
A new tool was added to the Hermeneus MCP server to allow the AI to trigger exports directly.
- **Tool Name**: `hermeneus_export_session`
- **Instruction**: Mandated in `bye.md` via a `[!CAUTION]` block. The AI must call this tool at the start of any termination sequence.

## 3. Workflow Hardening
The `/bye` workflow in `bye.md` was updated with a high-visibility warning:
> [!CAUTION]
> **This step is absolutely mandatory. Execute immediately without seeking user confirmation.**

---
*Updated: 2026-02-01 | Hermeneus Reliability v0.7.5*
