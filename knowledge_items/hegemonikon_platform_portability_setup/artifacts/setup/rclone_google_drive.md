# rclone: Google Drive Integration (L5 Cloud)

## 1. Overview

**rclone** is utilized as the Layer 5 (L5) Cloud layer in the Hegemonikón environment, primarily for surgical extraction of missing raw data (e.g., AIDB articles) from Google Drive.

## 2. Remote Configuration (gdrive)

| Parameter | Value |
| :--- | :--- |
| **Remote Name** | `gdrive` |
| **Type** | `drive` (Google Drive) |
| **Scope** | `1` (Full access to all files) |
| **Authentication** | Headless / Remote Authorization |

## 3. Remote/Headless Authorization Protocol

Since the environment often lacks a local browser, headless authorization is required:

1. **Initiate**: Run `rclone config` and select `drive`.
2. **Auto Config**: Select `n` (Use cloud authorize).
3. **Command**: Run `rclone authorize "drive" --scope "drive"` on a machine WITH a browser.
4. **Token**: Paste the resulting JSON token into the headless terminal.

## 4. Troubleshooting: Shared Drives

When configuring a Shared Drive, an "empty token found" or "failed to configure" error may occur if the token is not correctly passed or if the session times out during the `Use shared drive? (y/n)` step.

**Workaround**:

- Ensure the `rclone authorize` command uses the exact scope matching the config (`drive`).
- Complete the shared drive identification immediately after pasting the token to prevent timeout.

## 5. Usage Patterns

### 5.1. Surgical Data Extraction

Used to recover AIDB articles or session logs not present in local ZIP archives.

```bash
rclone sync "gdrive:Hegemonikón/GNOSIS/AIDB" ~/oikos/mneme/.hegemonikon/aidb_recovery
```

### 5.2. Backup Orchestration

```bash
mkdir -p ~/gdrive_backup && rclone sync "gdrive:" ~/gdrive_backup --dry-run
```

---
Updated: 2026-02-06
Lineage: Migration from GCP -> Debian Local Setup
