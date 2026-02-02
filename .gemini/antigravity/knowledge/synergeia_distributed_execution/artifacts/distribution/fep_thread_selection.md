# Distribution: FEP-Based Thread Selection

On 2026-02-01, Synergeia was upgraded with a **FEP-based cognitive router** (`fep_selector.py`), implementing a sophisticated thread selection mechanism based on the Free Energy Principle.

## 1. Objective

To optimize resource allocation by matching the cognitive complexity of a CCL expression with the appropriate execution environment (Manual/Deep vs. Automated/High-Speed).

## 2. Complexity Estimation

The selector (`estimate_ccl_complexity`) calculates a score (0.0 - 1.0) based on several factors:

- **Workflow Weights**: `/noe` (0.8), `/bou` (0.7), `/dia` (0.6), down to `/sop` (0.2).
- **Operators**: `>>` (convergence) adds 0.2, `!` (full expansion) adds 0.15, `+` (deepening) adds 0.1.
- **Control Structures**: `F:`, `I:`, `W:`, `L:` add 0.2.

## 3. Thread Mapping

| Complexity Score | Level | Target Thread | Rationale |
| :--- | :--- | :--- | :--- |
| **0.7 - 1.0** | High | `antigravity` | Deep cognitive processing required. |
| **0.4 - 0.7** | Medium | `claude` | Structured logic/formatting. |
| **0.0 - 0.4** | Low | `perplexity` | Information retrieval / basic query. |

## 4. Active Inference Integration

The selector integrates with `mekhane/fep/fep_bridge.py`:

- **noesis_analyze**: Estimates the confidence of the recommendation based on the current cognitive state.
- **Uncertainty-Awareness**: If complexity is high, the system defaults to "Antigravity" (human/deep manual mode) to reduce the risk of autonomous failure.

## 5. Implementation in Coordinator

The `select_thread` function in `coordinator.py` was extended to utilize the FEP selector by default:

```python
def select_thread(ccl: str, use_fep: bool = True):
    if use_fep:
        recommendation = select_thread_by_fep(ccl)
        return recommendation.thread
    # ... rule-based fallback
```

---
*Reference: synergeia/fep_selector.py (2026-02-01)*
