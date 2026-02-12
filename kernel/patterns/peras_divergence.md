# Peras 発散パターン — `~!` 演算子の実装仕様

> **帰属先**: CCL 演算子 `~!` (divergent oscillation) の内部アルゴリズム
> **元分類**: ccl/macros/diverge.md → 再帰属 (2026-02-12)
> **理由**: マクロではなく演算子の実装仕様であるため。公理から演繹されるべき

---

## 定義

```yaml
operator: ~! (divergent oscillation)
parameters:
  top_n: int (default: 3)
expansion: |
  # D1: スキャン — 6対の張力を評価
  F:[C(4,2)]{ E[tension(pair)] }
  _
  # D2: 深掘り — 上位N対を選択して交差分析
  let @topN = sort_by(tension, desc)[0:$top_n]
  F:[@topN]{
    /zet+{pair} _ /noe-{pair}
  }
  _
  # D3: 盲点レポート — 確信度付き
  @reduce(_){findings} _ /pis{blindspots} _ /dox.sens{blindspots}
```

---

## 処理フロー

```
D1: スキャン (Scan)
├─ C(4,2) = 6対を全走査
├─ 各対の「張力」を計算 (テンソル積座標の直交度)
└─ 張力スコア順にソート

D2: 深掘り (Probe)
├─ 上位N対のみ選択 (認知負荷の最適化, default=3)
├─ 各対に /zet+ で問いを深掘り
└─ /noe- で簡潔な認識を得る

D3: レポート (Report)
├─ 発見を統合
├─ /pis で確信度を付与
└─ /dox.sens で感覚的信念として記録
```

---

## 張力計算

> **tension(T_i, T_j)** = テンソル積座標間の直交度

| 座標パターン | 直交度 | 張力 |
|:-------------|:-------|:-----|
| 同軸 (I×E と I×P) | 低 | 低 — 共通軸あり |
| 半直交 (I×E と A×E) | 中 | 中 — 1軸共通、1軸異 |
| 完全直交 (I×E と A×P) | 高 | 高 — 接点なし、盲点が生まれやすい |

---

## 出力テーブル

| 項目 | 内容 |
|:-----|:-----|
| 最高張力対 | {T_i}⊗{T_j} (tension: {score}) |
| 盲点 | 1. {発見1} / 2. {発見2} / 3. {発見3} |
| 確信度 | {C/U} ({confidence}%) |
| 記録先 | /dox.sens → {path} |

---

## 借用元

| WF | 借用構造 | 適用先 |
|:---|:---------|:-------|
| `/zet` | PHASE 2 フィルタリング | D1 |
| `/noe` | PHASE 3 分析深化 | D2 |
| `/dox` | 永続化 (.sens) | D3 |
| `/sop` | 内部KB→外部の順序 | D1 |

---

## 複雑度

| マクロ | pt |
|:-------|:--:|
| `@diverge` | 5 |
| `@diverge{top_n=N}` | 6 |

*Hub WF Divergence Deepening v1.0*
