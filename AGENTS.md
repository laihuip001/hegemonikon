# AGENTS.md - Hegemonikon Project v2.1

> **Purpose**: AI エージェント（Claude, Gemini, Jules）へのガイダンス

## Overview

Hegemonikon: FEP (Free Energy Principle) に基づく認知ハイパーバイザーフレームワーク。

### 構造

| 項目 | 数 |
|------|----|
| 公理 | 7 |
| 定理 | 24 (6×4) |
| 関係 | 36 |
| **総数** | **60** |

### 定理群

| 記号 | 名称 | 役割 |
|------|------|------|
| O | Ousia | 本質 |
| S | Schema | 様態 |
| H | Hormē | 傾向 |
| P | Perigraphē | 条件 |
| K | Kairos | 文脈 |
| A | Akribeia | 精密 |

---

## Do

- Use TypeScript for frontend/tooling, Python for backend/ML
- Follow ESLint/Pylint rules
- Write tests for all business logic
- Use Japanese for user-facing text and documentation
- Keep code modular and well-documented
- Run linting and tests before commit

## Don't

- Don't hardcode credentials or API keys
- Don't skip tests
- Don't modify `kernel/*.md` without approval
- Don't use `any` type in TypeScript
- Don't commit without passing CI checks

---

## Setup Commands

```bash
# Python environment
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Node.js dependencies (if applicable)
npm install
```

## Test Commands

```bash
# Python tests
pytest tests/

# Lint check
pylint mekhane/
```

---

## File Structure

| Path | Purpose |
|------|---------|
| `kernel/*.md` | Core doctrine (immutable) |
| `mekhane/` | Python implementation |
| `.agent/workflows/*.md` | Workflows |
| `.agent/skills/*/SKILL.md` | Skills |
| `docs/` | Documentation |

### Key kernel files

| File | Content |
|------|---------|
| `SACRED_TRUTH.md` | Immutable truths |
| `axiom_hierarchy.md` | 7 axioms, 24 theorems |
| `naming_conventions.md` | Greek naming rules |

---

## Code Style

- **Python**: Black formatter, 88 char line length
- **TypeScript**: Prettier, 100 char line length
- **Naming**: snake_case (Python), camelCase (TypeScript)
- **Comments**: English for code, Japanese for documentation

---

## When Stuck

Ask for clarification. Propose a plan before implementing.

---

## References

- [kernel/axiom_hierarchy.md](kernel/axiom_hierarchy.md)
- [kernel/naming_conventions.md](kernel/naming_conventions.md)
- [README.md](README.md)

---

*Hegemonikón v2.1*
