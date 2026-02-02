# Fixer Manual

## Commands

`python mekhane/synedrion/ai_fixer.py mekhane/ --dry-run`
`python mekhane/synedrion/ai_fixer.py mekhane/`

## Supported Auto-Fixes

- **AI-012**: Transforms `time.sleep` into `await asyncio.sleep`.
- **AI-015**: Comments out redundant self-assignments.
- **AI-019**: Updates deprecated asyncio APIs.
- **AI-020**: Converts bare excepts and adds TODOs to silent pass blocks.

## Batch Operations

Use `--severity high,critical` to focus on high-priority fixes.
