# implementation: `llm-steer` Library API Reference

## 1. Library Overview

`llm-steer` is a lightweight library for adding steering vectors to transformer models by hooking into the residual stream at specific layers.

## 2. Core API Methods (Verified)

As verified by `dir(Steer)` during implementation on 2026-02-06:

| Method | Description |
| :--- | :--- |
| **`add(layer, coeff, text)`** | Adds a steering vector derived from `text` to the specified `layer`. |
| **`reset_all()`** | Removes all active steering vectors from the model. |
| **`reset(layer)`** | Removes steering vectors from a specific layer. (Note: behavior may vary by version). |
| **`get_all()`** | Returns a list of all active steers. |
| **`steers`** | Property/List of active steer objects. |

### 2.1. Initialization Pattern

```python
from llm_steer import Steer
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(...)
tokenizer = AutoTokenizer.from_pretrained(...)
steerer = Steer(model, tokenizer)
```

### 2.2. Common Pitfall: `remove_all`

Legacy documentation or early versions may refer to `remove_all()`. In the current implementation (v2.0.1+), use **`reset_all()`** or **`reset()`**.

## 3. Implementation Workflow

1. **Define Prompts**: Create contrastive prompts (e.g., "be polite" vs "be rude").
2. **Apply Steer**: `steerer.add(layer=16, coeff=0.5, text="be polite")`.
3. **Generate**: Use `model.generate()` as usual; the hooks automatically modify activations.
4. **Clear**: `steerer.reset_all()` to return to the baseline model.

---
*Created: 2026-02-06. References: conversation_id: bot-c4c1ec1e-0c4b-45b1-8a99-547069343e56*
