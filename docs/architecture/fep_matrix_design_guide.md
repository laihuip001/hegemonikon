# FEP Agent 行列設計ガイド

> **目的**: A/B/C/D 行列が「何をしているか」をレビュー可能にする
> **対象ファイル**: `mekhane/fep/fep_agent.py`

---

## 1. 全体像

### 状態空間（8 状態）

| # | Phantasia | Assent | Hormē | 解釈 |
|:--|:----------|:-------|:------|:-----|
| 0 | uncertain | withheld | passive | 不明確・保留・静止 |
| 1 | uncertain | withheld | active | 不明確・保留・衝動あり |
| 2 | uncertain | granted | passive | 不明確・同意・静止 |
| 3 | uncertain | granted | active | 不明確・同意・衝動あり |
| 4 | clear | withheld | passive | 明確・保留・静止 |
| 5 | clear | withheld | active | 明確・保留・衝動あり |
| 6 | clear | granted | passive | 明確・同意・静止 |
| 7 | clear | granted | active | **理想状態**: 明確・同意・行動準備 |

### 観測空間（8 観測）

| # | モダリティ | 値 | 意味 |
|:--|:-----------|:---|:-----|
| 0 | context | ambiguous | 文脈が曖昧 |
| 1 | context | clear | 文脈が明確 |
| 2 | urgency | low | 緊急性低 |
| 3 | urgency | medium | 緊急性中 |
| 4 | urgency | high | 緊急性高 |
| 5 | confidence | low | 確信低（Epochē トリガー） |
| 6 | confidence | medium | 確信中 |
| 7 | confidence | high | 確信高 |

---

## 2. A 行列: 観測尤度 P(o|s)

**「この隠れ状態のとき、どんな観測が得られやすいか」**

### 設計ルール

```
隠れ状態 → 観測
────────────────────────────
phantasia=clear   → context=clear (90%)
phantasia=uncertain → context=ambiguous (70%)
assent=granted    → confidence=high (70%)
assent=withheld   → confidence=low (50%)
horme=active      → urgency=high (60%)
horme=passive     → urgency=low (60%)
```

### 具体例

**状態 7 (clear, granted, active) のとき:**

- context=clear: 90%
- urgency=high: 60%
- confidence=high: 70%

→ 「明確で、緊急で、確信がある」観測が得られやすい

---

## 3. B 行列: 状態遷移 P(s'|s, a)

**「この状態でこの行動をすると、次にどの状態になりやすいか」**

### 行動定義

| # | 行動 | 対応 | 効果 |
|:--|:-----|:-----|:-----|
| 0 | observe | O1 Noēsis | 明確化、保留へ、静止へ |
| 1 | act | O4 Energeia | 同意へ、衝動活性化 |

### 設計ルール

**observe (行動 0):**

```
uncertain → clear: 60%（観察は明確化する）
granted → withheld: 30%（観察は Epochē を誘発）
active → passive: 70%（観察は落ち着かせる）
```

**act (行動 1):**

```
→ granted: 70%（行動は同意を意味する）
→ active: 80%（行動は衝動を活性化）
phantasia: ほぼ変化しない
```

---

## 4. C ベクトル: 選好

**「どんな観測が望ましいか」**

| 観測 | 選好値 | 理由 |
|:-----|:-------|:-----|
| context=clear | +2.0 | Zero Entropy 原則 |
| context=ambiguous | -2.0 | 曖昧さを避ける |
| urgency=high | +1.0 | 緊急なら対応すべき |
| confidence=high | +1.5 | 確信があるのは良い |
| confidence=low | -1.0 | Epochē トリガー |

---

## 5. D ベクトル: 初期信念

**「最初はどの状態を信じるか」**

```
初期状態の確率:
uncertain: 60%（認識謙虚）
clear: 40%

withheld: 60%（Epochē デフォルト）
granted: 40%

passive: 60%（慎重）
active: 40%
```

**最も確率が高い初期状態**: 状態 0 (uncertain, withheld, passive)

---

## 6. 計算例: 観測から信念更新

### 入力

```python
obs = encode_observation(clarity=0.8, urgency=0.3, confidence=0.9)
# → obs = 6
```

### 計算過程

1. **ベイズ更新**: `Q(s) ∝ A[obs, s] × D[s]`
2. **正規化**: `Q(s) = Q(s) / sum(Q)`
3. **Entropy 計算**: `H = -sum(Q × log(Q))`

### 結果

```python
result = agent.infer_states(observation=6)

# Q(s) = [0.05, 0.03, 0.08, 0.05, 0.12, 0.07, 0.35, 0.25]
#         ↑状態0                            ↑状態6=MAP

# MAP = 状態 6 (clear, granted, passive)
# Entropy = 1.67 (やや不確実)
```

---

## 7. レビューポイント

### 確認すべき質問

1. **A 行列の確率値は妥当か？**
   - 例: phantasia=clear で context=clear が 90% は高すぎ/低すぎ？

2. **B 行列の遷移確率は妥当か？**
   - 例: observe で granted→withheld が 30% は Epochē として妥当？

3. **C ベクトルの選好値は妥当か？**
   - 例: ambiguous が -2.0 は厳しすぎ/甘すぎ？

4. **D ベクトルの初期信念は妥当か？**
   - 例: 60% uncertain は認識謙虚として適切？

---

## 8. 数値の出所

| 数値 | 決め方 | 検証状態 |
|:-----|:-------|:---------|
| A 行列の確率 | Stoic 哲学からの直感 | ❌ 経験的検証なし |
| B 行列の遷移 | observe/act の意味論から | ❌ 経験的検証なし |
| C ベクトル | state_spaces.py の PREFERENCES | ✅ 定義済み |
| D ベクトル | 60:40 の謙虚バイアス | ❌ 根拠は薄い |

**正直な評価**: 多くの数値は「それらしい値」であり、経験的根拠はない。

---

*FEP Matrix Design Guide v1.0*
