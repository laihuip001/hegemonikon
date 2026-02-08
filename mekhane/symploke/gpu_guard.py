#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→GPU競合防止が必要→gpu_guard が担う
"""
GPU Guard — GPU リソース競合を防止するユーティリティ

PURPOSE:
    単一 GPU 環境 (RTX 2070 SUPER 8GB) で、長時間実行プロセス (gnosis_chat, LLM 推論等) が
    GPU を占有している場合に、新規プロセスの CUDA 初期化がブロックされてハングする問題を防止する。

USAGE:
    from mekhane.symploke.gpu_guard import gpu_preflight, force_cpu_env

    # GPU 状態チェック
    status = gpu_preflight()
    if not status.gpu_available:
        print(f"GPU busy: {status.reason}")

    # 強制 CPU 環境を設定
    force_cpu_env()  # os.environ["CUDA_VISIBLE_DEVICES"] = ""
"""

import os
import subprocess
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GPU_UTIL_THRESHOLD = 80      # GPU utilization % above which we consider it busy
GPU_MEM_THRESHOLD_MB = 6000  # Memory usage (MiB) above which we consider it busy
VRAM_TOTAL_MB = 8192         # RTX 2070 SUPER VRAM


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class GPUStatus:
    """GPU プリフライトチェック結果"""
    gpu_available: bool       # True if GPU is available for new processes
    utilization: int          # GPU utilization %
    memory_used_mb: int       # Memory used (MiB)
    memory_total_mb: int      # Memory total (MiB)
    blocking_process: Optional[str]  # Process name blocking GPU (if any)
    reason: str               # Human-readable status


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------

def gpu_preflight() -> GPUStatus:
    """
    GPU プリフライトチェック — GPU が新しいプロセスで使えるか判定

    Returns:
        GPUStatus with availability and details
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return GPUStatus(
                gpu_available=False,
                utilization=0,
                memory_used_mb=0,
                memory_total_mb=0,
                blocking_process=None,
                reason="nvidia-smi failed",
            )

        line = result.stdout.strip()
        parts = [p.strip() for p in line.split(",")]
        utilization = int(parts[0])
        memory_used = int(parts[1])
        memory_total = int(parts[2])

        # Check if GPU is busy
        is_busy = utilization > GPU_UTIL_THRESHOLD or memory_used > GPU_MEM_THRESHOLD_MB

        blocking = None
        reason = "GPU available"

        if is_busy:
            # Find blocking process
            blocking = _find_blocking_process()
            reason = (
                f"GPU busy: util={utilization}%, "
                f"mem={memory_used}/{memory_total}MiB"
            )
            if blocking:
                reason += f" (by {blocking})"

        return GPUStatus(
            gpu_available=not is_busy,
            utilization=utilization,
            memory_used_mb=memory_used,
            memory_total_mb=memory_total,
            blocking_process=blocking,
            reason=reason,
        )

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return GPUStatus(
            gpu_available=False,
            utilization=0,
            memory_used_mb=0,
            memory_total_mb=0,
            blocking_process=None,
            reason="nvidia-smi not available",
        )


def _find_blocking_process() -> Optional[str]:
    """GPU を占有している Python プロセスの名前を取得"""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-compute-apps=pid,process_name,used_memory",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            # Find the largest GPU consumer
            max_mem = 0
            max_name = None
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    try:
                        mem = int(parts[2])
                        if mem > max_mem:
                            max_mem = mem
                            max_name = parts[1]
                    except ValueError:
                        continue
            return max_name
    except Exception:
        pass
    return None


def force_cpu_env() -> None:
    """
    CUDA を無効化して CPU のみで実行させる。

    os.environ に設定するため、このプロセス内の全 torch/CUDA 操作に影響する。
    import torch の前に呼ぶ必要がある。
    """
    os.environ["CUDA_VISIBLE_DEVICES"] = ""


def ensure_safe_gpu() -> bool:
    """
    GPU が安全に使えるか確認し、使えない場合は CPU モードに切り替える。

    Returns:
        True if GPU is available, False if forced to CPU
    """
    status = gpu_preflight()
    if not status.gpu_available:
        force_cpu_env()
        return False
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    """GPU プリフライトチェック CLI"""
    status = gpu_preflight()
    icon = "🟢" if status.gpu_available else "🔴"
    print(f"{icon} GPU Status: {status.reason}")
    print(f"   Utilization: {status.utilization}%")
    print(f"   Memory: {status.memory_used_mb}/{status.memory_total_mb} MiB")
    if status.blocking_process:
        print(f"   Blocking: {status.blocking_process}")


if __name__ == "__main__":
    main()
