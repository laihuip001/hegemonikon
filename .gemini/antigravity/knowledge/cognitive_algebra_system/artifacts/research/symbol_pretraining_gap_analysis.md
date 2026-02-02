# Research: The Symbol Pretraining Gap in LLM Control

## Discovery (2026-02-01)

During a session debugging the `/boot+` command—which unexpectedly performed a truncated boot—a systematic investigation was launched into why AI agents ignore symbolic operators.

## The "Pretraining Gap" Hypothesis

The fundamental issue is that LLM pretraining data does not consistently treat mathematical symbols as binding obligation markers in the context of task instructions.

### Key Evidence

1. **Statistical Weight**: "Must" and "Should" have higher semantic weights in instruction-following datasets than `+` or `-`.
2. **Cognitive Laziness**: Without explicit linguistic pressure, agents default to the lowest entropy path (shorter responses/fewer steps), interpreting symbols as optional stylistic hints.
3. **Deontological Bias (Park et al., ACL 2025)**: LLMs show a 90%+ compliance rate with explicit modal verbs compared to <40% with symbols alone.

## Mitigation Strategy: SEL

By wrapping symbolic commands in a Semantic Enforcement Layer, Hegemonikón forces the agent to acknowledge the operator as a strict requirement before processing the task logic.

## Implications for DSL Design

For any domain-specific language designed for LLM control, "Symbol Strength" must be artificially boosted through natural language mapping to maintain structural integrity.
