# Task: Fix All 948 Audit Issues

## Status
- **Current Issues:** ~948 (Medium/Low)
- **Goal:** 0 Issues in Strict Mode

## Plan
- [ ] **Auditor Improvement**
    - [ ] Check current state of `ai_auditor.py` (post-revert).
    - [ ] Restore AI-017 Magic Number acceptable values (if lost).
    - [ ] Restore AI-007 Pattern Inconsistency thresholds (if lost).
    - [ ] Implement Inline Suppression (`# noqa: AI-xxx`, `# auditor: ignore`).
    - [ ] Refine AI-006 (Context Drift) logic (allow safe reassignments).
    - [ ] Refine AI-003 (Type Confusion) logic (allow implicit bool).
- [ ] **Code Fixes**
    - [ ] Fix `analyze_pb.py` (Path, Magic Numbers).
    - [ ] Fix AI-018 (Hardcoded Path) in other files.
    - [ ] Apply `# noqa` to false positives (AI-005, AI-022 where appropriate).
- [ ] **Verification**
    - [ ] Run `python ai_auditor.py mekhane/ --strict` → Expect 0 issues.
    - [ ] Commit changes.
