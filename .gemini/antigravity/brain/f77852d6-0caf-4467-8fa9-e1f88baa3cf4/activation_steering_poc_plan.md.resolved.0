# Activation Steering PoC 実験計画

> **Priority**: 🔵 Low (調査・実験)
> **Effort**: L (8h)
> **Deadline**: 2026-02 (2ヶ月以内)

---

## 目的

CCL 遵守率を推論レベルで向上させる Steering Vector の有効性を検証する。

---

## フェーズ

### Phase A: 環境構築 (2h)

- [ ] vLLM インストール (`pip install vllm`)
- [ ] llm_steer インストール (`pip install llm-steer`)
- [ ] LLaMA 3 8B or Mistral 7B ダウンロード
- [ ] GPU 環境確認 (CUDA, 8GB+ VRAM)

### Phase B: Vector 抽出 (2h)

- [ ] Contrastive prompt pair 設計
  - Positive: CCL 遵守を明示
  - Negative: 省略可能と暗示
- [ ] Middle layer (8-16) で活性化差分計算
- [ ] CCL 遵守 vector を保存 (.pt ファイル)

### Phase C: Steering 適用 (2h)

- [ ] llm_steer で vector 注入
- [ ] 複数 coefficient (0.5, 0.8, 1.0) テスト
- [ ] `/boot+`, `/zet+` 相当のプロンプトで出力生成

### Phase D: 評価 (2h)

- [ ] sel_validator で遵守率測定
- [ ] 出力品質の主観評価
- [ ] SEL のみ vs SEL + Steering 比較表作成

---

## 成功基準

| 指標 | 目標 |
|:-----|:-----|
| 遵守率向上 | +5% (90% → 95%) |
| 副作用 | 出力品質劣化なし |
| 実用性 | Production 検討可能な知見 |

---

## リスク

- GPU 環境がない → Google Colab Pro で代替
- モデルサイズ制約 → 7B モデルに限定
- Vector 効果なし → 調査知見として記録

---

*Created: 2026-02-01*
