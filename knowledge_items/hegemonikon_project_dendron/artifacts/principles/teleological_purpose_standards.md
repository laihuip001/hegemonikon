# Teleological Purpose Standards (L2 Surface)

Through the process of achieving 100% Purpose coverage for the `mekhane/dendron` module and a subsequent `/dia+` (Krisis) audit, a set of qualitative standards was established to ensure `# PURPOSE:` comments provide genuine teleological value rather than structural redundancy.

## 1. The Core Shift: WHY over WHAT

The most common failure pattern identified was the duplication of the function/class name or docstring. A valid Purpose declaration must explain the **teleological necessity** of the component within the system.

### Failure Patterns

- **WHAT-Duplication**: `# PURPOSE: Enum for Proof Status.` (The name `ProofStatus(Enum)` already says this).
- **Structural Description**: `# PURPOSE: Data class that holds file info.` (This describes the mechanism, not the intent).
- **Weak Verbs**: `# PURPOSE: Provides logic for checking files.` (Too vague; lacks specific system impact).

### Success Patterns (The "WHY" Standard)

- **Impact/Outcome**: `# PURPOSE: Allows the CI pipeline to branch its logic based on categorized verification failures.`
- **Functional Necessity**: `# PURPOSE: Unifies check results into a single interface to enable multi-format reporting.`
- **Constraint/Intent**: `# PURPOSE: Defines the granularity of existence proofs to manage computational overhead during recursive audits.`

## 2. Specific Classifications for Improvement

| Component Type | Weak Purpose (Structural) | Strong Purpose (Teleological) |
| :--- | :--- | :--- |
| **Enums** | "Enum for X status" | "Enables deterministic state transitions for X processing" |
| **DataClasses** | "Holds data for Y result" | "Standardizes Y results for downstream consumption/aggregation" |
| **Logic Classes** | "Main class for Z logic" | "Orchestrates Z verification and generates system-wide alerts" |
| **Methods** | "Initializes the checker" | "Pre-configures the verification environment to maximize throughput" |

## 3. The Krisis Checklist

When evaluating a Purpose comment (via `/dia+`), use the following criteria:

1. **Redundancy Test**: If the comment is removed, does the code lose an understanding of *why* it was built?
2. **Teleological Gap**: Does it explain what happens in the *future* (output/impact) rather than just what exists in the *past* (structure)?
3. **Verb Strength**: Does it use active, impactful verbs (Enables, Orchestrates, Standardizes, Prevents) instead of passive ones (Holds, Provides, Represents)?

---
Derived from /dia+ audit of mekhane/dendron - 2026-02-06
