# Methodology: Activation Steering Setup

## 1. Runtime Environment

### 1.1. Required Packages

The following stack is required for local steering experiments:

```bash
# Recommended environment for RTX 2070 SUPER (CUDA 12.4)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install llm-steer transformers accelerate bitsandbytes jupyter
```

### 1.2. Hardware Capability Check

Ensure CUDA is available and the GPU is correctly mapped:

```python
import torch
assert torch.cuda.is_available()
print(f"Device: {torch.cuda.get_device_name(0)}") # Expected: NVIDIA GeForce RTX 2070 SUPER
# Check for GUI overhead (GNOME/Xorg usually takes ~500MB+)
print(f"Memory allocated: {torch.cuda.memory_allocated(0) / 1e6:.1f}MB")
```

## 2. Steering Workflow (Phase A-D)

### Phase A: Environment & Base Model

- **Model Selection (8GB VRAM Constraint)**:
  - **Mistral-7B-Instruct-v0.3 (4-bit)**: Baseline for high deductive resolution, but prone to OOM on hosts with GUI overhead (GNOME/Xorg).
  - **Qwen2.5-1.5B-Instruct**: Recommended fallback for stable local execution on consumer GPUs with < 8GB available VRAM.
- Initialize using `BitsAndBytesConfig` for explicit quantization control.

### Phase B: Vector Extraction (Contrastive Prompting)

- Generate "Positive" (CCL-compliant) and "Negative" (Non-compliant) prompts.
- Extract the contrastive activation vectors from the residual stream across multiple layers.

### Phase C: Steering Application

- Use `llm-steer` to apply the extracted vectors during inference.
- **Important**: Use `steerer.reset()` or `steerer.reset_all()` to clear previous vectors (the API may differ from earlier documentation where `remove_all` was suggested).
- Calibrate the steering coefficient (alpha/coeff) to balance alignment and fluency (typically 0.1 - 1.0).

### Phase D: Evaluation

- Compare steered vs. unsteered outputs using the `sel_validator`.
- Document failure modes (e.g., "over-steering" causing gibberish).

## 3. Troubleshooting & Failure Notes (2026-02-06)

### 3.1. Initialization Error (load_in_4bit)

**Symptom**: `TypeError: MistralForCausalLM.__init__() got an unexpected keyword argument 'load_in_4bit'`

**Context**: Occurred when attempting to load `Mistral-7B-Instruct-v0.3` using `from_pretrained(..., load_in_4bit=True)` on Python 3.13 with `transformers` v4.49.0+.

**Root Cause**: In recent `transformers` versions, `load_in_4bit` is no longer a direct argument of `from_pretrained`. It must be passed via `quantization_config`.

**Fix**:

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
quant_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=quant_config)
```

## 4. Reference Implementation
