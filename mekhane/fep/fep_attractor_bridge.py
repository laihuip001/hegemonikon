# PROOF: [L1/FEP] <- mekhane/fep/
# PURPOSE: FEP A行列の学習結果を Attractor の basin 感度にフィードバックする
"""
FEP → Attractor Feedback Bridge

Active Inference の A 行列 (observation likelihood) の topic 行 (rows 8-13) から
Series 認識精度を抽出し、SeriesAttractor の similarity bias に変換する。

これにより閉じた Active Inference ループが実現される:

    Input → Attractor → FEP Agent → Learn A → ┐
    ┌──────────────────────────────────────────┘
    └→ Extract topic precision → Attractor bias → (next cycle)

FEP 的解釈:
- A 行列の topic 行は「この観測値がこの状態を示す確率」
- Dirichlet 学習で強化された行 = Agent がその Series を確信度高く認識する
- この確信度を Attractor の similarity に微小バイアスとして注入
- 結果: 経験的に確認された Series への感度が上がる
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
    from mekhane.fep.attractor import SeriesAttractor

# Series ↔ topic observation index (A行列の行 8-13)
_TOPIC_ROW_MAP = {"O": 8, "S": 9, "H": 10, "P": 11, "K": 12, "A": 13}

# A行列のtopic行からSeries応答確率を抽出し、状態次元で平均化する
_SERIES_LIST = ["O", "S", "H", "P", "K", "A"]

# 最大 bias magnitude: ±0.03 per extraction
# 理由: Attractor の similarity gap は ~0.005-0.01 が boundary
# ±0.03 は gap を反転させるのに十分だが、明らかに正しい分類を壊すほど大きくない
MAX_BIAS = 0.03

# 全ソースからの累積バイアス上限: ±0.05
# スケーラビリティガード: N cycles でも bias が発散しない
MAX_CUMULATIVE_BIAS = 0.05


# PURPOSE: A行列 topic 行から per-Series 精度バイアスを抽出
def extract_topic_bias(agent: "HegemonikónFEPAgentV2") -> dict[str, float]:
    """A行列 topic 行から per-Series 精度バイアスを抽出する。

    A行列 shape: (14, 48)
    - Rows 8-13 = topic modality (O, S, H, P, K, A)
    - Columns = 48 hidden states (phantasia × assent × horme × series)

    各 Series s について:
    1. A[topic_row(s), :] の平均値 = この topic が全状態にどれくらい反応するか
    2. 全 Series の平均との差分 = 相対的な精度
    3. MAX_BIAS でクリップ

    Returns:
        {series: bias_value} — 正=感度UP、負=感度DOWN
    """
    A = agent._get_A_matrix()  # (14, 48)

    # topic 行の平均値を各 Series ごとに計算
    topic_means = {}
    for series, row_idx in _TOPIC_ROW_MAP.items():
        topic_means[series] = float(A[row_idx, :].mean())

    # 全 Series の平均
    global_mean = np.mean(list(topic_means.values()))

    if global_mean < 1e-10:
        return {s: 0.0 for s in _SERIES_LIST}

    # 偏差を正規化してバイアスに変換
    biases = {}
    for series in _SERIES_LIST:
        deviation = (topic_means[series] - global_mean) / global_mean
        biases[series] = float(np.clip(deviation * MAX_BIAS, -MAX_BIAS, MAX_BIAS))

    return biases


# PURPOSE: Attractor に A行列由来のバイアスを注入 (idempotent + cap)
def apply_fep_bias_to_attractor(
    agent: "HegemonikónFEPAgentV2",
    attractor: "SeriesAttractor",
) -> dict[str, float]:
    """A行列の学習結果を Attractor の similarity bias に注入する。

    スケーラビリティ設計:
    - FEP bias は毎回 **置換** (加算ではない) — N cycles で発散しない
    - BasinBias (Problem C) からの既存バイアスは保持
    - 合計値は MAX_CUMULATIVE_BIAS でクリップ

    Returns:
        適用されたバイアス辞書 (デバッグ/ログ用)
    """
    biases = extract_topic_bias(agent)

    # FEP 固有のバイアスを追跡 (前回値を除去 → 置換)
    if not hasattr(attractor, "_fep_bias"):
        attractor._fep_bias = {}

    for series, bias in biases.items():
        # 前回の FEP bias を除去
        old_fep = attractor._fep_bias.get(series, 0.0)
        current = attractor._bias_adjustments.get(series, 0.0)
        base = current - old_fep  # BasinBias のみ残す

        # 新しい FEP bias を加算 + 累積キャップ
        new_total = float(np.clip(
            base + bias, -MAX_CUMULATIVE_BIAS, MAX_CUMULATIVE_BIAS
        ))
        attractor._bias_adjustments[series] = new_total
        attractor._fep_bias[series] = bias

    return biases

