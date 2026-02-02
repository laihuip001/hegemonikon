# Dendron v2: Parent Reference Specification & Migration Record

> **Status**: COMPLETED (2026-02-01)
> **Syntax**: `# PROOF: [LEVEL/CATEGORY] <- PARENT_REF`

## 1. Syntax Overview (Deductive Necessity)

To enforce the Deductive Necessity principle, every PROOF header must specify its logical parent. This established a verifiable deductive chain from the code up to architectural axioms.

### 1.1 The Reference Arrow (`<-`)

The `<-` symbol (alternatively `←`) represents the deductive flow. It points to the reason for the artifact's existence.

```python
# PROOF: [L2/インフラ] <- mekhane/dendron/
```

### 1.2 Parent Reference Types

| Reference | Type | Description |
| :--- | :--- | :--- |
| `FEP` | **Axiom** | Direct derivation from the Free Energy Principle. |
| `PATH/TO/REF` | **Path** | Reference to a directory or module that mandates this file. |
| `external:NAME` | **External** | Mandatory requirement from an external substrate (e.g., `external:Python`). |
| `legacy` | **Transition** | Temporary marker for files awaiting a proper deductive mapping. |

---

## 2. Checker v2 Data Model

The `DendronChecker` implements the following structure for v2/v2.1:

### 2.1 Extended FileProof

```python
@dataclass
class FileProof:
    path: Path
    status: ProofStatus
    level: Optional[ProofLevel] = None
    parent: Optional[str] = None
    line_number: Optional[int] = None
    reason: Optional[str] = None
```

### 2.2 Proof Statuses (v2)

- **OK**: Valid existence proof with parent reference found and verified.
- **ORPHAN**: The file has a PROOF header, but the mandatory parent reference is missing. Triggers a warning.
- **INVALID**: Parent reference exists but fails validation (e.g., non-existent path, traversal attack).

### 2.3 Coverage Logic

- **Coverage**: `(OK + ORPHAN) / CheckableFiles`. ORPHAN files are counted as "covered" because intent is present.
- **Passing**: CI passes if `Missing == 0` and `Invalid == 0`. ORPHAN status triggered warnings during migration Phase 1.

---

## 3. Migration Record (2026-02-01)

On 2026-02-01, the Hegemonikón core (`mekhane/`) underwent a full migration to Dendron v2.

### 3.1 Automated Migration: `migrate.py`

A specialized tool, `mekhane/dendron/migrate.py`, was used to process 240+ files.

**Parent Resolution Logic**:

1. **Package Level**: Files under a package (e.g., `__init__.py`) use the package directory as parent.
2. **Sub-Module Level**: Files in sub-directories use the relative directory path.
3. **Special Handling**: Manual overrides for `FEP` or `external` refs.

### 3.2 Result Summary

- **Target Count**: 241 files (Final metric after Synedrion migration).
- **Execution Success**: 100%
- **Final State**: 0 Orphans, 100% Coverage, 0 Invalid.

### 3.3 Subsystem Migration via Regex (Mass-Update)

For external subsystems (like `hermeneus/`) that already possess v1 PROOF tags, a mass-update strategy using `sed` is applied.

**The Trailing Description Pitfall**:
Most PROOF tags include trailing descriptions: `# PROOF: [L2/Infra] Compiler Logic`. A naive regex `s/]$/] <- parent\//` fails if characters exist after the bracket.

**Successful Pattern**:

```bash
# Capture the level and the trailing text separately to insert the parent ref
sed -i 's/^# PROOF: \[\([^]]*\)\] \([^<].*\)$/# PROOF: [\1] <- parent\/path\/ \2/' "$f"
```

This pattern ensures the deductive arrow is inserted *before* the description, maintaining readability and auditor compatibility.

---

## 4. Maintenance

The `migrate.py` tool remains in the repository for:

- Re-basing parents during directory restructuring.
- Mass-updating proofs for library migrations.
- Auditing deductive distance.
