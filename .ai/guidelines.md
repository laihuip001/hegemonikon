# AI Coding Guidelines

> **Purpose**: Coding standards and conventions for AI agents working on Hegemonikón.
> **Applies To**: All AI agents (Claude, Gemini, Copilot, etc.) writing code in this repository.

---

## 1. Language Standards

### Python

```python
# ✅ GOOD: Type hints, docstrings, snake_case
def sync_chat_history(session_id: str, limit: int = 100) -> list[dict]:
    """
    Synchronize chat history to LanceDB.
    
    Args:
        session_id: Unique session identifier.
        limit: Maximum entries to sync.
    
    Returns:
        List of synchronized records.
    """
    pass

# ❌ BAD: No types, no docstring, unclear naming
def sync(s, l):
    pass
```

### PowerShell

```powershell
# ✅ GOOD: Verb-Noun naming, comments
function Sync-ChatHistory {
    <#
    .SYNOPSIS
        Synchronizes chat history to database.
    #>
    param(
        [string]$SessionId,
        [int]$Limit = 100
    )
}

# ❌ BAD: Unclear naming
function DoSync { }
```

---

## 2. File Organization

### New Python File Template

```python
"""
Module: {module_name}
Description: {one-line description}

Part of Hegemonikón Forge layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# --- Constants ---
MAX_ENTRIES = 100

# --- Classes ---
class ExampleClass:
    """Example class docstring."""
    pass

# --- Functions ---
def example_function() -> None:
    """Example function docstring."""
    pass

# --- Main ---
if __name__ == "__main__":
    pass
```

### New Workflow Template

```yaml
---
description: {One-line description}
hegemonikon: {Modules used, e.g., Aisthēsis-H, Praxis-H}
modules: [{M1, M6, etc.}]
---

# /{workflow-name} ワークフロー

> **Hegemonikón Module**: {Primary modules}

## 実行手順

1. Step 1
2. Step 2

## 出力形式

```markdown
{Expected output format}
```
```

---

## 3. Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Use Case |
| :--- | :--- |
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructuring |
| `test` | Adding tests |
| `chore` | Maintenance |

### Examples

```
feat(gnosis): add arxiv paper collection

Implements CLI command for collecting papers from arXiv API.
Closes #123

---

fix(workflows): correct /boot memory loading order

M8 Anamnēsis was loading after M1, causing context loss.

---

docs(agents): add Critical Boundaries section
```

---

## 4. Error Handling

### Python

```python
# ✅ GOOD: Specific exceptions, logging
import logging

logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"Config file missing: {e}")
    raise
except ValueError as e:
    logger.warning(f"Invalid value, using default: {e}")
    result = default_value

# ❌ BAD: Bare except, silent failure
try:
    result = risky_operation()
except:
    pass
```

### PowerShell

```powershell
# ✅ GOOD: ErrorAction, try-catch
try {
    $result = Get-Content "config.json" -ErrorAction Stop | ConvertFrom-Json
} catch [System.IO.FileNotFoundException] {
    Write-Error "Config file not found"
    throw
}

# ❌ BAD: Silent failure
$result = Get-Content "config.json" 2>$null
```

---

## 5. Testing Requirements

### Minimum Test Coverage

| Layer | Requirement |
| :--- | :--- |
| `forge/gnosis/` | Unit tests for all public functions |
| `forge/scripts/` | Integration tests for CLI commands |
| `.agent/workflows/` | Manual verification documented |

### Test File Naming

```
module.py       → test_module.py
sync_history.py → test_sync_history.py
```

### Running Tests

```powershell
# Run all tests
python -m pytest forge/gnosis/tests/ -v

# Run with coverage
python -m pytest --cov=forge/gnosis --cov-report=html
```

---

## 6. Documentation Standards

### Inline Comments

```python
# ✅ GOOD: Explain WHY, not WHAT
# Using LanceDB instead of SQLite for vector similarity support
db = lancedb.connect("gnosis_data")

# ❌ BAD: Stating the obvious
# Connect to database
db = lancedb.connect("gnosis_data")
```

### README Updates

When adding new features, update:
1. `README.md` if user-facing
2. `docs/STRUCTURE.md` if structural change
3. `AGENTS.md` if workflow/boundary change

---

## 7. Forbidden Patterns

| Pattern | Reason | Alternative |
| :--- | :--- | :--- |
| `import *` | Namespace pollution | Explicit imports |
| `exec()` / `eval()` | Security risk | Structured data |
| `rm -rf` without confirm | Data loss risk | Use trash/backup |
| Hardcoded secrets | Security | Environment variables |
| `pandas`, `numpy` | Termux incompatibility | Pure Python or `sqlite3` |

---

## 8. Performance Guidelines

### File Operations

```python
# ✅ GOOD: Use pathlib, context managers
from pathlib import Path

config_path = Path("M:/Hegemonikon/config.json")
if config_path.exists():
    with config_path.open() as f:
        config = json.load(f)

# ❌ BAD: String manipulation, no cleanup
f = open("M:\\Hegemonikon\\config.json")
config = json.load(f)
# f never closed
```

### Database Queries

```python
# ✅ GOOD: Limit queries, use indexes
results = table.search(query).limit(10).to_list()

# ❌ BAD: Unbounded query
results = table.to_pandas()  # Loads entire table
```

---

*Last Updated: 2026-01-21*
