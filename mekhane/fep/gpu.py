# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: FEP 計算用 GPU ユーティリティ — 認知シミュレータの計算基盤
"""
GPU Utilities for FEP Computation

GPU を「LLM の箱」から「認知シミュレータ」に転換する共通基盤。
attractor.py, fep_agent.py 等の行列演算を GPU で加速する。

Usage:
    from mekhane.fep.gpu import get_device, to_tensor, batch_cosine_similarity

    device = get_device()
    prototypes = to_tensor(numpy_array, device)
    similarities = batch_cosine_similarity(query, prototypes)
"""

from __future__ import annotations

from typing import Optional

import numpy as np

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def get_device(force_cpu: bool = False) -> "torch.device":
    """CUDA 可用性チェック + デバイス選択."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for GPU acceleration")

    if force_cpu:
        return torch.device("cpu")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def to_tensor(
    array: np.ndarray,
    device: Optional["torch.device"] = None,
    dtype: Optional["torch.dtype"] = None,
) -> "torch.Tensor":
    """numpy → GPU tensor 変換."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required")

    if device is None:
        device = get_device()
    if dtype is None:
        dtype = torch.float32

    return torch.tensor(array, dtype=dtype, device=device)


def batch_cosine_similarity(
    query: "torch.Tensor",
    targets: "torch.Tensor",
) -> "torch.Tensor":
    """バッチ cosine similarity — 1 回の行列演算で全ターゲットとの類似度を計算.

    Args:
        query: (D,) or (N, D) — クエリベクトル
        targets: (M, D) — ターゲット行列 (e.g. 6 Series prototypes)

    Returns:
        (M,) or (N, M) — 各ターゲットとの cosine similarity
    """
    if query.dim() == 1:
        query = query.unsqueeze(0)  # (1, D)

    # L2 normalize
    query_norm = torch.nn.functional.normalize(query, p=2, dim=-1)
    targets_norm = torch.nn.functional.normalize(targets, p=2, dim=-1)

    # (N, D) @ (D, M) → (N, M)
    similarities = query_norm @ targets_norm.T

    # Squeeze if single query
    if similarities.shape[0] == 1:
        return similarities.squeeze(0)  # (M,)

    return similarities
