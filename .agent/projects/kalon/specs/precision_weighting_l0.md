---
title: "Precision Weighting (PW) — L0 概念定義"
version: "1.1"
created: "2026-02-08"
updated: "2026-02-08"
status: "APPROVED"
related:
  - .agent/projects/kalon/doxa/precision_weighting_gap.md
  - .agent/projects/kalon/specs/adjunction_resolution.md
  - .agent/workflows/o.md
tags: [precision-weighting, ccl, fep, natural-transformation]
---

## 背景

HGK は FEP の自然変換の一つ。FEP 推論サイクルの 4 ステップのうち、
Precision Weighting (PW) だけが動的操作として未実装だった。
PW を明示化し、自然変換 η の忠実性を回復する。

## 定義

### Precision Weighting とは

> **「今この瞬間、各定理/ステップの出力をどれくらい信頼するか」を動的に決定する操作**

| 概念 | 説明 |
|:-----|:-----|
| 設計時精度 (座標) | Precision 座標 (C↔U) が定める構造的精度 |
| **実行時精度 (PW)** | **文脈に応じた動的な信頼度重みづけ** |

### `+`/`-` と `pw:` の関係

Kalon (`adjunction_resolution.md`) で `+` は**自然変換 η: Id ⟹ T** と定義された。

```
+   = 自然変換 η  (全対象を均等に強化)
-   = 自然変換 ε  (全対象を均等に縮約)
pw: = パラメータ化された自然変換族 η_w  (対象ごとに異なる強度)
```

つまり: **`+` と `-` は `pw:` の省略形（均等 PW）。`pw:` は +/- の一般化。**

```
/o+          = /o{pw: [+1, +1, +1, +1]}   # 均等強化
/o-          = /o{pw: [-1, -1, -1, -1]}   # 均等縮約
/o{pw: O1+}  = /o{pw: [+1,  0,  0,  0]}   # 不均等 — O1 だけ強化
```

## CCL 構文

### Hub WF での使用

```ccl
# 省略形: 特定定理の +/- だけ指定 (残りは 0)
/o{pw: O1+, O3+, O4-}

# 明示形: 全定理の重みを指定
/o{pw: [O1=0.5, O2=0, O3=0.5, O4=-0.5]}
```

重み w ∈ [-1, +1]。0 = default。正 = 信頼強化。負 = 信頼低下。

### 個別 WF での使用

個別 WF にも `pw:` は自然変換として適用可能:

```ccl
# WF 内の各ステップに対する重みづけ
/noe{pw: 直観+, 分析-}
# → Noēsis 実行時に直観ステップを強化、分析ステップを抑制

# X-series 入力チャネルの重みづけ
/noe{pw: X-OS+, X-OH-}
# → Schema からの射を強化、Hormē からの射を抑制
```

これは Hub WF 内での定理重みづけと**同じ自然変換**が、
スケールを変えて（定理→ステップ、Series→X-series）適用されている。
**フラクタル構造の一例。**

## Hub WF 処理フローへの統合 (C0)

### C0: PW 決定 (新ステップ)

既存の C1-C3 の前に C0 を追加:

```
C0: PW 決定                    ← NEW
  → 各定理の実行時精度重みを決定
  ↓
C1: 射の列挙 (Contrast)
  → 4 定理を実行 (PW 重みを意識)
  ↓
C2: Cone 頂点探索 (Resolve)
  → PW 重みを使った加重融合
  ↓
C3: 普遍性検証 (Verify)
  → PW 重み込みの確信度
```

### C0 の具体的ロジック

#### Case 1: 明示的 PW (Creator 指定)

```ccl
/o{pw: O1+, O3+}
→ C0: pw = [O1=+1, O2=0, O3=+1, O4=0]
```

#### Case 2: 暗黙的 PW (文脈推定)

| 条件 | PW 推定 | 理由 |
|:-----|:--------|:-----|
| 直前が `/noe` | O1+ | 直前の定理の出力を活かす |
| V[] > 0.5 | O3+ (Zētēsis) | 不確実性高 → 探求を強化 |
| バイアス警告 | バイアス元- | `/ore.bias` の結果を反映 |
| 指定なし | 全0 (均等) | default = `+` と同等 |

#### Case 3: 自動 PW (将来 — L2)

```
Attractor Engine → Series 間 attract 度 → 定理レベルに分解 → PW 自動設定
```

## C2 (Cone 頂点探索) での PW 適用

```
# PW 重み込みの加重融合
統合出力 = Σ (定理_i の出力 × (1 + pw_i)) / Σ (1 + pw_i)

# 例: pw = [O1=+1, O2=0, O3=+1, O4=0]
# O1 と O3 の重みが 2倍 → 統合出力は O1・O3 寄りになる
```

C3 (確信度) にも PW 情報を記載:

```
| 項目 | 値 |
|:-----|:---|
| PW 設定 | O1=+1, O3=+1 |
| PW 根拠 | 直前が /noe → O1 強化; 探求文脈 → O3 強化 |
```

## 数学的位置づけ

### 座標 ⊣ 操作 (随伴)

```
Precision (座標/場)  ⊣  PW操作 (行為)
     C ↔ U              動的重みづけ
```

### 自然変換族

```
η_w: Id ⟹ T_w    (w = 重みベクトル)

η_{[1,1,1,1]} = +  (均等強化)
η_{[-1,-1,-1,-1]} = -  (均等縮約)
η_{[1,0,1,0]} = pw:[O1+,O3+]  (不均等)
```

### フラクタル構造

```
Layer 0: >> / >* 内の精度パラメータ (atomic PW)
Layer 1: 個別 WF 内のステップ重みづけ (theorem PW)
Layer 2: Hub WF の定理重みづけ (series PW)
Layer 3: Series 間の attract 度 (system PW) ← Attractor Engine
```

**PW 自体がフラクタル。同じ自然変換 η_w が各スケールで反復する。**

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 全てに pw+ | `+` と同義。不均等にする意味がない |
| 根拠なく pw- | `/ore.bias` の結果に基づくべき |
| PW を固定値にする | PW は文脈依存。毎回変わるべき |
| PW を過度に操作 | 操作しすぎは overfitting。default (均等) が基本 |

---

*L0 Precision Weighting 概念定義 v1.1 — Creator レビュー反映 — 2026-02-08*
