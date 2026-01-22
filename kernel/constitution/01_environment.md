---
id: G-1
layer: Iron Cage (Environment)
enforcement_level: L1
---

# G-1: Environment Protocol

> Controls file access, directory structure, and dependencies.

---

## M-01: DMZ Protocol (L0: IMMUTABLE)

**Rule:** Critical files (`.env`, `config.py`, `auth/*`) are **READ-ONLY**.

**Trigger:** User requests modification of protected assets.

**Action:**

1. HALT code generation
2. Issue "DMZ Violation Alert"
3. Require override: `SUDO_OVERRIDE_DMZ`

**Protected Patterns:**

- `^\.env$`
- `^config\.py$`
- `^secrets\.json$`
- `^auth/.*\.py$`
- `^docker-compose\.yml$`
- `^requirements\.txt$`

---

## M-02: Directory Topology Lock (L1: ENFORCED)

**Rules:**

- Do NOT create synonymous directories (`utils/` vs `helpers/`)
- Do NOT move/rename files without explicit "Refactor" request
- New directories require **Topology Amendment** proposal

**Trigger:** Intent to `mkdir`, create new path, or `mv`.

**Process:**

1. Scan existing directory structure
2. If new directory needed → PAUSE and propose
3. Wait for user approval

---

## M-03: Dependency Quarantine (L1: ENFORCED)

**Rules:**

- **Standard Library First:** Exhaust stdlib before external packages
- **No Silent Installs:** Require approval for `pip/npm install`
- **Version Pinning:** Always use `package==1.2.3`, never `latest`

**Trigger:** Import of module not in `requirements.txt`.

**Process:**

1. Check if stdlib → Proceed
2. Check if already in deps → Proceed
3. Else → HALT and generate Justification Report
4. Wait for `APPROVE_DEP` command

---

## M-19: Container First (L3: OPTIONAL) — Phase 2 Only

> [!WARNING]
> This module is **SUSPENDED** during Phase 1 (Termux).
> Activate only for Phase 2 (APK distribution).

**Rules:**

- Assume host has only Docker and Git
- Generate `Dockerfile` + `docker-compose.yml` instead of install steps
- Use specific version tags (`python:3.11-slim`), never `latest`

**Deliverables:**

- `Dockerfile` (multi-stage if needed)
- `docker-compose.yml` (all services)
- `.dockerignore`
