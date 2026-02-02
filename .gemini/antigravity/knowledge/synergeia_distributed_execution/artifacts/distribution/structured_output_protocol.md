# Structured Output Protocol (v1.0)

## Overview

As part of the [CCL Control Enhancement Research 2026], Synergeia now supports **Grammar-Constrained Decoding (GCD)** through native model APIs. This protocol defines how to use the `response_schema` and `tool_use` features to ensure high-fidelity CCL execution.

## 1. Technical Implementation

The `gemini_api.py` and `coordinator.py` have been updated to support JSON Schema enforcement.

### 1.1 `response_schema` (Gemini)

When calling `gemini_api.query()`, you can provide a `response_schema` dictionary:

```python
schema = {
    "type": "object",
    "properties": {
        "ccl_expression": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "string"},
                    "output": {"type": "string"}
                }
            }
        },
        "sel_compliance": {"type": "boolean"}
    }
}

result = gemini.query(prompt, response_schema=schema)
```

### 1.2 `output_config.format` (Claude)

Claude supports JSON Schema enforcement via the `output_config` parameter. This ensures the output is a valid JSON object matching the provided schema.

```python
request_params["output_config"] = {
    "format": {
        "type": "json_schema",
        "json_schema": {
            "name": "AuditResult",
            "schema": schema,
            "strict": True,
        }
    }
}
```

### 1.3 Strict Tool Use

For multi-stage reasoning (e.g., `/tek`), Synergeia uses Claude's `tool_use` with `strict: true`. This forces the model to use the defined tools with precise parameter matching, reducing hallucination in process steps.

## 2. Integration with SEL

This protocol is the primary mechanism for **SEL Phase 2 (Structural Enforcement)**.

1. **Schema Definition**: Pydantic models in `mekhane/ccl/output_schema.py` define the required fields for each operator.
2. **Schema Injection**: The `coordinator` injects these schemas into the API calls (Gemini `response_schema` or Claude `output_config`).
3. **Verification**: The `sel_validator.py` confirms that the structured fields contains the necessary semantic markers defined in the workflow's `minimum_requirements`.
4. **Audit Loop**: If L5 verification fails in `/vet`, the structured schema is used to provide pin-pointed feedback for re-generation.

## 3. Usage Patterns

### 3.1 Strict Step Execution

For `/boot+` or `/ax+`, a schema should be used to mandate a specific number of steps, preventing the model from collapsing multiple steps into a single summary.

### 3.2 Citation Enforcement

For `/sop` or `/zet`, use a schema that requires a `citations` list of objects `{url, title, snippet}` to prevent hallucinated or missing references.

---
*Created: 2026-02-01 | Synergeia Distribution Tech v1.0*
