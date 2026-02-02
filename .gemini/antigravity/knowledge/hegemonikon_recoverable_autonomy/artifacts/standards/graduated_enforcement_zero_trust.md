# Graduated Enforcement (Zero-Trust) Specification

## 1. Overview

**Graduated Enforcement** (codified 2026-01-31) implements the "Agentic Zero-Trust" protocol. It ensures that agent outputs are structurally verified according to the risk level of the operation, preventing "agentic laziness" and ensuring system integrity.

## 2. Enforcement Levels

| Risk Level | Mode | Mechanism | Macro |
| :--- | :--- | :--- | :--- |
| 🟢 **Low** | **Soft** | Verification of "Anti-Skip" requirements (no omissions). | `@antiskip` |
| 🟡 **Medium** | **Medium** | Schema validation (JSON/CCL Structure). | `@schema` |
| 🔴 **High** | **Hard** | Formal verification against semantic Guardrails. | `@guardrails` |

## 3. Structural Enforcement Protocol

1. **Zero-Trust Initialization**: Every workflow starts with a `se_scale` declaration (Micro, Meso, Macro).
2. **Template Obligation**: Outputs must match the predefined template for the scale.
3. **Validation Gate**: The `@enforce` macro triggers a validation check before any file commit.
4. **Mandatory Failure**: Validations that do not return a 100% match result in a block and potential `@rollback`.

## 4. Integration with Prompt-Lang

- **Low**: Standard Markdown enforcement.
- **Mid**: Prompt-Lang template with schema.
- **High**: Prompt-Lang Guardrails AI integration.

---
*Created: 2026-01-31 | v7.5 Strategic Alignment*
