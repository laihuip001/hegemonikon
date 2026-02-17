# Case Study: GCP VM to Local Debian Migration (2026-02-02)

This case study documents the final migration of the Hegemonikón environment from a GCP VM (`hegemonikon` instance) to a local Debian PC.

## Background

- **Source**: GCP VM (Debian 12), Primary User: `laihuip001`
- **Destination**: Local PC (Debian 12), Primary User: `makaron8426`
- **Objective**: Full cognitive continuity (Score 1.0) and cleanup of cloud resources.

## 1. Remote Discovery & Path Validation

A common hurdle in migration is discovering that the data is stored under a different system user than expected.

- **Initial Assumption**: Data was at `/home/makaron8426/`.
- **Discovery**: `ls /home/` revealed the actual user was `laihuip001`.
- **Action**: Corrected all `gcloud compute scp` paths to `/home/laihuip001/`.
- **MCP Discovery**: Initially failed to find `mcp_config.json` in `~/.gemini/`. Discovery revealed it was nested at `/home/laihuip001/.gemini/antigravity/mcp_config.json`. This required a targeted `scp` and path update.

## 2. Data Selection Logic (Cognitive Priority)

During migration, a distinction was made between "Cognitive Assets" and "Runtime Artifacts."

### ✅ Migrated (High Priority)

- **Knowledge Items (KI)**: `~/.gemini/antigravity/knowledge/`.
- **Identity Stack**: `mneme/.hegemonikon/identity/` (`values.json`, `persona.yaml`).
- **Episodic Memory**: `mneme/.hegemonikon/sessions/` (Handoff files).
- **Traces & Beliefs**: `mneme/.hegemonikon/meaningful_traces.json`, `doxa_beliefs.json`.
- **Conversations**: `~/.gemini/antigravity/conversations/*.pb`. Initially skipped, but eventually migrated (9.2MB) to ensure historical brain state availability in the local IDE.
- **Tool Configs**: `~/.claude/` (Claude Code settings) migrated.

### ❌ Not Migrated (Low Priority/Binary)

- **Cache/Venvs**: `.venv`, `.cache`, `.dspy_cache`. These are rebuilt locally to ensure binary compatibility.
- **Missing Source**: `.codex/` (was not found on the GCP instance user directory).

## 3. Troubleshooting & Permission Issues

### 3.1 `knowledge.lock` Permission Denied

During `scp` of the KI directory, the `knowledge.lock` file often errors with "Permission denied."

- **Insight**: This is normal; the file is held by the active IDE.
- **Resolution**: Ignore and continue; the rest of the KI data transfers correctly.

### 3.2 `Permission denied` on Hidden Tool Directories

Attempting to `scp` directories like `.claude/` or `.gemini/.../conversations/` initially failed with `remote readdir Permission denied`.

- **Cause**: Standard `gcloud compute scp` lacks permissions for directories owned by processes or with restrictive user-level permissions.
- **Workaround**: Executed `sudo chmod -R 755` on the remote GCP instance via SSH before running the `scp` command.
- **Result**: Successfully copied `~/.claude/` and conversation history.

## 4. Continuity Verification

After migration, the `/boot` workflow was executed on the local PC.

- **Identity Stack**: Loaded successfully.
- **Handoff**: Read the final GCP session (2026-02-01).
- **Continuity Score**: **1.0** achieved.
- **Infrastructure**: Node.js 20.x installed local; MCP configuration successfully re-mapped and active.
- **Final Integration**: Codex CLI and Claude Code CLI successfully installed and authenticated via paid account logins, bypassing the need for explicit API keys in `.env` for these specific tools.
- **Decommissioning**: The GCP instance `hegemonikon` is confirmed ready for deletion as all cognitive state and tool configurations have been successfully bridged to the local Debian environment.
- **Outcome**: The local Debian environment is now the primary "Oikos" for Hegemonikón, with full cognitive continuity and enhanced developer tooling.

## 5. Cloud Resource Deletion Checklist

Before deleting the GCP instance:

1. [x] Verify local `values.json` and `persona.yaml` content.
2. [x] Check `meaningful_traces.json` for emotional continuity.
3. [x] Confirm that the `oikos` directory passes `git status` check.
4. [x] Verify `gcloud compute scp` completion for KI.
5. [x] Migrate conversation history (`.pb` files) and verify count.
6. [x] Verify `.claude/` settings availability.
7. [x] Install Node.js 20.x and verify `npm` availability.
8. [x] Authenticate with Codex CLI and Claude CLI (using accounts, skipping keys).
