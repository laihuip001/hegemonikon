# Active Projects System (Governance)

> **Objective**: Solve the "Buried Project" problem (Cognitive Decay).
> **Mechanism**: Central Registry + Standard Metadata.

## 1. The Visibility Problem

As the repository grows, specialized projects (Dendron, Synteleia, etc.) often get buried deep within the `mekhane/` or `kernel/` directories. This leads to "Cognitive Decay" where the AI or the Creator forgets the project's status, leading to "Existence Errors."

## 2. System Components

### 2.1 Central Registry (`projects.yaml`)
A machine-readable list of all named projects at the root of the repository.

- **Path**: `hegemonikon/projects.yaml`
- **Fields**: `name`, `path`, `status`, `phase`, `priority`, `updated`, `next_action`.

### 2.2 Project Metadata (`PROJECT.md`)
Each project MUST contain a `PROJECT.md` file in its root directory with YAML frontmatter.

- **Status Values**: `planning` | `active` | `mvp_complete` | `stable`.
- **Priority**: `high` (always shown) | `medium` (weekly) | `low` (monthly).

## 3. Operational Integration

### 3.1 /boot Display (Step 17.5)
The `/boot` sequence automatically reads `projects.yaml` and displays active projects.

- **High Priority**: Displayed on every boot.
- **Freshness Alerts**:
    - **7+ Days**: ⚠️ (Warning: Velocity drop).
    - **21+ Days**: 🔴 (Critical: Consider archiving or re-activating).

### 3.2 /bye Update Prompt
The session closing ritual should prompt for updates to the `updated` and `next_action` fields if significant progress was made.

### 3.3 Implementation Note: Initial Projects (2026-02-01)
The following projects were the first to be registered in the system (Status: **Successfully Deployed**):
1. **Dendron** — Existence Proof CLI (MVP Complete)
2. **Hermēneus** — CCL Compiler (Active)
3. **Synteleia** — Ensemble Layer (Planning)
4. **Pythōsis** — Python Philosophy (Active)
5. **Synergeia** — Infrastructure (Stable)

## 4. Significance

The Active Projects System ensures that "Existence Reason" (Ousia) is coupled with "Visibility" (Phaneron). It forces the system to acknowledge what is currently being prioritized, facilitating persistent identity and focus across sessions.
