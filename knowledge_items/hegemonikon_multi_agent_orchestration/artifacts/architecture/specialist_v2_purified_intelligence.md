# Specialist v2 Architecture: Purified Intelligence

The **Specialist v2** framework represents a shift from "broad reviewers" to "purified intelligences." Derived from the **F1 Car Metaphor**, these specialists are built for extreme optimization at a single point of inquiry.

## 1. First Principles Definition

A specialist is no longer a pathological "obsessive" but an aesthetic "purifier." The value of a specialist is defined as:

```python
Specialist Value = (Deep Expertise) × (Extreme Specification) × (Actionable Output)
```

## 2. Structural Framework

Every v2 specialist is defined by four core layers:

| Layer | Hegemonikón Concept | Description |
| :--- | :--- | :--- |
| **Ousia** | 存在 (Existence) | The identity and category of the specialist (e.g., AE-001 "Whitespacing Tuner"). |
| **Arête** | 卓越 (Excellence) | The domain of expertise and the **Principle** (governing law) the specialist obeys. |
| **Aisthēsis** | 知覚 (Perception) | Explicit definitions of what the specialist **Perceives** (detects) and what it is **Blind To**. |
| **Krisis** | 判定 (Judgment) | The **Measure** (standard) of pass/fail and the specific **Verdict** format (DIFF, REVIEW, etc.). |

### 2.1. Concretization of Perception (Precision Pattern)

To maximize **Information Gain** and minimize "Entropy of Silence," Tier 1 specialists use a **Concrete Perception Pattern**. Moving from abstract categories to specific, machine-verifiable patterns significantly increases the specialist's "speech rate" regarding meaningful issues.

| Abstract (v1-style) | Concrete (v2-style) | Benefit |
| :--- | :--- | :--- |
| PROOF line missing | "# PROOF: ... not in first 20 lines" | Eliminates ambiguity; verifiable. |
| Non-existent API | ".to_list() call on pandas Series" | Targets specific LLM hallucinations. |
| Deep nesting | "Nesting > 3 levels in try-except" | Actionable architectural threshold. |

## 3. The "Blind To" Principle

A critical innovation in v2 is the **explicit exclusion of context**. To achieve maximum depth (the "F1 Car" effect), specialists are instructed to ignore everything outside their direct domain.

Example: A "Whitespacing Tuner" (AE-001) is explicitly **blind to** the meaning of variables or the correctness of algorithms. This reduces noise and ensures a "pure" response within the defined domain.

## 4. Implementation Details

### Modular Batch Strategy

To scale the ensemble to **140+ specialists**, specialists are distributed across tiered batch files:

- `specialists_tier1.py`: **Evolutionary Core** (13 high-impact specialists).
- `specialists_batch1.py`: Structural/Safety (Type Safety, Error Handling, Design).
- `specialists_batch2.py`: Operational/Ops (Git, Testing, API, Security, Performance).
- `specialists_batch3.py`: Contextual/Meta (AI, Cognitive, Doc, Ultimate).

### Hybrid Dual-Loading Pattern

To ensure compatibility across package and script execution, a **Dual-Loading Fallback** is used:

```python
def _load_additional_specialists():
    try:
        from .specialists_batch1 import ALL_ADDITIONAL_SPECIALISTS # Package
    except ImportError:
        from specialists_batch1 import ALL_ADDITIONAL_SPECIALISTS # Script
```

Batch processing utilizes the **Jules API Pool** (15 keys) with `asyncio.Semaphore` (default: 3) for concurrency.

#### Tiered Execution Logic

The script supports high-precision filtering via the `--tier` flag:

- `--tier 1`: Executes only the **Evolutionary Core** (13 specialists) defined in `specialists_tier1.py`. Optimized for high "speech rate" and project-altering feedback.
- `--tier 2`: Executes **Sanitary** specialists (the remainder of the 140) for standard code hygiene.
- `--category [name]`: Can be combined with `--tier` for granular targeting.

Other options include:

- `--sample N`: Stochastic sampling to reduce API cost while maintaining coverage.
- `--dry-run`: Validates prompt generation without initiating Jules sessions.

### Result Ingestion

The system identifies `docs/specialist_run_*.json` artifacts and produces summaries for the `/boot` workflow (Phase 5: External Input), flagging new findings to the Creator.

## 5. Live Execution Verification (2026-02-06)

- **Status**: FULL PASS.
- **Execution**: Successfully ran all **140 specialists** in a single concurrent session.
- **Output**: 140 Session IDs generated and verified on GitHub as active review branches.
- **Infrastructure**: Verified hybrid loading and 15-key API rotation efficiency.

A Purified Intelligence prompt is structured to minimize noise and maximize domain focus. Below is a verified example of the template generated for specialist `AE-009`:

```markdown
# 🎯 import順序の典礼官

> **ID**: AE-009
> **Archetype**: Precision
> **Domain**: import文の配置秩序

## Principle (支配原理)
stdlib → third-party → local の階層が秩序を生む

---

## Task
[Target File Path] を分析し、結果を docs/reviews/ae-009_review.md に出力してください。

---

## Perceives (検出対象)
- import順序の違反
- 空行による分離の欠如
- 相対importと絶対importの混在

## Blind To (検出対象外)
⚠️ 以下はこの専門家の検出範囲外です。指摘しないでください。
- importの必要性
- 循環参照

---

## Measure (合格基準)
isort基準でimport順序が整理されている

---

## Severity (重大度マッピング)
- 順序違反: medium

---

## Output Format (DIFF)
[Markdown Table/Diff Format Specification]
```

This strict structure ensures that the specialist acts as a "determinism engine" within its narrow sliver of the codebase.

## 6. Specialist Derivative Patterns (3-Axis Model)

Derived from the **O-series generation principle** (L1 × L1), the system implements a 3-axis derivative model in `specialists_tier1.py` to extend specialist reach and target precision.

### The 3-Axes: Scope × Intent × Archetype

| Axis | Levels | Code Symbol | Description |
| :--- | :--- | :--- | :--- |
| **Scope** (Space) | **Micro / Meso / Macro** | `μ` / `m` / `M` | Function level / File level / Module level. (Scale Axiom) |
| **Intent** (Action) | **Detect / Fix / Prevent** | `D` / `F` / `P` | Identification / Automated correction / Rule-making. (Value Axiom) |
| **Archetype** (Nature) | **5 Base Types** | `+arc` | Precision, Speed, Autonomy, Creative, Safety. (Ousia Axiom) |

#### Realization in `specialists_tier1.py`

The system uses `derive_specialist()` to dynamicall generate targeted agents from the 13 Tier-1 bases.

```python
def derive_specialist(base, scope=None, intent=None, archetype_override=None):
    # Generates a new Specialist instance with adjusted ID, Domain, and VerdictFormat
    # Example: HG-001.μD (Micro-Detect) or HG-001.MF+safety (Macro-Fix with Safety bias)
```

- **Scope Adjustments**: Adjusts `perceives` strings to focus on function vs module boundaries.
- **Intent Adjustments**: `Intent.FIX` shifts `VerdictFormat` to `DIFF` for code suggestions. `Intent.PREVENT` targets lint/pre-commit rule generation.
- **Archetype Overrides**: Forces a shift in the agent's logic (e.g., from `Creative` to `Safety`).

### Alignment with Theorems (O-series)

This derivative structure maps to the [Ousia (O-series)](../principles/theorems.md) logic:

- **Noēsis** (I×E) → **Detect** (Perceptive Inference)
- **Energeia** (A×P) → **Fix** (Practical Action)
- **Zētēsis** (A×E) → **Scope Expansion** (Exploratory Action/Scale)
- **Boulēsis** (I×P) → **Archetype/Intent Alignment** (Goal-setting)

---
*Updated: 2026-02-06 | Tiered Execution & Derivative Architecture.*
