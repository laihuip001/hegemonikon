# AGENTS.md - Hegemonikon Project

> **Purpose**: AI エージェント（Jules, Claude, Gemini）へのガイダンス

## Overview

Hegemonikon: A cognitive hypervisor framework integrating FEP-based AI modules.
TypeScript + Python hybrid. Japanese documentation, English code.

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
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Node.js dependencies (if applicable)
npm install
```

## Test Commands

```bash
# Python tests
pytest

# Lint check
pylint mekhane/

# TypeScript tests (if applicable)
npm run test
```

---

## File Structure

| Path | Purpose |
|------|---------|
| `kernel/*.md` | Core doctrine (immutable) |
| `mekhane/` | Python implementation |
| `.agent/workflows/*.md` | Workflows |
| `.agent/skills/*/SKILL.md` | Skills |
| `forge/` | Experimental tools |
| `docs/` | Documentation |

---

## Code Style

- **Python**: Black formatter, 88 char line length
- **TypeScript**: Prettier, 100 char line length
- **Naming**: snake_case (Python), camelCase (TypeScript)
- **Comments**: English for code, Japanese for documentation

---

## Good Examples

- Python module: `/mekhane/anamnesis/antigravity_logs.py`
- Workflow: `/.agent/workflows/manual.md`
- Skill: `/.agent/skills/*/SKILL.md`

---

## When Stuck

Ask for clarification. Propose a plan before implementing.

---

## References

- Prompt-Lang v2 Spec: `docs/specs/prompt-lang-v2-spec.md`
- Jules Setup Guide: `docs/guides/jules_setup_guide.md`
