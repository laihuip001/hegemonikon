# Setup Guide: AI Tools & API Configuration

Hegemonikón leverages multiple Large Language Model (LLM) interfaces and developer tools. This guide details their configuration after migration.

## 1. API Keys (.env Management)

Primary keys are stored in the root `.env` of the framework.

- **Path**: `~/oikos/hegemonikon/.env`
- **Recommended Content**:

  ```bash
  GOOGLE_API_KEY=AIzaSyCYJnMGLndoL3y1AbGVfzKm6Q3hcgK3sn8  # Required for Gemini & Hermeneus
  ANTHROPIC_API_KEY=sk-ant... # Optional: Used by Synergeia
  OPENAI_API_KEY=sk-...       # Optional: Used by Codex CLI
  PERPLEXITY_API_KEY=pplx-...  # Required for /sop research workflow
  # Jules API Keys (18 accounts for high-parallelism; Ultra Tier)
  JULES_API_KEY_01=xxx
  ...
  JULES_API_KEY_18=xxx
  ```

> [!NOTE]
> If you are a paid subscriber and have performed a system-level login (e.g., `claude login`), the CLI tools may NOT require an explicit API key in the `.env` file.

## 2. Claude Code CLI

Anthropic's terminal-based coding assistant.

- **Installation**: `sudo npm i -g @anthropic-ai/claude-code`
- **Authentication**: `claude login` (or run `claude` and follow prompts).
- **Interactive Setup**: On first run, Claude asks for:
    1. **Text Style/Theme**: Multi-choice selection.
    2. **Login Method**: Choosing **Option 1 ("Claude account with subscription")** allows login via the browser, bypassing the need for a Console API key.
- **Migration Note**: Settings are typically stored in `~/.claude/`. During migration, ensure this directory is copied to maintain context across environments.

## 3. OpenAI Codex CLI

A terminal-based pair programmer powered by OpenAI Codex.

- **Documentation**: [https://developers.openai.com/codex/cli](https://developers.openai.com/codex/cli)
- **Status**: Installed globally via `sudo npm install -g @openai/codex`.
- **Authentication**: On first run, selecting **Option 1 ("Sign in with ChatGPT")** enables use via a paid plan (Plus/Pro/Team/Enterprise), removing the requirement for a separate billing API key.

## 4. Gemini Code Assist

- **Status**: Integrated via the Antigravity IDE or as a standalone extension.
- **Setup**: Ensure `gcloud auth login` is performed and the correct project is selected via `gcloud config set project [PROJECT_ID]`.

## 4.5 Gemini CLI (`gemini`)

Official command-line interface for interacting with Gemini models.

- **Installation**: `sudo npm install -g @google/gemini-cli`
- **Authentication**: Run `gemini` and follow the OAuth flow in the browser.
- **Usage**: `gemini "query"` or `gemini --help`.
- **Enabling Gemini 3**:
  - Run `/settings` within the Gemini CLI and enable "Preview features".
  - Alternatively, edit `~/.gemini/settings.json` and set `"previewFeatures": true`.
  - Restart the CLI and use `/model` to select Gemini 3 models.

## 4.6 Google Antigravity IDE & GEMINI.md

Google Antigravity is the primary AI-powered IDE for Hegemonikón development. It uses a project profile file to set the AI's persona and rules.

- **Primary Profile**: `~/.gemini/GEMINI.md`
- **Role**: This file is injected into the AI's context at the start of every session (Rules). It defines the Core Doctrine, primary workspace, and available workflows.
- **Maintenance**:
  - The file should contain an accurate list of all active workflows (e.g., the 42 commands in O/A/H/K/S/P/X series).
  - It should explicitly list "Always On" rules (like `.agent/rules/hegemonikon.md`).
- **Syncing**: During platform migration, ensure `~/.gemini/GEMINI.md` is preserved or regenerated from the framework's `.agent/` source of truth.

## 4.7 Jules CLI (`jules`)

Google's terminal-based tool for working with Jules agents and execution.

- **Documentation**: [https://jules.google/docs/cli/reference/](https://jules.google/docs/cli/reference/)
- **Installation**: `sudo npm install -g @google/jules`
- **Authentication**: `jules login` (Opens browser for Google OAuth).
- **Usage**:
  - `jules`: Launch the Interactive Dashboard (TUI).
  - `jules new "task"`: Create a new agent session.
  - `jules remote list --session`: List active sessions and their status.
- **CLI vs. API**: The Jules CLI is used for manual TUI-based dashboard interaction, while the API is used via the `mekhane/mcp/jules_mcp_server.py` for automated framework tasks.
- **Advanced: Multi-Account Dual-Access (Jules Pool)**:
  - **CLI Pool**: Managed via `synergeia/jules_api.py`. Used for manual dashboard interaction and cost-optimization (Browser OAuth).
  - **API Pool**: Uses `JULES_API_KEY_0X` in `.env`. Enables high-parallelism (300 requests/day per account, 1,800 total) and faster execution for automated framework tasks.
  - **Isolation**: Both modes use separate configuration directories (e.g., `~/.jules/accounts/01`) to maintain independent session state.

## 5. Model Context Protocol (MCP)

Hegemonikón uses MCP to grant tools access to the knowledge base (`gnosis`).

- **Configuration**: `~/.gemini/antigravity/mcp_config.json` (Primary config for Antigravity/Gemini).
- **Setup**: Configured with 7 core servers: `gnosis`, `sophia`, `jules`, `prompt-lang`, `digestor`, `hermeneus`, and `sequential-thinking`.
- **Paths**: Update all `command` and `args` paths to reflect the new local `/home/[USER]/oikos/` hierarchy, specifically pointing to `mekhane/mcp/` and `hermeneus/src/`.

## 6. Runtime Prerequisite: Node.js (Debian)

CLI tools for Claude and Codex require Node.js 20.x+.

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 6.1 Python Prerequisites (Debian)

Internal framework tools and some CLI managers (like `jules_api.py`) require Python 3.13+ and specific libraries.

- **Recommended Commands**:

  ```bash
  # Activate the primary virtual environment
  source ~/oikos/hegemonikon/.venv/bin/activate

  # Ensure python3 is used instead of the 'python' alias (or 'python' within venv)
  sudo apt install -y python3-pip
  pip install PyYAML
  ```

## 6.2 Python SDK: Google GenAI (Modern)

Hegemonikón uses the modern `google-genai` SDK (v1.60.0+) for all Gemini integrations to avoid legacy EOL (Nov 2025).

- **Installation**:

  ```bash
  pip install google-genai
  ```

- **Migration Warning**: Do **NOT** use `google-generativeai` (legacy). If found in imports, migrate to `from google import genai`.
- **References**: See `google_genai_migration` KI for implementation patterns.

## 7. CLI Performance: Timeout Configuration

To prevent premature session termination during complex reasoning or large-scale tasks, set the timeout to the maximum (10 minutes).

### OpenAI Codex CLI

- **File**: `~/.codex/config.yaml`
- **Config**:

  ```yaml
  timeout: 600000
  ```

### Gemini CLI

- **File**: `~/.gemini/settings.json`
- **Config**:

  ```json
  {
    "timeout": 600000
  }
  ```

### Claude CLI

- **Status**: No explicit timeout cap in current version; defaults to system/network limit.
