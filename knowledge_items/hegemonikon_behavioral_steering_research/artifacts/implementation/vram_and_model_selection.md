# Implementation: VRAM Management and Model Selection (8GB GPU)

## 1. Hardware Context

The local compute host utilizes an **NVIDIA GeForce RTX 2070 SUPER (8GB VRAM)**. While 8GB is theoretically sufficient for 7B models in 4-bit quantization, real-world constraints often lead to CUDA Out-of-Memory (OOM) errors.

### 1.1. GUI Overhead (The Hidden Cost)

Running a full desktop environment (GNOME, Xorg, Firefox) consumes significant VRAM before any model is loaded:

- **Xorg/Gnome-shell**: ~200MB - 500MB
- **Browser/Antigravity Desktop**: ~100MB - 300MB
- **Total Overhead**: ~0.5GB - 0.8GB

This leaves only ~7.2GB - 7.5GB available for PyTorch.

## 2. Model Compatibility Matrix

| Model | Size | Quantization | VRAM (Est.) | Status on 8GB (w/ GUI) |
| :--- | :--- | :--- | :--- | :--- |
| **Mistral 7B v0.3** | 7B | 4-bit (NF4) | ~5.5GB - 6.5GB | **Fragile/OOM** |
| **Qwen 2.5 7B** | 7B | 4-bit (NF4) | ~5.5GB - 6.5GB | **Fragile/OOM** |
| **Qwen 2.5 1.5B** | 1.5B | BF16 / 4-bit | ~1.5GB - 3.0GB | **Stable** ✅ |
| **Llama 3.2 1B** | 1B | BF16 | ~2.5GB | **Stable** ✅ |

### 2.1. Why Mistral 7B Fails

Even with 4-bit quantization, the activation memory and KV cache during inference, combined with the `llm-steer` wrapper overhead, easily exceed the remaining ~7.2GB buffer.

**Error recorded (2026-02-06):**
> `torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 112.00 MiB. GPU 0 has a total capacity of 7.77 GiB of which 37.19 MiB is free.`

## 3. Recommended Fallback Strategy

When a 7B model fails due to OOM, the system should downgrade to a high-quality "Small Language Model" (SLM) to ensure behavioral steering experiments can proceed.

- **Primary Fallback**: `Qwen/Qwen2.5-1.5B-Instruct`
- **Configuration**: Can be run in 4-bit (bitsandbytes) for maximum headroom or FP16 for precision.
- **Layer Adjustment**: SLMs have fewer layers (e.g., 28 for Qwen 1.5B vs 32 for Mistral 7B). Adjust the `LAYER` parameter in `llm-steer` accordingly (typically `total_layers // 2`).

## 4. VRAM Optimization Tips

- **Unbuffered Execution**: Use `PYTHONUNBUFFERED=1` or `python -u` to see logs and memory usage in real-time.
- **Garbage Collection**: Manually call `torch.cuda.empty_cache()` if switching models in the same session.
- **Memory Management**: Set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` to reduce fragmentation.

---
*Created: 2026-02-06. References: conversation_id: bot-c4c1ec1e-0c4b-45b1-8a99-547069343e56*
