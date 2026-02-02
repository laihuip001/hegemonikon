# Active Inference パラメータ: Hegemonikón フレームワークの経験的根拠

> **Source**: Perplexity Deep Research (2026-01-28)
> **Cutoff**: 2025-03 (過去3年以内)
> **Confidence**: Medium-High

---

## エグゼクティブ・サマリー

Active Inference の A/B/C/D 行列パラメータに関する 50+ 文献を精査した結果:

- **具体的数値は限定的** — 理論文献は豊富だが実装論文は少ない
- **タスク特性に応じた個別キャリブレーション** が必要
- pymdp 実装例から **小規模状態空間（8-16 状態）向けの推奨値セット** を構築

---

## パラメータ推奨値: 構造化テーブル

| パラメータ | 推奨値/範囲 | 根拠論文 | 検証状態 |
|:-----------|:-----------|:---------|:---------|
| **A: 高信頼度** | 0.7–0.9 | pymdp tutorial | ✅ 文献根拠 |
| **A: 低信頼度** | 0.1–0.3 | pymdp multi-armed bandit | ✅ 文献根拠 |
| **A: Dirichlet α** | 1.0 (対称) | Da Costa et al. (2020) | ✅ 文献根拠 |
| **B: 決定的遷移** | 1.0 | pymdp grid-world | ✅ 文献根拠 |
| **B: 確率的遷移** | 0.8–0.95 | 実装例 | ⚠️ 経験的 |
| **C: 高い好み** | +2.0 to +3.0 | Gijsen et al. (2022) | ✅ 文献根拠 |
| **C: 中程度** | +1.0 to +2.0 | 実装例 | ⚠️ 経験的 |
| **C: 回避** | -1.0 to -3.0 | 実装例 | ⚠️ 経験的 |
| **D: 均一分布** | [0.5, 0.5] | デフォルト | ✅ 理論根拠 |
| **D: 弱バイアス** | [0.6, 0.4] | 学習後の傾向 | ⚠️ 経験的 |
| **γ (ポリシー精度)** | 16.0 | pymdp Agent 初期値 | ✅ 実装根拠 |
| **β (逆温度)** | 1.0–4.0 | Gijsen et al. | ✅ 文献根拠 |
| **α (EFE係数)** | 16.0 | pymdp 初期値 | ✅ 実装根拠 |
| **lr_pA** | 1.0 | pymdp 初期値 | ✅ 実装根拠 |
| **lr_pD** | 0.5 | 推奨 | ⚠️ 経験的 |

---

## Hegemonikón 具体値

### 現在の実装 vs 推奨値

| パラメータ | 現在値 | 推奨値 | 判定 |
|:-----------|:-------|:-------|:-----|
| A: clear→clear | 0.9 | 0.7–0.9 | ✅ 範囲内 |
| A: unclear→ambiguous | 0.7 | 0.7–0.9 | ✅ 範囲内 |
| A: granted→high_conf | 0.7 | 0.7–0.9 | ✅ 範囲内 |
| A: withheld→low_conf | 0.5 | 0.1–0.3 | ⚠️ 高すぎ |
| B: observe clarifies | 0.6 | 0.8–1.0 | ⚠️ 低すぎ |
| C: clear context | +2.0 | +2.0–+3.0 | ✅ 範囲内 |
| C: ambiguous | -2.0 | -1.0–-3.0 | ✅ 範囲内 |
| D: uncertain bias | 0.6 | 0.5–0.7 | ✅ 範囲内 |

### 修正推奨

1. **A[withheld→low_conf]**: 0.5 → **0.3** (Epochē をより強く表現)
2. **B[observe→clear]**: 0.6 → **0.8** (観察の効果を強化)

---

## キャリブレーション・検証方法

### 定量指標

| 指標 | 目標値 |
|:-----|:-------|
| VFE (収束後) | < 5.0 |
| Accuracy (100試行後) | > 0.85 |
| Information Gain | 0.3–0.5 bits/試行 |

### 感度分析対象

| パラメータ | テスト値 |
|:-----------|:---------|
| γ | {4.0, 8.0, 16.0, 32.0} |
| λ | {0.5, 1.0, 2.0, 4.0} |

---

## 主要参考文献

1. **Smith, R., Friston, K., Whyte, C. (2022)** — "A step-by-step tutorial on active inference"
2. **pymdp Contributors (2024)** — pymdp documentation
3. **Da Costa, L., et al. (2020)** — "Active inference on discrete state-spaces: A synthesis"
4. **Gijsen, S., et al. (2022)** — "Active inference and the two-step task"
5. **Parr, T., Pezzulo, G., Friston, K. (2022)** — "Active Inference" (MIT Press)
6. **Prakki, R. (2024)** — arXiv:2412.10425 (STOIC Architecture)

---

*Active Inference Parameter Research Report v1.0*
*Source: Perplexity Deep Research 2026-01-28*
