# Dendron Usage & Auditing Workflows

Dendron provides both a command-line interface and an agent-accessible workflow (`/dendron`) for existence proof audits.

## 1. CLI Usage

### Basic Check
Verifies all files and directories starting from the current paths.
```bash
python3 -m mekhane.dendron check mekhane/
```

### Options
- `--coverage`: Output only the coverage summary.
- `--ci`: CI mode (exit code 1 on failure).
- `--strict`: Treats ORPHAN files as hard failures.
- `--format {text, markdown, json, ci}`: Specify report style.
- `--no-dirs`: Skip directory `PROOF.md` validation.

---

## 2. Workflow: `/dendron` (Existence Proof Audit)

The `/dendron` workflow (implemented in CCL) automates the verification of deductive necessity.

### 2.1 Operators (Cognitive Algebra)

| Operator | Meaning | Output |
|:---------|:--------|:-------|
| `/dendron+` | **Deep Check** | Full scan including subdirectories, detailed report. |
| `/dendron-` | **Quick Check** | Shallow scan of current path, minimal output. |
| `/dendron*` | **Meta Check** | Verification of Dendron's own PROOF integrity. |
| `/dendron~` | **Compare** | Comparative analysis against the "100% Stable" state. |

### 2.2 Configuration Parameters

| Parameter | Description |
| :--- | :--- |
| **Scope** | Target directory tree (e.g., `mekhane/`, `kernel/`). |
| **Granularity**| `file` (headers), `dir` (PROOF.md), or `all`. |
| **Format** | `text`, `json`, `markdown`, `ci`. |
| **Recovery** | Propose parent references for missing/orphan proofs. |

---

## 3. Reporting Formats

1. **TEXT (Default)**: Human-readable summary.
2. **MARKDOWN**: Tabular data for documentation or PR comments.
3. **JSON**: For machine/agent consumption.
4. **CI**: Minimal output for build logs.

## 4. Integration Scenarios

- **Pre-Commit**: Locally ensure new files have valid proofs.
- **Milestone Review**: Verify system-wide deducibility from axioms.
- **Hardening Cycles**: Audit for path traversal or logic bypasses using `/mek+` + `/dendron`.
