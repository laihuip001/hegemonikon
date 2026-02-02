# Portability & Persistence Patterns

Hegemonikón is designed to be portable across environments (e.g., GCP VM to House PC). This requires systematic patterns for service persistence and environment initialization.

## 1. Service Persistence via Systemd Templates

When background mechanisms (like the Gnōsis Digestor) require constant execution, we use `systemd` user-specific service templates.

- **Pattern**: `[Service]` files using `@.service` naming allowing invocation as `service-name@user.service`.
- **Implementation**:
  - `WorkingDirectory` and `Environment` variables should be relative to the user's home or consistently mapped.
  - `ExecStart` points to the local `.venv` to ensure isolated dependencies.
  - `Restart=on-failure` ensures robustness.

## 2. Portability & Setup Automation

To reduce "migration friction," mechanisms should include a `setup-*.sh` script.

- **Requirements**:
  - Idempotent script that clones/copies service files to `/etc/systemd/system/`.
  - Reloads `daemon-reload` and enables the service.
  - Provides a status check output immediately after setup.

## 3. Combating Maintenance Blindness

Background services often fail or go unstarted silently. Hegemonikón uses the **Bootstrap Integration** pattern.

- **Phase 4 Integration**: The `/boot` workflow (v3.1+) includes checks for background mechanisms.
- **Lightweight Probes**: Rather than just "is it running?", the probe performs a lightweight data retrieval (e.g., `DigestorPipeline.run(max_papers=15, dry_run=True)`) to verify both process and connectivity.

## 4. Migration Continuity (The "Beautiful" Handoff Pattern)

Rather than using hardcoded file checks in the core `/boot` workflow—which creates "technical debt" and clutter—Hegemonikón uses the **Session Handoff** for transitory environment states.

- **The Hack (Discarded)**: Creating a standalone `MIGRATION_CHECKLIST.md` and modifying `/boot` to check for its existence.
- **The Beautiful Solution**: Embedding migration tasks (like `bash setup-scheduler.sh`) directly into the **Latest Handoff** (`mneme/.hegemonikon/sessions/handoff_*.md`).
- **Mechanism**: Since `/boot` (Step 3) already reads the latest handoff to synchronize AI state, the migration tasks are naturally presented to the AI and Creator at the optimal context without polluting the core workflow code.
- **Cleanup**: The requirement is naturally "superseded" in the next session's handoff once the task is marked complete.

---
*Operational Insight | 2026-01-29 | Hegemonikón Beauty Standard v1.1*
