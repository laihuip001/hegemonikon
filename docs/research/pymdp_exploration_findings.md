# pymdp 探索知見レポート

> **日付**: 2026-01-28
> **目的**: pymdp と Hegemonikón の連動パターンを実験的に検証

---

## 1. 実験結果サマリー

### テキスト→政策選択の対応パターン

| 入力タイプ | 観測 | MAP 状態 | 推奨行動 |
|:-----------|:-----|:---------|:---------|
| `y` (承認) | ambiguous/low/high | uncertain/granted/passive | **observe 52%** |
| `緊急：バグ修正！` | ambiguous/high/medium | uncertain/withheld/active | **act 59%** |
| `どう思う？` | ambiguous/low/low | uncertain/withheld/passive | **observe 69%** |
| `fep_agent.py を確認` | clear/low/medium | clear/withheld/passive | **act 77%** |
| `いつでもいいから考えて` | ambiguous/low/medium | uncertain/withheld/passive | **observe 69%** |

---

## 2. 発見した法則

### 法則 1: 明確な文脈 → 行動を推奨

具体的なファイルパス、コードブロック、明示的な指示があると:

- `phantasia: clear` に収束
- act (O4 Energeia) の確率が上昇 (77%)

**解釈**: 十分な情報があれば、行動に移すべき

---

### 法則 2: 低確信 + 曖昧な文脈 → 観察を推奨

`どう思う？` のような問いかけ:

- `assent: withheld` (Epochē 状態)
- observe (O1 Noēsis 継続) の確率が上昇 (69%)

**解釈**: 情報不足/不確実な時は判断を保留し、さらなる観察を行うべき

---

### 法則 3: 高緊急度 → 行動バイアス

緊急マーカー (`緊急`, `今すぐ`, `!`) があると:

- `horme: active` (衝動活性化)
- act の確率が上昇 (59%)

**解釈**: 時間制約は行動を促進するが、文脈が曖昧なら慎重さが必要

---

### 法則 4: 高確信 + 曖昧文脈 → バランス

`y` (承認) の場合:

- `assent: granted` (同意付与)
- しかし `phantasia: uncertain` (文脈不明)
- observe/act がほぼ均衡 (52%/48%)

**解釈**: 確信があっても、何をすべきか不明なら追加情報を求めるべき

---

## 3. エントロピー分析

| シナリオ | エントロピー | 解釈 |
|:---------|:-------------|:-----|
| 意見要求 | 1.641 | 最も確定的 (Epochē 状態が支配的) |
| ユーザー承認 | 1.812 | 中程度 (assent は明確だが方向性は不明) |
| 緊急タスク | 1.846 | 中程度 (urgency は高いが何をすべきか不明) |
| 具体ファイル | 1.983 | やや高い (多くの状態が有力) |

**発見**: エントロピーだけでは判断材料として不十分。政策選択 (EFE) と組み合わせる必要がある。

---

## 4. 実用への示唆

### `/noe` への統合案

```python
# 思考開始前にエントロピーをチェック
if entropy > 1.9:
    print("⚠️ 多くの可能性を考慮中。PHASE 0.5 盲点チェックを強化")
```

### `/bou` への統合案

```python
# 政策選択に基づく行動推奨
if q_pi[0] > 0.6:  # observe probability > 60%
    print("🔍 追加情報収集を推奨。/noe または /why を実行")
elif q_pi[1] > 0.7:  # act probability > 70%
    print("✅ 行動準備完了。/ene で実行")
```

### Anti-Skip Protocol との連携

```python
# 文脈が ambiguous なのに act を選ぼうとしている場合
if phantasia == "uncertain" and q_pi[1] > q_pi[0]:
    print("⚠️ Anti-Skip: 行動前に文脈を明確化してください")
```

---

## 5. 今後の課題

| 課題 | 優先度 | 対応案 |
|:-----|:-------|:-------|
| 複数モダリティ同時処理 | 高 | pymdp 最新版への移行 |
| 連続観測での信念累積 | 中 | セッション内履歴保持 |
| A/B 行列の調整 | 低 | 実運用データで学習 |

---

*知見収集完了 — pymdp PoC v1.0*
