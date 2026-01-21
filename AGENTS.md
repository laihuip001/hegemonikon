# Hegemonikón: AI Agent Guidelines

> **Note**: This document is the "Instruction Manual" for AI agents (Claude, Gemini, Copilot, etc.) working on this repository.
> **Read Also**: [docs/STRUCTURE.md](docs/STRUCTURE.md) for detailed architecture.

## 1. Project Overview

**Hegemonikón** is an AI-Native Cognitive Architecture and Development Environment based on the **Free Energy Principle (FEP)**. It serves as the user's "Second Brain" and "Exocortex", integrating knowledge management, code execution, and agentic workflows.

### Core Philosophy
- **Minimizing Free Energy**: The system aims to minimize surprise and uncertainty for the User (Creator).
- **Environment over Will**: Reliability is achieved through environmental constraints and automated checks, not "willpower".
- **Zero Entropy**: Ambiguity is the enemy. Structure is beauty.

## 2. Technical Stack

- **Core Languages**: Python (3.10+), PowerShell (Core 7.4+), Markdown (Obsidian flavored).
- **Data Store**: LanceDB (Vector/Relational), JSON/YAML (Config).
- **Environment**: Windows 11 (Termux/WSL compatible logic).
- **Key Libraries**: `boto3`, `langchain`, `lancedb`, `pydantic`.

## 3. Repository Structure

This repository follows a 4-Layer Architecture:

- **`kernel/`**: **IMMUTABLE**. Theoretical foundations and core axioms. Do NOT modify without explicit authorization.
- **`.agent/`**: **The "Brain"**. Contains:
  - `workflows/`: Automated procedures (e.g., `/boot`, `/ask`, `/plan`).
  - `skills/`: M-Series (M1-M8) and P-Series (P1-P4) cognitive modules.
  - `rules/`: Operational constraints (including `GEMINI.md` rules).
- **`forge/`**: **The "Hands"**. Tools, scripts, and product implementations (e.g., Gnōsis, Chat History DB).
- **`docs/`**: Documentation and architectural maps.

## 4. Critical Boundaries (Traffic Light System)

### 🔴 RED: DO NOT TOUCH (Explicit Approval Required)

| Target | Reason |
| :--- | :--- |
| `kernel/` | Theoretical core. Changes break axioms. |
| `.gemini/GEMINI.md` | Identity definition. |
| `.agent/rules/CONSTITUTION.md` | Immutable constraints. |
| `config.json`, `.env*` | Secrets and environment. |
| Any `rm -rf` or destructive commands | Data loss risk. |

### 🟡 YELLOW: CAUTION (Verify Before Changing)

| Target | Guidance |
| :--- | :--- |
| `.agent/workflows/*.md` | Test after changes. Affects all sessions. |
| `.agent/skills/*/SKILL.md` | Verify M-series dependencies. |
| `forge/gnosis/` | Run tests: `python -m pytest forge/gnosis/tests/` |
| `vault/`, `gnosis_data/` | Backup before modification. |

### 🟢 GREEN: SAFE TO MODIFY

| Target | Notes |
| :--- | :--- |
| `docs/` | Documentation is always safe. |
| `forge/scripts/` | Utility scripts. Test after changes. |
| `runtime/antigravity/playground/` | Experimental area. |
| `archive/` | Historical records. |

## 5. Operational Rules for Agents

### 5.1 Language & Communication
- **User Communication**: MUST be in **Japanese** (unless explicitly requested otherwise).
- **Code & Identifiers**: MUST be in **English**.
- **Commit Messages**: English (Imperative mood, e.g., "Add feature X").

### 5.2 File Operations
- **Absolute Paths**: Always use absolute paths (e.g., `M:\Hegemonikon\...`).
- **Safety First**: Use `list_dir` or `find_by_name` to verify paths before reading/writing.
- **Backups**: Major changes should refer to `M6 Praxis` safety protocols (backup/restore).

### 5.3 Kernel Protection
- **`GEMINI.md`** and **`kernel/`** directory are **SACRED**.
- Modification requires **Explicit User Approval**.

## 6. Build, Test & Lint Commands

```powershell
# Gnōsis CLI
python m:/Hegemonikon/forge/gnosis/cli.py --help
python m:/Hegemonikon/forge/gnosis/cli.py check-freshness

# Chat History Sync
python m:/Hegemonikon/forge/scripts/sync_chat_history.py

# Linting (if configured)
ruff check forge/

# Tests
python -m pytest forge/gnosis/tests/ -v
```

## 7. Key Workflows (The "How-To")

Agents should recognize and utilize these standardized workflows:

| Command | Purpose | Module |
| :--- | :--- | :--- |
| `/boot` | Session initialization | M1 + M8 |
| `/ask` | Research inquiry generation | M5 Peira |
| `/plan` | Architectural design | M4 Phronēsis |
| `/code` | Implementation protocol | M6 Praxis |
| `/rev` | Daily review | M7 Dokimē |
| `/rec` | Memory refresh | M8 Anamnēsis |

## 8. Common Tasks

### Adding a New Workflow
1. Create `new-workflow.md` in `.agent/workflows/`.
2. Follow YAML frontmatter format (see existing workflows).
3. Test manually before committing.

### Adding a New Skill
1. Create folder in `.agent/skills/m{N}-{name}/`.
2. Add `SKILL.md` with standard format.
3. Update `docs/STRUCTURE.md` module table.

### Updating Gnōsis Knowledge Base
```powershell
python m:/Hegemonikon/forge/gnosis/cli.py collect -s arxiv -q "query" -l 10
```

## 9. Debugging Tips

| Symptom | Likely Cause | Solution |
| :--- | :--- | :--- |
| Workflow not recognized | File not in `.agent/workflows/` | Check path and filename |
| Gnōsis returns empty | DB not populated or stale | Run `collect-all` command |
| Memory not loading | `.hegemonikon/` files missing | Check `M:\Documents\mine\.hegemonikon\` |
| LanceDB errors | Version mismatch | `pip install --upgrade lancedb` |

## 10. Development Status (Phase 1)

- **Focus**: Stabilizing the Core Architecture and Workflows.
- **Active Products**:
  - **Gnōsis**: Knowledge Base (RAG).
  - **Antigravity**: Agent Runtime.
