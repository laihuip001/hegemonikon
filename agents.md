# agents.md - Hegemonikón

## Project Overview

Hegemonikón is a cognitive hypervisor framework based on:

- **Free Energy Principle (FEP)** - Predictive processing and active inference
- **Stoic Philosophy** - Greek terminology and philosophical foundations
- **Common Model of Cognition (CMoC)** - 8-module cognitive architecture

## Tech Stack

| Component | Version |
|-----------|---------|
| Python | 3.11 |
| Async | asyncio, aiohttp |
| Vector DB | LanceDB + HNSWlib |
| Embedding | all-MiniLM-L6-v2 |
| Protocol | MCP (Model Context Protocol) |

## Directory Structure

```
hegemonikon/
├── kernel/           # Core theorems (O/S/H/P/K/A series)
│   ├── tropos.md     # S1-S10 mode definitions
│   ├── rhope.md      # H1-H10 impulse definitions
│   └── axiom_hierarchy.md
├── mekhane/          # Implementation layer
│   ├── anamnesis/    # Memory systems
│   ├── symploke/     # Integration layer (Jules client)
│   └── ...
├── mcp/              # MCP servers
│   ├── gnosis_mcp_server.py
│   ├── jules_mcp_server.py
│   └── mneme_server.py
└── docs/             # Documentation
```

## Coding Standards

### Naming Conventions

- **Greek terms** for philosophy concepts (Hegemonikon, Tropos, Krisis)
- **snake_case** for Python functions/variables
- **PascalCase** for classes
- **SCREAMING_SNAKE_CASE** for constants

### Type Annotations

- Required for all function signatures
- Use `Optional[]` for nullable types
- Prefer `list[]` over `List[]` (Python 3.11+)

### Documentation

- docstrings in Japanese or English
- Markdown for all documentation
- YAML frontmatter for workflow/skill files

## Default Branch

**`master`** (NOT main)

## Testing

```bash
# Run all tests
pytest tests/

# Run async tests
pytest tests/ -v --asyncio-mode=auto

# Run specific test
pytest tests/test_jules_client.py -v
```

## Environment Setup

```bash
# Create venv
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Important Notes

1. **Branch name**: Always use `master`, not `main`
2. **Greek naming**: Use accurate Stoic philosophy terms
3. **Async patterns**: Prefer async/await for I/O operations
4. **Type safety**: All functions must have type hints

---

*Generated for Jules environment setup*
