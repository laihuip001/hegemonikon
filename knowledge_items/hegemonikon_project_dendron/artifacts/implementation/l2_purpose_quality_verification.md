# L2 Purpose Quality Verification (v2.6)

Building upon the qualitative standards established in the Teleological Purpose Standards, version 2.6 of the Dendron Checker introduces **Automated Quality Verification** for `# PURPOSE:` comments. This represents a transition from simple existence checks to teleological depth validation.

## 1. Technical Framework

The checker now distinguishes between three L2 states:

- `OK`: Purpose exists and passes qualitative filters.
- `WEAK`: Purpose exists but is identified as "structural" (WHAT) rather than "teleological" (WHY).
- `MISSING`: No Purpose comment found.

### Quality Validation Logic

The `_validate_purpose_quality` method evaluates the Purpose text against a set of regex-based "Weak Patterns." These patterns target linguistic markers of structural description that duplicate the function's name or type.

## 2. Weak Purpose Patterns (Greylist)

The following patterns are actively detected and flagged as `WEAK`:

| Pattern | Detected Failure | Recommendation |
| :--- | :--- | :--- |
| `を表す` | Describes the representation (WHAT). | Use `を可能にする` or `を実現する`. |
| `を保持する` | Describes data structure (WHAT). | Use `を管理する` or `を統一的に扱う`. |
| `を提供し` / `を提供する` | Vague structural utility. | Explain the specific system impact. |
| `を定義する$` | Redundant definition statement. | Describe the necessity of the definition. |
| `^データクラス$` | Minimalist structural label. | Explain why the data must be encapsulated. |
| `^列挙型$` | Minimalist structural label. | Explain the state logic governed by the enum. |

## 3. Implementation Details

- **`ProofStatus.WEAK`**: A new enum state to support qualitative flagging without hard-failing the CI (currently).
- **`FunctionProof.quality_issue`**: A new field containing the rationale for the qualitative rejection.
- **AST Integration**: The validation is performed immediately after the comment is extracted from the AST, ensuring zero-overhead integration with the existing scanner.

## 4. Self-Correcting Loop

The first application of v2.6 was on `checker.py` itself. Following the `/dia+` audit which identified structural redundancy in its own comments, the checker's new rules were used to verify the subsequent refinement of those comments. This "Recursive Self-Correction" ensures that Dendron enforces the same rigor it demands of the rest of the Hegemonikón core.

---
Updated: 2026-02-06 | Version 2.6
