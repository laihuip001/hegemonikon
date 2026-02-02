# Implementation: Double-Export System for Session Persistence

## 1. Context: The "Agent Skip" Problem

In previous versions of the Hegemonikón environment, session persistence relied on the AI agent manually executing an export script during the `/bye` sequence. Inconsistency in LLM instruction following occasionally led to "Agent Skips," resulting in the loss of valuable chat history and cognitive context.

## 2. Structural Solution: The Double-Export Architecture

As of 2026-02-01, a two-tiered reliability system ensures 100% session capture.

### 2.1 Passive Layer: Hourly Cron Job (`auto_export.sh`)

An autonomous shell script runs at the system level via Cron.

- **Location**: `/home/laihuip001/oikos/hegemonikon/mekhane/anamnesis/auto_export.sh`
- **Schedule**: `0 * * * *` (Hourly)
- **Logic**:
    1. Checks for an active Antigravity session via the CDP port (9222).
    2. If active, triggers `export_chats.py --all`.
    3. Logs results to `mneme/.hegemonikon/logs/auto_export.log`.
- **Impact**: Provides a safety net that captures work even if the agent is disconnected or fails to initiate `/bye`.

### 2.2 Active Layer: Programmatic MCP Tool (`hermeneus_export_session`)

The Hermēneus MCP server includes a dedicated tool for session management.

- **Function**: `hermeneus_export_session(session_name)`
- **Mechanism**: Subprocess call to `export_chats.py --single`.
- **Enforcement**: Defined as a **[`!CAUTION`]** (Non-negotiable) step in the `bye.md` workflow. The agent is instructed to execute this tool immediately upon receiving a terminate command, without seeking confirmation.

## 3. Impact on Subjective Continuity

The Double-Export system significantly reduces "memory decay" caused by technical failures. By ensuring the latest conversation is always available in `mneme/`, subsequent `/boot` sequences can perform high-fidelity identity stack reconstitution.

---
*Updated: 2026-02-01 | Memory Layer v5.7*
