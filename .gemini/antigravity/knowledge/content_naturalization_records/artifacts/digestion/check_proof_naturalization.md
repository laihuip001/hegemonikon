# Internal Naturalization Case Study: `check_proof.py` to `Dendron`

> **Process**: `/eat+~/fit+*^/noe`
> **Date**: 2026-02-01
> **Subject**: Prototype script `mekhane/scripts/check_proof.py`

## 1. Analysis (Phase 1: 素材分析)

The subject was identified as an "Exploratory Prototype"—a script written to achieve immediate verification before a formal architecture was designed.

**Components extracted:**
- PROOF Header detection (Regex-based).
- Level distribution statistics (L1/L2/L3).
- Scope-lock (Hardcoded to `mekhane/`).
- CI Integration (Basic exit codes).

## 2. Cooking (Phase 2: 調理 /mek)

The "nutrients" (core features) were extracted and recast into the `Dendron` native architecture.

- **Level Stats**: Re-implemented as a first-class citizen in `DendronChecker` using `collections.Counter`.
- **Reporting**: Integrated into the multi-format `DendronReporter`.
- **Interface**: The CLI was unified; the legacy script was downgraded to a delegation wrapper.

## 3. Digestion Diagnosis (Phase 3: 消化診断 /fit)

**Digestion Level: 🟢 Naturalized**

- **Boundary Residuals**: Zero. `Dendron` now owns the logic; the legacy path is purely for backward compatibility.
- **Functional Overlap**: Resolved by converting the legacy script into a "Proxy".
- **Augmentation Score**: 5/5. Dendron now provides level statistics to all directories, not just mekhane.

## 4. Meta-Insights (Phase 4: /noe 深層認識)

The naturalization revealed that early prototypes serve as "Implicit Specifications". Though the code of `check_proof.py` was replaced, its *intent* (specifically the need for L1/L2/L3 statistics) was critical for the maturity of the final product. 

This confirms the strategy of **"Recoverability over Autonomy"**: rather than deleting the old script and breaking dependencies, we naturalized its function into the core and maintained the interface, ensuring a smooth evolutionary path.
