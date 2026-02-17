# Setup Guide: Local Debian PC

- **Host**: Local Debian PC (Oikos Hub)
- **Status**: Active (Migrated from GCP)
- **Agent Capabilities**:
  - Full local file system access (`~/oikos`, `~/mneme`).
  - **RESTRICTION**: No `sudo` / root permission (`NO_NEW_PRIVS` flag set or containerized restriction).
  - **Mitigation**: Critical system-level updates/installs (Docker, apt) must be performed by the Creator via local terminal or RDP.

Migrating from GCP to a local Debian machine requires specific adjustments to ensure the "Oikos" remains functional.

## 1. Environment Reconstruction

After downloading the `oikos` directory (e.g., via tarball or `gcloud scp`), perform the following:

### Python venv Refresh

Binary dependencies in `.venv` are often platform-specific. Rebuild them:

```bash
cd ~/oikos/hegemonikon
rm -rf .venv  # Remove old GCP venv if present
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Path Virtualization (System-wide)

If your local username differs from the GCP username (e.g., `/home/laihuip001/` vs `/home/makaron8426/`), update all relevant configuration files:

```bash
cd ~/oikos

# Update paths in code, json, and config files (recursive)
find . \( -name "*.py" -o -name "*.json" -o -name "*.yaml" -o -name "*.sh" \) \
  -not -path "./.venv/*" \
  -exec grep -l '/home/laihuip001/' {} \; \
  | xargs sed -i 's|/home/laihuip001/|/home/makaron8426/|g'
```

## 2. Antigravity & Git-ignored Files

Several critical system components are typically git-ignored and must be transferred manually:

- **.agent/**: Contains workflows (`/boot`, `/noe`) and skills.
- **.gemini/antigravity/**: Contains the Knowledge Base (KI) and conversation Brain.
- **GEMINI.md**: The system's identity doctrine (may be in root or `~/.gemini/`).

### Transfer via Antigravity Editor (Recommended)

1. **Archive on GCP VM**:

   ```bash
   tar -czvf ~/oikos/Downloads/antigravity-files.tar.gz \
     .agent/ \
     .gemini/antigravity/knowledge/ \
     .gemini/antigravity/mcp_config.json \
     mneme/.hegemonikon/
   ```

2. **Download**: In the Antigravity file explorer, right-click `Downloads/antigravity-files.tar.gz` and select **Download**.
3. **Deploy on Debian**:

   ```bash
   tar -xzvf ~/Downloads/antigravity-files.tar.gz -C ~/oikos/
   ```

> [!WARNING]
> The `.gemini/antigravity/` directory can be large (e.g., 1.1GB+) as it stores all historical conversation state and knowledge artifacts.

## 2. Secrets Management

Secrets (like `.env` files) are not tracked by Git and must be manually verified.

- **File**: `~/oikos/hegemonikon/hermeneus/.env`
- **Required Keys**: `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY` (if used).

## 3. Verification Suite

Run a minimal test pass to ensure the local environment is correctly configured:

```bash
cd ~/oikos/hegemonikon
source .venv/bin/activate
# Run quick tests (requires pytest)
pytest tests/ -x -q
```

## 4. Hardware/OS Specifics

Local Debian setups benefit from direct hardware access.

- Ensure `n8n` or other automation tools are configured for the local IP if they were cloud-bound previously.
- Update local firewall (`ufw`) to allow necessary ports for MCP or Synergeia communication.

## 5. Data Analysis Dependencies

For projects involving automated analysis of Excel files (e.g., project specifications), additional system-level Python packages are required.

```bash
# Install pandas and openpyxl via system package manager for stability
sudo apt-get update && sudo apt-get install -y python3-pandas python3-openpyxl
```

> [!NOTE]
> System-level installation is preferred over `pip` on Debian 13 "Trixie" to avoid "externally-managed-environment" errors when global access is needed for scripts.

## 6. Maintenance Log

### 2026-02-05: System-wide Upgrade

- **Antigravity CLI**: Updated from `1.15.8-1769233008` to `1.16.5-1770081357`.
  - **Performance**: Optimized @-mention search speed in Agent Manager.
  - **Features**: "Secure Mode" feature renamed.
- **Google Cloud CLI**: Updated `google-cloud-cli` and `google-cloud-cli-anthoscli` to v555.0.0.
- **Environment**: Debian Trixie (testing).
- **Procedure**: Successful `sudo apt update && sudo apt upgrade -y`.

## 7. Administrative Efficiency: Passwordless Sudo

To enable seamless background agent operations and remote automation via SSH/RDP without manual password prompts, configure `NOPASSWD` for the primary user.

### Configuration

The most robust way to do this is to add a dedicated file in `/etc/sudoers.d/`:

```bash
# Replace 'makaron8426' with your actual username
echo "makaron8426 ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/makaron8426
```

### Security Consideration

While this reduces friction, it increases risk if the account is compromised. Ensure the system is protected by **Tailscale** and that SSH keys are used for remote access instead of passwords where possible.

## 9. Desktop Environments (DE) & Customization

As documented in the Feb 2026 session, the Hegemonikón Debian host uses a hybrid DE strategy to balance local aesthetics and RDP stability.

### Hybrid Strategy

| Context | DE | Status |
| :--- | :--- | :--- |
| **Local Session** | **GNOME** / **KDE Plasma** | Modern UI, full HW acceleration |
| **RDP Session** | **Xfce** | Optimized for low bandwidth, stable |

### KDE Plasma Installation

Installed for testing modern desktop capabilities alongside GNOME.

```bash
sudo apt install -y kde-standard sddm
# During install, select 'sddm' as the default display manager
```

### GNOME Customization

To optimize the default local workflow, several shell extensions are used:

1. **Extension Manager**: `sudo apt install gnome-shell-extension-manager`
2. **Dash to Dock**: For macOS-like navigation.
3. **AppIndicator/KStatusNotifierItem**: For system tray icons.
4. **Caffeine**: To prevent sleep during long-running tasks.

## 10. Peripheral Hardware (RTX 2070 SUPER)

Specific optimization for local LLM execution:

- **Quantization**: Always use 4-bit (bitsandbytes) for 7B models on 8GB VRAM.
- **Model Choice**: 1.5B (Qwen) for background logic, 7B (Mistral) for steering/reasoning tasks.
