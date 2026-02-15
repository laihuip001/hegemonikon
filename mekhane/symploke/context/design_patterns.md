# Design Patterns & Architecture

> Architectural patterns used across the Hegemonikón codebase.
> Jules reviewers: deviations from these patterns may be intentional or bugs.

## Module Hierarchy

```
kernel/          — Theory (axioms, theorems, definitions)
  └→ hermeneus/  — CCL parser & workflow engine
       └→ mekhane/ — Implementation layer
            ├── symploke/   — Jules reviews & boot integration
            ├── ochema/     — LLM routing (LS + Cortex)
            ├── dendron/    — Code quality & existence proofs
            ├── peira/      — Health monitoring
            ├── ergasterion/ — Paper analysis pipeline
            ├── fep/        — FEP calculations
            ├── synteleia/  — Safety & verification
            └── mcp/        — MCP servers
```

## Mandatory Code Conventions

| Pattern | Rule | Violation Signal |
|:--------|:-----|:-----------------|
| `# PROOF:` header | Every module file starts with existence proof | Missing = not integrated |
| `# PURPOSE:` comments | Every function/class has purpose annotation | Missing = undocumented intent |
| Type annotations | All new functions require type hints | Missing = incomplete |
| snake_case | Functions and variables | PascalCase ≠ function |
| PascalCase | Classes only | snake_case ≠ class |
| SCREAMING_SNAKE | Constants only | lowercase ≠ constant |

## Design Principles (Ranked)

1. **Reduced Complexity** — 10x → 1/10 compression
2. **Intuitive Logic** — Structure needs no explanation
3. **Obsessive Detail** — Edge cases always matter
4. **Form Follows Function** — No decorative code
5. **Consistency Over Cleverness** — Follow established patterns

## Anti-Patterns to Flag

- Reimplementing existing functionality (check `registry.yaml` first)
- Breaking the kernel → hermeneus → mekhane dependency flow
- Mixing Greek/English naming without following the naming convention
- Large functions (>20 lines) without decomposition
