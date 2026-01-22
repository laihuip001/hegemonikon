# Prompt Library

A modular prompt engineering toolkit optimized for LLM-powered development workflows.

## Features

- **19 Modules** covering Critical Audit, Quality Control, Analysis, and Execution
- **Unified Audit/Fix** design: `C-1-2`, `C-4-5`, `C-6-7` combine review and repair
- **52% average reduction** from source prompts via XML flattening

## Quick Start

```
1. Open module file from prompts/modules/
2. Copy content
3. Paste into chat as your message
```

## Module Categories

| Category | Modules | Purpose |
|---|---|---|
| **Critical** | C-1-2, C-3, C-4-5, C-6-7 | Adversarial audit and surgical fixes |
| **Quality** | Q-1 to Q-4 | Simplicity, second-order thinking, aesthetics |
| **Analysis** | A-2, A-3, A-7 to A-9 | Lateral thinking, bias detection, first principles |
| **Execution** | B-3, E-1, I-1, M-1, R-1, X-1/2 | Roadmaps, context mapping, agent commands |

## Design Principles

1. **Modular Invocability**: YAML frontmatter with `id:` and `modes:`
2. **Mode-Based Unity**: Audit and Fix in single file with `## Mode: Audit/Fix`
3. **No Truncation**: All output templates are complete and copy-paste ready

## License

MIT
