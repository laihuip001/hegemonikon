# Activation Steering 調査レポート

> **Date**: 2026-02-01
> **Goal**: CCL 遵守率 96%+ に向けた推論操作技術の調査

---

## エグゼクティブサマリー

**結論**: Hegemonikón での直接適用は **不可** だが、OSS LLM での PoC は **実現可能**。

| 項目 | 状況 |
|:-----|:-----|
| Claude/Gemini API | ❌ Steering 未サポート |
| OSS LLM (LLaMA, Mistral) | ✅ 完全対応 |
| 推奨フレームワーク | **EasySteer** (vLLM 統合) |
| 実験工数 | M (4-8時間) |

---

## 2025-2026 最新研究

### 1. Instruction Following 強化 (ICLR 2025)

Microsoft Research による研究。Steering vector で instruction-following を向上。
- 出力形式、長さ、特定語句の包含を制御可能
- **Cross-model transfer**: instruction-tuned モデルから base モデルへ転移可能

### 2. AdaRAS — 推論信頼性向上 (2026-01)

"Reasoning-Critical Neurons" を特定し、推論時に steering。
- 数学・コーディングタスクで **+13%** 精度向上
- 追加学習不要

### 3. EasySteer (2025-09)

vLLM 上に構築された統合 steering フレームワーク。
- 既存手法比 **5.5-11.4x** 高速
- 複数 steering vector 同時適用可能
- モジュラー設計で拡張容易

### 4. llm_steer ライブラリ

HuggingFace transformers 統合の Python モジュール。
- LLaMA, Mistral, Phi, StableLM 対応
- シンプル API:
  ```python
  steerer.add_steering_vector(layer=12, coeff=0.8, text="CCL遵守")
  ```

---

## CCL 遵守への応用シナリオ

### Contrastive Prompt Pairs

```
Positive: "/boot+ を実行し、全18ステップを確実に完了してください"
Negative: "/boot+ を実行してください（省略可）"
```

中間層の活性化差分から "CCL 遵守 vector" を抽出。

### 対象レイヤー

Middle layers (8-16) が最も効果的 (研究知見)。

### 期待効果

| Before | After |
|:-------|:------|
| 自然言語義務のみ (SEL) | 活性化レベルでの傾向注入 |
| 90% 遵守 | 理論上 95%+ 可能 |

---

## 実験計画 (PoC)

### 環境要件

| 項目 | 要件 |
|:-----|:-----|
| GPU | CUDA 対応 (8GB+ VRAM) |
| モデル | LLaMA 3 8B / Mistral 7B |
| フレームワーク | vLLM + EasySteer or llm_steer |

### ステップ

1. **環境構築** — vLLM + transformers インストール
2. **Vector 抽出** — Contrastive prompt で CCL 遵守 vector 生成
3. **Steering 適用** — middle layer に vector 注入
4. **評価** — `/boot+`, `/zet+` 等で遵守率測定
5. **比較** — SEL のみ vs SEL + Steering

### 検証基準

- 遵守率 (sel_validator 使用)
- 出力品質 (内容の自然さ)
- 副作用 (他タスクへの影響)

---

## 制約と Non-Goals

- ❌ Claude/Gemini API への統合 (技術的不可)
- ❌ Production 環境への即時導入
- ✅ 研究・実験としての知見蓄積

---

## 推奨アクション

| 優先度 | アクション |
|:-------|:-----------|
| 🔴 High | EasySteer リポジトリ調査 |
| 🟠 Medium | llm_steer で最小 PoC |
| 🟢 Low | AdaRAS 論文精読 |

---

*調査完了: 2026-02-01T16:10*
