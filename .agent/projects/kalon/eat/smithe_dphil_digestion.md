# /eat: Smithe DPhil 消化 — Bayesian Brain の圏論的基盤

> **消化元**: Toby St Clere Smithe, "Mathematical Foundations for a Compositional Account of the Bayesian Brain" (2022)
> **arXiv**: 2212.12538
> **消化日**: 2026-02-07
> **消化モード**: /eat (Hegemonikón に統合)

---

## 1. 論文の核心構造

### 統語側 (Syntactic Side)

| 概念 | 定義 | Hegemonikón 対応 |
|:-----|:-----|:---------------|
| **Bayesian lens** | (forward predictor, backward updater) のペア | `>>` の基盤 |
| **Copy-composition** | Bayesian lens の合成則 (新概念) | 射の合成 |
| **Statistical game** | 統計的推論問題のファイバー化 | Hub WF の定式化 |
| **Strict section** | relative entropy の鎖則 | 正確なベイズ推論 |
| **Lax section** | free energy 最小化 / MLE | **Hub WF = lax section** |

### 意味側 (Semantic Side)

| 概念 | 定義 | Hegemonikón 対応 |
|:-----|:-----|:---------------|
| **Open dynamical system** | ポリノミアル関手の coalgebra | 定理 = 開放力学系 |
| **Monoidal opindexed category** | 力学系の収集圏 | 24定理の圏 Cog |
| **Cilia** | lens を制御する力学系 | CCL の振動 `~` |
| **Predictive coding circuit** | cilia 上への関手 | XR pipeline |

---

## 2. Hegemonikón への統合ポイント

### 2.1 Bayesian Lens = `>>`

```
Bayesian lens:
  forward:  prior → prediction     (事前分布 → 予測)
  backward: prediction error → posterior update  (予測誤差 → 事後更新)

CCL >>:
  A >> B = A を B に構造的に変換
         = forward(A) → B, backward(error) → new_state
```

**統合**: `>>` は Bayesian lens の認知的略記。

### 2.2 Lax Section = Hub WF

```
Strict section:  KL(q || p) の鎖則を厳密に満たす
                → 正確なベイズ推論 (計算的に不可能)

Lax section:     free energy F ≥ KL を最小化
                → 変分推論 (計算可能な近似)

Hub WF /o:       4定理を融合して最適な1点に収束
                = lax section の実行
```

**統合**: Hub WF の Limit 解釈を「lax section」として再定義。「完璧な Limit に到達しないが、最善の近似を返す」。

### 2.3 Cilia = 振動 `~`

Smithe の Cilia: 「lens を制御する力学系」

```
Cilia = (dynamics, lens)
      = (状態遷移規則, 入出力チャネル)

振動 ~:
  /noe ~ /dia = O1 ↔ A2 を交互に実行
            = (O1_dynamics, O1→A2 lens) ∘ (A2_dynamics, A2→O1 lens) ∘ ...
            = cilia の合成
```

**統合**: `~` は cilia の交替合成。Smithe の言葉で言えば「交互に制御を交換する2つの bidirectional dynamical system」。

### 2.4 Enrichment Lens = `>*`

**Smithe の論文には存在しない。** これは CCL 固有。

先ほどの形式化から:

```
>* = Partial Bayesian Lens (部分的更新)
   = α-weighted lax section (学習率 α で制御)
```

Smithe の枠組みでは、lax section は「free energy の最小化」だが、`>*` は「free energy を **部分的に** 最小化」。

---

## 3. 消化品質評価 (/fit)

| 基準 | 評価 | 理由 |
|:-----|:-----|:-----|
| 構造保存 | ✅ | Bayesian lens → `>>`, lax section → Hub WF |
| 過剰適応なし | ✅ | `>*` が未対応であることを正直に認識 |
| 新規概念の獲得 | ✅ | cilia, copy-composition, strict/lax section |
| 実践的有用性 | ⚠️ | 概念の獲得に留まる。コード実装はまだ |
| Naturalized 度 | 🟡 | 語彙は取り込んだが、日常的に使うには練度が必要 |

---

## 4. Hegemonikón への提案

### 即時適用可能

| 対象 | 変更 | 優先度 |
|:-----|:-----|:------|
| `ccl/operators.md` | `>>` の説明に "Bayesian lens composition" を追記 | 🟡 |
| `ccl/operators.md` | `>*` の説明に "Enrichment lens" を追記 | 🟡 |
| Hub WF 各 `.md` | "lax section" の概念を注釈として追記 | 🟢 |
| `taxis.md` | Limit 行に "= lax section (Smithe 2022)" 追記 | 🟢 |

### 要精読

| 概念 | 理由 |
|:-----|:-----|
| Copy-composition | Bayesian lens の合成則の詳細が不明 |
| Monoidal opindexed category | 圏 Cog の正確な定式化に必要 |
| Polynomial functor coalgebra | 定理を力学系として定式化する具体的方法 |

---

*Smithe DPhil /eat 消化完了 — 2026-02-07*
