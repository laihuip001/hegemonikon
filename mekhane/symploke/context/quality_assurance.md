# Quality Assurance & Testing

> QA patterns including PROOF.md, Dendron checks, and Synteleia safety.
> Jules reviewers: understand what "quality" means in THIS project.

## PROOF.md — Existence Proofs

Every module must justify its existence:

```
# PROOF: [Level/Category] <- parent/path/ Axiom→Need→This module fills it
```

- **Level**: L0 (kernel), L1 (hermeneus), L2 (mekhane), L3 (integration)
- **Axiom trace**: Which axiom/theorem necessitates this module

## Dendron — Structural Guard

`mekhane/dendron/` validates:

- Every `.py` file has a `# PROOF:` header
- Every function has a `# PURPOSE:` comment
- Module dependency flow is respected
- No orphan modules (everything traces to an axiom)

## Synteleia — Safety White Blood Cells

`mekhane/synteleia/` provides:

- Automated code safety checks
- Multi-backend review (Cortex Gemini, jules, local)
- Sweep analysis for systemic issues

## What Jules Should Review For

| Priority | Focus | NOT This |
|:---------|:------|:---------|
| 1 | **Design-level insights** — structural problems, coupling | PEP8, basic lint |
| 2 | **Niche discoveries** — subtle logic errors, edge cases | Obvious typos |
| 3 | **Aesthetic judgments** — naming harmony, visual rhythm | Formatting preferences |
| 4 | **Pattern violations** — deviations from above conventions | Style opinions |
| 5 | **SILENCE if nothing wrong** — don't manufacture issues | Filler feedback |
