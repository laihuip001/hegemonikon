# Dendron L2 Surface: Docstring Purpose Check

The L2 Surface layer (Cell P20 in the EPT) verifies that every function and class has a declared "Purpose" (志向性) within its docstring.

## 1. Technical Strategy

Unlike L1 proofs which reside in file headers, L2 proofs are embedded within the code's documentation to ensure high cohesion between implementation and intent.

### Parser Requirements

- **AST Scanning**: Use Python's `ast` module to walk the source tree of each `.py` file.
- **Node Classification**: Distinguish between `ast.FunctionDef` and `ast.ClassDef`.
- **Docstring Extraction**: Retrieve `ast.get_docstring(node)` for each defined entity.

### Purpose Pattern

The checker looks for a `Purpose:` prefix followed by a descriptive string.

```python
# Regex: r"Purpose:\s*(.+)"
def process_data(data: list):
    """
    Purpose: Transforms raw input list into a normalized format for storage.
    """
    ...
```

## 2. Implementation Model

The logic will be integrated into `checker.py` by adding a granular scanning pass for functions and classes.

### Data Structures

- **`FunctionProof`**: A new dataclass to track the status of individual code blocks.
  - `name`: Target function/class name.
  - `path`: File path.
  - `line_number`: Definition start line.
  - `has_purpose`: Boolean flag.
  - `purpose_text`: Extracted content if present.

### Validation Flow

1. Load file content.
2. If the file has a valid L1 PROOF header, proceed to L2 analysis.
3. Parse the AST.
4. For each relevant node:
   - Extract docstring.
   - Run `PURPOSE_PATTERN`.
   - Record `FunctionProof`.
5. Aggregate results into `CheckResult.function_proofs`.

## 3. Self-Verification

Dendron will be the first system to adopt this standard. Every function in `checker.py` and `reporter.py` must include a `Purpose:` statement in its docstring to achieve 100% P20 coverage.

---
*Reference: [VISION.md v2.1](file:///home/makaron8426/oikos/hegemonikon/mekhane/dendron/VISION.md)*
