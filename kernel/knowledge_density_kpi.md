# Knowledge Density KPI — 知識密度指標

> **定義**: 知識密度 = 蓄積量 × 消化深度 × アクセス効率
> **目的**: 「蓄積 ≠ 密度」 — 量ではなく質を計測する

---

## 3軸 KPI

### 軸 1: 蓄積量 (Volume)

| 指標 | 計測方法 | 現在値 |
|:-----|:---------|:-------|
| Gnōsis 論文数 | `cli.py search --count` | ~100+ |
| Digestor 日次取得 | scheduler.log | 14/day |
| KI (Knowledge Item) 数 | knowledge/ count | 15 |

### 軸 2: 消化深度 (Depth)

| レベル | 意味 | 判定方法 |
|:-------|:-----|:---------|
| L0 索引 | ベクトル化のみ | gnosis-index で自動 |
| L1 要約 | digest_report に要約あり | Digestor 出力 |
| L2 統合 | 既存 KI と統合済み | /eat 実行済み |
| L3 発見 | 新しい知見を既存体系に結合 | /noe, /fit で検証 |

**KPI**: 平均消化深度 = Σ(level × count) / total

### 軸 3: アクセス効率 (Accessibility)

| 指標 | 計測方法 |
|:-----|:---------|
| 検索ヒット率 | query → top-3 に正解がある率 |
| /boot 表示率 | boot 時に Digestor 候補が表示される率 |
| PKS プッシュ率 | 能動的に知識が提示される率 |

---

## 統合スコア

```
Knowledge Density = V × D × A
  V = min(volume / 200, 1.0)           # 200論文で飽和
  D = avg_depth / 3.0                   # L3 で最大
  A = (hit_rate + boot_rate + pks_rate) / 3.0
```

**目標**: KD ≥ 0.5 (現在: 推定 ~0.15)

---

*Created: 2026-02-08 | Source: /dia+~*/noe Action 2*
