# Hegemonikón Platform Portability and Setup

Hegemonikón is architected to be platform-agnostic, enabling seamless transition between Cloud VMs (GCP, AWS), local machines (Debian, macOS, Windows/WSL), and edge devices. This capability is rooted in the **"Zero Design"** philosophy.

## Core Principles

- **Zero Design**: The system should have zero hard-coded dependencies on specific paths or local OS states.
- **Mnēme Portability**: Cognitive state (Handoffs, Identity Stack, Knowledge Items) must be portable as a discrete unit.
- **Environment Isolation**: Runtime-specifics (venvs, caches) are easily rebuilt, while cognitive assets are surgically synced.

## Directory Structure

To maintain portability, Hegemonikón uses the following structure:

- `~/oikos/`: The self-contained primary workspace.
- `~/oikos/hegemonikon/`: Core framework and project logic.
- `~/oikos/mneme/.hegemonikon/`: Cognitive state (identity, sessions, traces).
- `~/.gemini/antigravity/knowledge/`: Cross-session distilled knowledge base.

## Migration & Setup Guides

Individual guides for specific platforms and migration scenarios:

- **[Local Debian Setup](setup/debian_local.md)**: Bringing Hegemonikón to a local PC.
- **[GCP Linux Setup](setup/gcp_linux.md)**: Deploying on cloud infrastructure.
- **[Migration Workflows](migration/setup_workflows.md)**: Procedures for moving between environments.
- **[GCP-to-Local Case Study](migration/gcp_to_debian_case_study.md)**: Real-world troubleshooting and results (2026-02-02).
- **[RDP Client Connection](setup/rdp_client_connection.md)**: Configuring the Windows/macOS client.
- **[RDP Xfce Optimization](setup/rdp_xfce_optimization.md)**: Lightweight environment rituals and recovery.
- **[Antigravity Requirements](../../google_antigravity_platform/artifacts/setup/requirements.md)**: Specific glibc and OS version dependencies for the IDE.
- **[Hardware & Peripherals](setup/hardware_peripherals.md)**: Verified client hardware and sub-monitor selection criteria.
- **[Cross-Platform Sync](setup/cross_platform_sync.md)**: Git/RDP/Syncthing hybrid strategy for work mobility.
- **[Syncthing Device Mesh](setup/syncthing_device_mesh.md)**: 4-node "Oikos Mesh" topology and CLI configuration.
- **[RDP Failure Prevention](setup/rdp_failure_prevention.md)**: Troubleshooting Ritual for port conflicts, black screens, and IME issues.
- **[Nemo Actions Setup](setup/nemo_actions.md)**: Custom right-click menu items for the Cinnamon file manager.
- **[Post-Migration Verification](checklists/post_migration_verification.md)**: Checklist for API keys, CLI tools, and system registries.
- **[Legacy Path Regularization](../../hegemonikon_knowledge_infrastructure/artifacts/maintenance/forge_path_regularization.md)**: Removing Windows-era drive letters and legacy "Forge" structures (2026-02-05).
- **[Automation Backbone (n8n/Zapier)](../../hegemonikon_automation_backbone_n8n_zapier/artifacts/overview.md)**: Local Docker-based automation infrastructure (2026-02-06).
