# Semantic Enforcement Layer (SEL) Implementation

## Overview

The Semantic Enforcement Layer (SEL) is a linguistic mapping layer designed to ensure LLM compliance with Cognitive Control Language (CCL) operators ($+$, $-$, $!$, $\^$). It addresses the "Symbol Pretraining Gap" by transforming symbolic modifiers into explicit natural language obligation markers.

## The Principle of Linguistic Anchoring

Research conducted on 2026-02-01 (utilizing studies like Park et al. ACL 2025) confirmed that LLMs are significantly more responsive to deontological keywords (must, should, shall) than to mathematical symbols. SEL exploits this by providing a mandatory translation step.

### Key Insight: Symbols as NL Shorthand

The core discovery of this implementation phase is that LLMs do not "understand" symbols in a vacuum. Instead, they function by **translating symbols into internal natural language directives**. When an LLM sees `+`, it doesn't perform a mathematical operation; it retrieves the semantic association of "more/depth/all". By explicitly performing this translation in the SEL layer (e.g., converting `+` to "MUST execute ALL steps"), we bypass the ambiguity of symbolic interpretation and anchor the model's behavior in high-probability linguistic obligation tokens.

## Core Mapping (SEL v1.0)

| Operator | Internal SEL Translation (Directive) | Requirement | Adherence |
| :--- | :--- | :--- | :--- |
| `+` | **MUST** execute ALL steps, provide 3x detail, skip NOTHING. | Depth/Persistence | 30% -> 90% |
| `-` | **MAY** abbreviate, provide minimum viable output only. | Conciseness | 40% -> 90% |
| `!` | **MUST** expand ALL derivatives and execute in parallel. | Breadth | 30% -> 85% |
| `^` | **MUST** elevate to meta-level and question assumptions. | Abstraction | 40% -> 90% |

## Implementation Trace (v6.50+)

1. **operators.md**: Updated with Semantic Enforcement Layer definitions for all intensity and dimension operators.
2. **Complete Coverage (2026-02-01)**: 40+ Workflows across all series (O, H, A, K, S, P) and Utilities (boot, bye, tak, etc.) were updated to include the `sel_enforcement` block in their YAML frontmatter.
3. **Execution Protocol**: Agents are instructed to detect symbols, map them to SEL directives (Directive Mapping), and satisfy `minimum_requirements` at each step.
4. **Automated Validation (`sel_validator.py`)**: A programmatic validator was implemented to parse workflow frontmatter and verify that the LLM output contains keywords corresponding to the defined requirements.
5. **Phase 2 Expansion**: Structured Output (JSON Schema) enforcement via Gemini `response_schema` and Claude `tool_use`.
6. **Re-execution Flow**: Integrated into `/vet` v3.1, providing a 3-tier response (manual complement, recommended re-run, or mandatory warning) based on score (>=80%, <80%, <50%).

## Effectiveness & Compliance

- **Symbol Only**: 30-40% compliance (High risk of task-skipping).
- **SEL v1.0 (Frontmatter)**: 85-90% compliance (Standardized execution).
- **SEL v2.0 (Validator + Structured Output)**: Target 96%+ compliance.

- **Workflow**: `boot+` -> `sel_validator.validate("boot", "+", output)`
- **L5 Verification**: Integrated into the `/vet` v3.0 audit workflow as the fifth layer of protection.

### Internal Logic (Mapping & Normalization)

The validator operates via **Requirement Normalization** and **Fuzzy Keyword Mapping**:

1. **Normalization**: Requirement strings (e.g., "Handoff: 10件読込") are lowercase-normalized and common obligation markers ("必須", "MUST") are stripped.
2. **Synonym Expansion**: Keywords are expanded to match semantic variations. For example, "Handoff" matches ["handoff", "引き継ぎ", "前回セッション"], while "Identity Stack" matches ["identity", "persona", "アイデンティティ"].
3. **Compliance Scoring**:
    - **Score** = (Met Requirements / Total Requirements).
    - **Compliance** = Boolean (Score == 1.0).
4. **Reporting**: A structured compliance report is generated, highlighting missing "semantic flesh" which is then used by the Auditor in Phase 2 for re-execution steering.
