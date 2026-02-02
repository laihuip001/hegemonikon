# FEP Interactive Demo Utility

## 1. Overview

The `fep_demo.py` script serves as the primary empirical verification tool for the Hegemonikón FEP agent. It bridges the natural language processing layer (`encoding.py`) with the cognitive inference layer (`fep_agent.py`), allowing for real-time interaction and world-model adaptation.

## 2. Usage

To launch the interactive REPL:

```bash
python scripts/fep_demo.py -i
```

## 3. Core Features

### 3.1 Text-to-Inference Pipeline

Any natural language input provided at the `fep>` prompt is automatically processed through the following pipeline:

1. **Encoding**: `encode_to_flat_index(text)` maps the input to a discrete observation (0-7).
2. **Inference**: `agent.infer_states(obs)` updates beliefs and calculates entropy.
3. **Learning**: `agent.update_A_dirichlet(obs)` adapts the likelihood model immediately.
4. **Policy Selection**: `agent.infer_policies()` evaluates and recommends an action (`observe` vs `act`).

### 3.2 REPL Commands

| Command | Description |
| :--- | :--- |
| `/help` | Displays command list and usage. |
| `/entropy` | Shows current belief entropy (measure of uncertainty). |
| `/diff` | Displays the L1 norm difference in the A-matrix since initialization (learning delta). |
| `/history` | Lists the most recent input-observation-action triplets. |
| `/save` | Persists the current learned A-matrix to disk. |
| `/load` | Restores a previously saved A-matrix. |
| `/reset` | Reinitializes the agent with default priors. |
| `/quit` | Exits the interactive session. |

## 4. Experimental Value

The utility provides a "cognitive laboratory" for the Hegemonikón framework:

- **Entropy Monitoring**: Users can observe how consistent input leads to belief convergence (lower entropy).
- **Learning Verification**: The `/diff` command quantifies how much the agent's internal model of observation-state relationships has shifted.
- **Action Prototyping**: Allows for the fine-tuning of the policy selection layer to ensure that "deep thinking" (`observe`) is triggered appropriately during periods of high uncertainty.

## 5. Implementation Notes

### 5.1 Commit Reference

- **Commit**: `379fbb0e` (2026-01-28)
- **Changes**: Added REPL mode, command parser, and Dirichlet learning loop.

### 5.2 Technical Insight: Belief Structure

During implementation, a bug was identified where `agent.beliefs` returned a nested structure (list or object-dtype ndarray) from `pymdp`.

- **Fix**: Implemented a robust belief extractor in `get_entropy()` to handle both flat and nested belief arrays:

  ```python
  if isinstance(beliefs, np.ndarray) and beliefs.dtype == object:
      qs = np.asarray(beliefs[0], dtype=np.float64).flatten()
  ```

## 6. Real-time Feedback Example (v3.2)

When used within a workflow like `/noe`, the FEP layer provides formatted cognitive feedback based on state space inference:

```text
📥 入力: X-series とは何か？その本質を問い直す
📊 観察値: context=ambiguous, urgency=low, conf=medium

━━━ FEP Cognitive Feedback ━━━
┌─[Active Inference Layer]──────────────────┐
│ 観察値: context=ambiguous, urgency=low, conf=medium
│ 信念状態:
│   phantasia: clear
│   assent: withheld
│   horme: passive
│ エントロピー: 1.98 (中程度の不確実性)
│ 推奨: act (50%)
│   → 結論に確信あり、行動に移行可能
└────────────────────────────────────────────┘

✅ エントロピー安定 (1.98) → 分析続行可能
```

---
*Verified Implementation: 2026-01-29 — Cognitive Feedback Standard v1.0*
