# Setup Guide: GCP Linux Instance

This guide covers the initial setup of Hegemonikón on a cloud-based Linux instance (verified on Debian 12 Bookworm).

## 1. System Dependencies

Standard packages required for core operations and MCP support:

```bash
# Core
sudo apt update && sudo apt install -y python3.13 python3.13-venv git curl

# Git Identity
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"

# GitHub CLI (for PR management)
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y

# Node.js 20.x (for MCP servers)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2. Environment Initialization

### Python Virtual Environment

Hegemonikón relies on a Python 3.13 environment.

```bash
cd ~/oikos/hegemonikon
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install mcp  # Ensure SDK is present
```

### Antigravity / Doctrine

For ID-level recognition, create a `GEMINI.md` file:

```bash
mkdir -p ~/.gemini
cat <<EOF > ~/.gemini/GEMINI.md
# GEMINI.md - Hegemonikon Doctrine
**Primary Workspace**: /home/laihuip001/oikos/hegemonikon
- **Rules**: .agent/rules/
- **Workflows**: .agent/workflows/
EOF
```

## 3. Infrastructure Specifications (Typical GCP)

- **OS**: Debian GNU/Linux 12 (bookworm)
- **CPU**: e2-standard-4 (4 vCPU, 16 GB memory) recommended for development.
- **Disk**: 50GB+ balanced persistent disk.
