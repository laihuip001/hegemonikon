# Local GPU Compute Host

## 1. Hardware Profile (Current Host)

Verified via `nvidia-smi` on 2026-02-06:

| Component | Specification |
| :--- | :--- |
| **GPU** | NVIDIA GeForce RTX 2070 SUPER |
| **VRAM** | 8GB (8192 MiB) GDDR6 |
| **Driver Version** | 550.163.01 |
| **CUDA Version** | 12.4 |

### Role in Hegemonikón

Unlike the CPU-limited RDP clients (e.g., Intel N100), this host serves as the primary execution engine for:

- Local LLM inference (Ollama / vLLM)
- Behavioral research (Activation Steering)
- High-volume data processing (Specialist runs)

## 2. GPU Task Persistence Pattern (Anti-Entropy)

To prevent hardware-bound tasks from being "buried" or forgotten during cross-platform migrations (GCP -> Local Host), Hegemonikón implements a specific persistence pattern.

### 2.1. The `gpu_required_tasks.md` Sentinel

- **Location**: `~/oikos/hegemonikon/docs/gpu_required_tasks.md`
- **Function**: Acts as a tombstone for tasks that cannot be executed on cloud VMs or lightweight clients.
- **Protocol**:
  1. When a task requires GPU but none is available, record it in this file.
  2. During the `/boot` workflow, the system checks for the existence of this file if a local GPU is detected.
  3. "Unburying" the tasks becomes an explicit ritual upon returning to the high-performance environment.

### 2.2. Current Active Tasks (as of 2026-02-06)

- **Activation Steering PoC**: 8h effort, T4+ equivalent required.
- **OpenManus Experiments**: Local agent execution testing.
- **Local LLM Benchmarking**: Qwen 2.5 / LLaMA 3 8B evaluation.
