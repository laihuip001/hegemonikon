# Checklist: Post-Migration Verification

After files are moved and the environment is reconstructed, use this checklist to ensure all systems are operational.

## 1. Identity & Continuity

- [x] Run `/boot` workflow.
- [x] Verify **Continuity Score** is 1.0.
- [x] Check if `values.json` and `persona.yaml` were loaded.
- [x] Verify the latest Handoff file was read correctly.

## 2. API Keys & Environment Variables

Check `.env` files and session exports:

- [x] **GOOGLE_API_KEY**: Present in `oikos/hegemonikon/.env`.
- [x] **PERPLEXITY_API_KEY**: Present in `oikos/hegemonikon/.env` (Required for research).
- [x] **ANTHROPIC_API_KEY**: (Optional) Paid login via `claude login` verified.
- [x] **OPENAI_API_KEY**: (Optional) Paid login via `codex` verified.

## 3. CLI Tools & Runtimes

Verify availability and versions:

- [x] **Python**: `python3 --version` (should be 3.11+).
- [x] **Python Packages**: `pip list | grep PyYAML` (Required for Jules Pool manager).
- [x] **Node.js**: `node --version` (should be 20.x+).
- [x] **Claude CLI**: `claude --version` (Login status: `claude login`).
- [x] **Codex CLI**: `codex --version` (See OpenAI developer portal).
- [x] **Gemini Code Assist**: (Authenticated via gcloud).
- [x] **Gemini CLI**: `gemini --version` (Login status: browser OAuth).
- [x] **Gemini 3**: Enabled via `/settings` or `settings.json` (Preview features).
- [x] **Jules CLI**: `jules remote list --session` (Login status: OAuth).
- [x] **CLI Timeouts**: Set to 600,000ms in `~/.codex/config.yaml` and `~/.gemini/settings.json`.
- [x] **gcloud**: `gcloud auth list` (Verify correct account is active).

## 4. System Registries

- [x] **tools.yaml**: Verify all MCP servers point to existing local paths.
- [x] **projects.yaml**: Verify all project paths reflect the new local `oikos` location.
- [x] **mcp_config.json**: Ensure paths are updated (use bulk replacement if necessary).

## 5. Antigravity IDE

- [x] Check that previous conversations appear in the history sidebar (Verified `.pb` copy).
- [x] Verify that Knowledge Items (KI) are searchable in the knowledge pallet.
- [x] Verify CLI login persistence (Codex/Claude).
