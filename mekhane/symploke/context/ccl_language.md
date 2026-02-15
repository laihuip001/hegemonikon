# CCL (Cognitive Control Language)

> Domain-specific language for orchestrating cognitive workflows.
> Jules reviewers: CCL syntax in comments/filenames is INTENTIONAL, not typos.

## Syntax Quick Reference

| Operator | Meaning | Example |
|:---------|:--------|:--------|
| `/` | Workflow invocation | `/noe` = invoke Noēsis |
| `+` | Deep variant (L3) | `/noe+` = deep Noēsis |
| `-` | Quick variant (L1) | `/noe-` = quick Noēsis |
| `~` | Oscillation | `~(/noe*/dia)` = alternate |
| `>>` | Sequence | `/noe >> /dia` = then |
| `*` | Parallel | `/noe*/dia` = concurrent |
| `{}` | Group | `{/noe + /dia}` |
| `F:[×N]` | Loop N times | `F:[×3]{...}` |
| `V:{}` | Verify block | `V:{/dia+}` |
| `C:{}` | Core block | `C:{/ene+}` |

## Workflow Naming Convention

| Layer | Length | Language | Example | Role |
|:------|:-------|:---------|:--------|:-----|
| Ω (Omega) | 1-2 | English | `/o`, `/s`, `/ax` | Series orchestrator |
| Δ (Delta) | 3 | Greek | `/noe`, `/dia`, `/zet` | Domain expert (theorem) |
| τ (Tau) | 3-4 | English | `/bye`, `/dev`, `/plan` | Task execution |

## Common CCL Macros

- `/ccl-dig` — Deep analysis
- `/ccl-build` — Build/implement
- `/ccl-fix` — Fix/repair
- `/ccl-vet` — Verification
- `/ccl-proof` — Formal proof

## For Code Review

CCL expressions in code comments (e.g., `# /noe+ analysis`) indicate which
cognitive workflow produced or validates that section. Do NOT flag these as
formatting issues — they are intentional workflow markers.
