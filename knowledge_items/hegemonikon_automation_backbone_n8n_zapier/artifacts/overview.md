# Hegemonikón Automation Backbone: n8n & Zapier

## 1. Strategic Vision: The "Life Center" (人生の中枢)

Hegemonikón's automation strategy shifted on 2026-02-06 from a "Minimal Complexity" approach (cron/shell scripts) to a "High Capability" approach centered on **n8n** and **Zapier**.

### The Complexity vs. Capability Trade-off

- **Minimalist Stance**: Fear that complex automation (n8n) becomes a maintenance debt, advocating for cron + shell.
- **"Life Center" Stance**: Recognition that a backbone for 100+ service integrations and complex life-management logic is "essential" for the system's ultimate goal. The cognitive cost of learning/maintaining n8n is accepted as a necessary investment for future scaling.

## 2. Platform Architecture

### n8n (Local Debian / Docker)

- **Role**: The "Nervous System" for internal and deep integration tasks.
- **Hosting**: Self-hosted on local Debian (moving from GCP) via Docker to ensure data sovereignty and low-latency local file access.
- **Primary Use Cases**: Gnōsis knowledge collection, Perplexity digestion, session persistence, and multi-service orchestration (Slack, GitHub, local FS).

### Zapier (Cloud)

- **Role**: The "External Skin" for lightweight, cloud-native triggers.
- **Primary Use Cases**: Simple 3rd party triggers that feed into the n8n webhook listener.

## 3. Core Automation Workflows

| ID | Workflow | Trigger | Action |
| :--- | :--- | :--- | :--- |
| **WF-04** | Perplexity Daily Digestion | Daily Cron | Fetches Perplexity task results -> Saves to `.hegemonikon/incoming` -> Generates `/eat` digest. |
| **WF-BOOT** | Morning Boot Notification | 08:00 JST | Scans Git log and Handoffs -> Notifies Slack -> Prompts user for `/boot` prompt. |
| **WF-SYNC** | Gnōsis/Sophia Activation | On Change | Synchronizes active knowledge fragments across the Oikos mesh. |

## 4. Design Principles

1. **Self-Documentation**: Every n8n workflow must have a corresponding `.md` design doc in `mekhane/ergasterion/n8n/`.
2. **Failure Transparency**: Notifications sent to Slack (#hegemonikon-alerts) on workflow failure.
3. **Stateless Processing**: Workflows should ideally be idempotent, relying on the file system (Git/incoming) as the ground truth.

---
*Created: 2026-02-06. Sources: perplexity_n8n_automation_design.md, conv_8_AI_Relationship_Evolution.*
