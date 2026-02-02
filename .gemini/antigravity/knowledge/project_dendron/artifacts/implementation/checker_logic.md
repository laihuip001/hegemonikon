# Dendron Implementation: Checker Logic

The core logic of Dendron resides in `mekhane/dendron/checker.py`, implementing a recursive scanner that validates the existence of PROOF markers.

## 0. Module Structure & Packaging
As of 2026-02-01, the tool has been integrated as a submodule of `mekhane`:
- `mekhane/dendron/`: Package directory.
- `__main__.py`: Entry point for `python -m mekhane.dendron`.
- `cli.py`: Argument parsing and command dispatch.
- `checker.py`: Core logic (v2.2 Hardening implemented).
- `reporter.py`: Multi-format report generation.
- `migrate.py`: Automated v2 migration tool.

## 1. Data Structures

### ProofStatus
- `OK`: Valid existence proof with parent reference found.
- `ORPHAN`: Valid proof found but parent reference is missing or invalid (🆕 v2).
- `MISSING`: No proof found.
- `INVALID`: Proof format is incorrect or file is unreadable.
- `EXEMPT`: File/directory is ignored via `EXEMPT_PATTERNS` (e.g., `__pycache__`, `.venv`).

### ProofLevel
- `L1`: Theorem (Core functionality/Philosophy).
- `L2`: Infrastructure (Utilities, support code).
- `L3`: Test/Sample.

## 2. Validation Logic

### File Validation (L1) — Mandatory Parent Linking
The scanner reads the first 10 lines of a `.py` file attempting to match the v2 regex:
`#\s*PROOF:\s*\[([^\]]+)\](?:\s*<-\s*([^\s#]+))?`

**Note**: The pattern intentionally omits the end-of-line anchor (`$`) to allow for trailing explanations or comments (e.g., `# PROOF: [L1/定理] A0→...`).

### Comment filtering (🆕 v2.2)
To prevent "Docstring Hijacking" where a PROOF header inside a string or multi-line comment is mistakenly captured, the `_is_code_comment()` method ensures only lines starting with `#` are processed as valid headers.

### Resource Protection (🆕 v2.2/v2.3)
To prevent "Auditor DoS" attacks via massive files, the checker enforces `MAX_FILE_SIZE` (default 10MB). Files exceeding this size are marked as `INVALID`.

**Binary Detection (🆕 v2.3)**: To prevent processing non-text files that might masquerade as code, the checker scans the first segment of the file for NULL bytes (`\x00`). If detected, the file is marked as `INVALID`.

### Parent Path Validation (🆕 v2.1)
As of v2.1, parent references are no longer "placeholder" strings. The `DendronChecker.validate_parent()` method performs several checks:
1.  **Exemption**: Skips validation for `SPECIAL_PARENTS` (`FEP`, `external`, `legacy`).
2.  **Traversal Prevention**: Rejects any path containing `..` to prevent out-of-bounds exploration.
3.  **Absolute Path Check**: Rejects paths starting with `/`.
4.  **Path Length Validation (🆕 v2.4)**: Rejects parent paths exceeding filesystem limits (e.g., 255 chars) before performing `exists()` to prevent `OSError` crashes.
5.  **Physical Existence**: If a `root` path is provided to the checker, it verifies that the parent reference points to a valid file or directory relative to that root.

Failure in any of these checks results in a `ProofStatus.INVALID` for that file.

### Directory Validation (L0)
Dendron checks for the presence of a `PROOF.md` file in the directory. The absence of this file for a non-exempt directory results in a `MISSING` status.

## 3. Exemptions
Default exemptions include:
- `__pycache__`
- `.git`
- `.venv`
- `.egg-info`

## 4. Coverage Calculation
`Coverage = ((OK + ORPHAN) / (Total Files - Exempt Files)) * 100`

- **ORPHAN** files are included in coverage as "locally justified" but technically incomplete.
- **Milestone**: As of 2026-02-01, the core `mekhane` module maintains **0 ORPHAN** files.
- A "passing" state (`is_passing`) requires **0 missing** and **0 invalid** proofs. Strict mode (failing on ORPHANs) is now supported for core developments.

## 5. Security & Hardening (v2.1 Iterative Remediation)

The following vulnerabilities identified in the 2026-02-01 Red-Team Audit have been remediated through an **Iterative Hardening Cycle** (Audit → Fix → Audit).

| Issue | Status | Remediation |
| :--- | :--- | :--- |
| **Logic-Only Linking** | ✅ FIXED | Implemented physical path existence check in `validate_parent()`. |
| **Path Traversal** | ✅ FIXED | Explicitly reject `..` in parent strings (Blocked at line 140). |
| **Absolute Paths** | ✅ FIXED | Explicitly reject `/` prefix. |
| **Dead Code** | ✅ FIXED | Removed `PROOF_PATTERN` (v1) and updated `SPECIAL_PARENTS`. |
| **Docstring Hijack** | ✅ FIXED | Only parse lines starting with `#` (`_is_code_comment`). |
| **Level Spoofing** | ✅ FIXED | Strict prefix validation (`L1/L2/L3` only) in `_parse_level`. |
| **Memory DoS** | ✅ FIXED | Implemented `MAX_FILE_SIZE` (10MB) limit. |

### Iteration 1 Summary
- **Start**: 2 Vulnerabilities, 2 Dead Code paths. (Path Traversal, Absolute Path).
- **Remediation**: 100% of reported issues fixed in v2.1.

### Iteration 3 (Quality & QA) Summary
- **Targets**: Edge cases and boundary conditions (Fuzzing).
- **Remediation (v2.3)**: Fixed binary file detection (T2 bug).
- **Remediation (v2.4)**: Fixed path length crash (R4-6 bug).
- **Final Result**: 100% pass on 26 combined logic and edge-case vectors.

**Future Hardening Targets**:
- Recursive cycle detection in the deductive graph.
- Checksum-based proof integrity.
