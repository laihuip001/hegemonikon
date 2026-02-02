# Auditor Usage Guide

## Commands

- `python mekhane/synedrion/ai_auditor.py mekhane/` (Reports all detected issues)

## Customization

Standard library and known 3rd party modules are defined in `KNOWN_MODULES` to prevent AI-001 false positives. Local modules should be added there.

## 4. The 5-Step Audit Process

Following the 2026-02-01 architecture update, the `AIAuditor` follows a deterministic 5-step pipeline to ensure Kairema 10 compliance:

1. **LOAD**: Direct read of the source text.
2. **PARSE**: AST generation and diagnostic check for syntax blockers.
3. **AUDIT**: Execution of the 22-axis risk scan (Symbolic, Logic, Performance, etc.).
4. **FILTER**: Intelligent suppression handling (checks for `# noqa` and valid exclusions).
5. **REPORT**: Generation of the unified JSON/Text report.

## 5. Kairema 10 Enforcement

The Synedrion system rejects the concept of "acceptable noise." All findings must be remediated or explicitly suppressed. See **[[hegemonikon_governance_integrity/artifacts/standards/kairema_10_integrity_standard.md]]** for philosophical details.

## Severity & Integrity Standards

Hegemonikón maintains a **True Zero** policy for AI-generated code.

- **Critical**: Security (secrets) or major async violations.
- **High**: Potential crashes or silent failures.
- **Medium**: Resource leaks or mutable defaults.
- **Low**: Style, docstrings, magic numbers, or recommendations.

## Inline Suppression

Hegemonikón allows for explicit, local suppression of audit findings when a pattern is intentional or a false positive. This is preferred over global deactivation.

- **Standard**: `# noqa: AI-xxx` (e.g., `x = 100  # noqa: AI-017`)
- **Multiple**: `# noqa: AI-017, AI-006`
- **Catch-all**: `# noqa` (Suppresses all findings on the line)
- **Alternative**: `# auditor: ignore: AI-xxx`

*Note: Suppression must be used judiciously. "Cleaning" the report by suppressing actual issues is a violation of systemic integrity.*
