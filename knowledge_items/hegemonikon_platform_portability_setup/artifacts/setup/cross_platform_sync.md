# Cross-Platform Data Synchronization Strategy

This guide outlines the protocol for maintaining a seamless development environment across the **Hegemonikón Home Station (Debian)** and the **Work Laptop (Win 11 Pro)**.

## 1. System Topology (4-Node Surface Convergence)

| Node | OS | Role | Primary Apps |
| :--- | :--- | :--- | :--- |
| **Production Core** | Debian (KDE Plasma) | **Life/Soul Center (魂の中枢)** | Antigravity IDE, Synergeia, Hermeneus |
| **Execution Host** | Windows 11 | **Professional Limb (実務の手足)** | FileMaker Pro, Office Suite |
| **Reference Surface** | Android (OPPO) | **Reference Surface (静的参照)** | SNS (Slack/Discord), Research Docs |
| **Mobile Access** | Android (Pixel) | **Mobile Interface (動的介入)** | Prompt Reference, Mobile Interaction |

## 2. Synchronization Layers

| Layer | Method | Direction | Content |
| :--- | :--- | :--- | :--- |
| **Clipboard (L1)** | **xrdp (standard)** | Windows ↔ Debian | Text, Screenshots (Images) |
| **File / Data (L2)** | **Syncthing** | 4-Node Mesh | MD docs, `.fmp12`, Screenshots, PDFs |
| **Version (L3)** | **Git (GitHub)** | Windows ↔ Debian | Design Source Code, System Config |
| **Reference (L4)** | **O-Connect** | Windows ↔ OPPO | Proprietary Mobile Integration |
| **Cloud/Bulk (L5)** | **rclone** | G-Drive → Debian | Large Archives, Legacy Data Recovery |

## 3. Setup Requirements

### Git Configuration (Debian)

Initialize the work directory and push to a private repository:

```bash
# Setup work directory structure
mkdir -p ~/仕事用/{プロジェクト,設計,ダミーデータ,成果物,ドキュメント}

cd ~/仕事用
git init
git add .
git commit -m "Bootstrap work env"

# GitHub Authentication (requires gh CLI)
sudo apt-get install gh
gh auth login --web

# Create private repo and push
gh repo create work-filemaker --private --source=. --remote=origin --push
```

### Syncthing Configuration (4-Node Mesh)

Syncthing enables P2P real-time synchronization without a central cloud, utilizing the Tailscale network for secure, high-speed transfers. Unlike Obsidian Sync or OneDrive, it does not rely on a central server, ensuring privacy and lower latency between nodes.

#### 1. Shared Folder Mode (Primary Recommendation)

The simplest configuration is to designate a single "Sync Root" (e.g., `~/Sync`) and share it across all nodes. This functions like an **Obsidian Vault**, where the folder structure is preserved across all devices.

#### 2. Directory Structure Recommendation

To maintain order across all surfaces, use a consistent internal structure within the sync root:

```text
~/Sync/                    ← Syncthing Root
├── screenshots/           ← Global screenshot buffer (Instantly available on all nodes)
├── work/                  ← Active implementation projects
│   ├── FileMaker/         ← .fmp12 clones/backups
│   └── design_docs/       ← Markdown design specifications
├── prompts/               ← AI Prompt library (Create on Debian, use everywhere)
├── AI_History/            ← Linked AI chat logs (via symbolic links)
└── reference/             ← PDFs, research docs, and SNS assets
```

#### 3. AI Tool History Integration (Advanced)

To reference AI chat histories from within the Antigravity IDE, link the local history folders of Windows/Android AI apps into the Syncthing root:

```bash
# Example for a specific tool (concept)
ln -s ~/.config/chat-app/history ~/Sync/AI_History/app_name
```

#### 4. Setup by Node

#### 5. Debian (Host) Setup

```bash
# Install and enable
sudo apt install -y syncthing
systemctl --user enable --now syncthing

# Get local Device ID
syncthing --device-id

# Add remote devices via CLI (efficient method)
# Replace <ID> and <NAME>
syncthing cli config devices add --device-id "<DEVICE_ID>" --name "<NODE_NAME>"

# Create the shared folder (Local side)
# ID must be unique across the cluster
syncthing cli config folders add --id "sync" --label "Sync" --path "/home/makaron8426/Sync"

# Share the folder with the remote devices
syncthing cli config folders "sync" devices add --device-id "<DEVICE_ID>"

# Access Web UI (usually localhost:8384) for final sharing confirmation
```

#### 6. Windows (Client) Setup

1. Install via Winget: `winget install Syncthing.Syncthing`
2. Launch Syncthing and share the ID with the Debian host.
3. Designate a local sync folder (e.g., `C:\Users\you\Sync`).

#### 7. OPPO Pad (Reference) Setup

1. Install **Syncthing-Fork** (or standard) from F-Droid/Play Store.
2. Add the tablet to the Syncthing cluster.
3. Sync the `Screenshots` or `ReferenceDocs` folder for seamless cross-reading.

#### 8. Pixel 9a (Mobile Access) Setup

1. Install **Syncthing** from F-Droid or Google Play.
2. Link to the Mesh as a "Receive Only" or "Send & Receive" node.
3. Use for quick reference of prompts generated in the "Life Center" (Debian) while on the move.

## 4. Operational Workflows

### The "Seamless Production" Loop

1. **Design (Debian/RDP)**: Open Antigravity on the sub-monitor. Save design docs/prompts in the shared Sync folder.
2. **Implementation (Windows)**: Open FileMaker on the laptop screen. Reference the docs/prompts in the local Sync folder.
3. **Reference (OPPO Pad)**: Reference research or system specs directly on the tablet, synced via Syncthing.
4. **Consumption (Pixel 9a)**: Reference refined prompts or check system status via synced logs.
5. **Screenshot Handover**:
    - Take a screenshot on Debian → Save to `~/Sync/screenshots`.
    - Appears instantly on Windows (to paste into FileMaker) and OPPO/Pixel (to share on SNS).

---

### 5. Architectural Pattern: Hegemonikón as Central Hub

In this topology, the **Debian Host** is the **"Soul/Life Center" (魂の中枢)**.

- **Centralization of Truth**: All high-level reasoning, prompt engineering, and architectural designs occur on Debian.
- **Digital Sovereignty**: By using a P2P mesh (Syncthing over Tailscale), the system effectively replaces third-party cloud services like **Notion** or **Obsidian Sync**.
- **Convergence**: Any insight captured or generated in the "Hub" is instantly projected to the "Limbs" (peripheral nodes) for execution or reference.
- **Workflow Integrity**: Chat histories from various AI tools on different devices can be symbolic-linked into the Hub for a unified intellectual repository accessible via the Antigravity IDE.
- **Infrastructure Recovery**: `rclone` serves as a "surgical extraction" tool for legacy data (like AIDB) stored in cloud silos that exceed the practical handling limits of P2P meshes or manual ZIP transfers.

### 6. Setup: rclone (Google Drive Integration)

`rclone` is used as an auxiliary layer for large-scale data migration or recovery from Google Drive.

```bash
# Install
sudo apt install rclone

# Configuration
rclone config
# 1. New remote -> 'gdrive'
# 2. Type -> 'drive'
# 3. Scope -> 'drive' (1)
# 4. Use auto config -> 'n' (if on headless/different browser)
# 5. Run 'rclone authorize "drive" "..."' on browser machine
# 6. Paste token back
```

#### Remote/Headless Authorization Pattern

When configuring `rclone` on a remote server (Debian over RDP/SSH) without easy browser redirection:

1. Run `rclone config` on the target machine.
2. Select `n` for "Use auto config".
3. On a machine **with a browser**, run the authorization command provided by `rclone` (e.g., `rclone authorize "drive" "scope_token"`).
4. Authenticate in the browser, then copy the resulting JSON token from the terminal.
5. Paste the token into the `config_token>` prompt on the target machine.

#### 6.1. Usage Patterns

**Mounting Google Drive**:

```bash
mkdir -p ~/gdrive
rclone mount gdrive: ~/gdrive --daemon
```

**Copying/Syncing Data**:

```bash
# rclone copy gdrive:[folder_id] /path/to/local/target --progress
```

#### 6.3. Troubleshooting rclone Authorization

1. **"Couldn't decode response"**: This often occurs if you paste the `rclone authorize` command itself into the `config_token>` prompt instead of the JSON token result. Ensure you are copying the JSON block *starting with `eyJ0...`*.
2. **"Empty token found"**: If the authorization fails or a token is missing, run `rclone config reconnect gdrive:` to re-initiate the handshake.
3. **Headless Mismatch**: Ensure `rclone` version matches on both machines (headless target and local browser machine) to avoid encoding/decoding errors.

#### 6.4. Pattern: Recovering from the Void (Windows Recycle Bin)

When data appears "lost" during a migration from Windows to Debian (especially when using NTFS external drives), check the **Windows Recycle Bin** directory directly from Linux.

- **Observation**: Files deleted on Windows are moved to a hidden `$RECYCLE.BIN` folder on the root of the source drive.
- **Access Pattern**:

  ```bash
  # Search for raw data in the Recycle Bin
  find /media/[user]/[drive_id]/\$RECYCLE.BIN -type d -name "target_folder"
  ```

- **Constraint**: Windows uses unique SID subfolders (e.g., `S-1-5-21-...`). Data is often renamed with a `$R` prefix (e.g., `$R0JRRJY`). Manual deep inspection of these renamed subdirectories is required to verify the payload.
- **Success Case (2026-02-06)**: Recovered the entire AIDB article dataset (762 files) which had been partially deleted/abandoned on the Windows side but persisted in the disk's trash substrate.

This architecture transforms the home workstation from a mere "RDP server" into a vital nerve center for a user's entire digital existence.

---

### Key Lessons (2026-02-07 Update)

- **P2P > Cloud**: Syncthing operates locally/via Tailscale, providing lower latency and higher privacy than central servers.
- **Clipboard Unidirectionality**: While `xrdp` handles text/images well, use Syncthing for file "copies" to avoid RDP-specific transfer limitations.
- **Encryption**: Tailscale + Syncthing provides dual-layer encryption for data in transit.
- **Zombie Sync Prevention**: Always specify a subfolder (e.g., `~/Sync`) rather than the home directory to prevent accidental profile synchronization.
- **Syncthing v1.29+ CLI**: Commands evolved to nested subcommands. Use `syncthing cli config folders [id] type set sendonly` instead of the legacy flag-based syntax.

### Connectivity Troubleshooting

- **NAT-PMP Refusal**: If the local router (e.g., 192.168.1.1) refuses NAT-PMP, Syncthing will automatically fallback to **Relays**. This is normal but may slightly increase latency. To reduce log noise, NAT-PMP can be disabled in the Syncthing settings if the relay performance is acceptable.
- **Device Isolation**: If a device shows as "Disconnected", ensure **Tailscale** is active on both sides and the Syncthing user service is running (`systemctl --user status syncthing`).

### Verification

Verified by Creator: 2026-02-07 (Syncthing Mesh Fully Operational)
