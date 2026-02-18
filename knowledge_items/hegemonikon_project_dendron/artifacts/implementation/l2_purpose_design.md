# Dendron L2 Surface: # PURPOSE: Comment Design

The L2 Surface layer (Cell P20 in the EPT) evolved from a docstring-based approach to a comment-based approach following a `/noe` (Noēsis) deep-insight session.

## 1. The Design Shift: Why # PURPOSE:?

Initially, the plan was to embed `Purpose:` within the function's docstring. However, the Noēsis session identified a "Principle of Consistency":

- **L1 (File Level)**: Uses `# PROOF:` comments in the header.
- **L2 (Function/Class Level)**: Should use `# PURPOSE:` comments for cognitive alignment.

### Advantages of the Comment Approach

- **Universal Applicability**: Works for functions and classes that don't have (or need) a full docstring.
- **Cognitive Symmetry**: Directly mirrors the L1 PROOF pattern, reducing the mental load required to differentiate proof layers.
- **Separation of Concerns**: Keeps "teleological proof" (why it exists) structurally distinct from "documentation" (how to use it), while remaining in the source file.

## 2. Technical Implementation

### Standard Pattern

The checker walks the AST and looks for the nearest preceding comment to a function or class definition.

```python
# PURPOSE: Validates the user's session token and returns current permissions.
def get_permissions(session_id: str):
    ...
```

### Handling Decorators

A critical implementation detail discovered during self-verification: The `# PURPOSE:` comment must be placed **above** any decorators (e.g., `@dataclass`, `@property`). This is because the AST node's starting line includes decorators, and logical proximity requires the proof to precede the entire definition chunk.

```python
# PURPOSE: Data container for L2 proof results.
@dataclass
class FunctionProof:
    ...
```

## 3. Scope and Exclusions

- **Dunder Methods**: Standard Python methods like `__init__` or `__str__` are exempt, as their purpose is predefined by the language.
- **Private Methods**: Methods starting with `_` are excluded from mandatory checks to focus on the public interface of the infrastructure layer.
- **Test Files**: Files matching `test_*.py` are exempt to prevent overhead in the verification of test harnesses themselves.

---
*Reference: [Noēsis Insight session - 2026-02-06]*
