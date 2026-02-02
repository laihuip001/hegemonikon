# Pythōsis 開発「備え」マトリックス

> **目的**: 大規模開発に必要な「備え」を Hegemonikón の定理群から洗い出す
> **CCL**: `/tak+*^/noe+`

---

## 1. 「備え」思考法の定理マッピング

### 1.1 リスク・失敗分析

| 思考法 | 定理/派生 | CCL | 説明 |
|:-------|:---------|:----|:-----|
| **Premortem (死亡前死因分析)** | O2 Boulēsis `akra` | `/bou.akra+` | 失敗を事前に想定 |
| **Five Whys** | `/why` | `/why+` | 根本原因の探求 |
| **Worst Case** | A2 Krisis `worst_case` | `/dia.worst_case` | 最悪シナリオ |
| **Counterfactual** | A2 Krisis `counterfactual` | `/dia.counterfactual` | 反事実的思考 |
| **Inversion** | A2 Krisis `inversion` | `/dia.inversion` | 逆から考える |
| **Devil's Advocate** | A2 Krisis `devil` | `/dia.devil` | 敵対的批判 |

### 1.2 成功分析

| 思考法 | 定理/派生 | CCL | 説明 |
|:-------|:---------|:----|:-----|
| **成功要因分析 (Futurespective)** | O2 Boulēsis `voli` | `/bou.voli+` | 統合的成功像 |
| **Backcast** | P2 Hodos `backcast` | `/hod.backcast` | 成功から逆算 |
| **Steelman** | A2 Krisis `steelman` | `/dia.steelman` | 最強の主張構築 |

### 1.3 アナロジー・外部知識

| 思考法 | 定理/派生 | CCL | 説明 |
|:-------|:---------|:----|:-----|
| **Analogy** | A3 Gnōmē `analogy` | `/gno.analogy` | 類推 |
| **Cross-domain Analogy** | A3 Gnōmē `analogy_cross` | `/gno.analogy_cross` | 異分野類推 |
| **History Analogy** | A3 Gnōmē `analogy_history` | `/gno.analogy_history` | 歴史からの類推 |
| **CS Analogy** | A3 Gnōmē `analogy_cs` | `/gno.analogy_cs` | CS からの類推 |
| **Reference Class** | A4 Epistēmē `reference_class` | `/epi.reference_class` | 参照クラス予測 |
| **Base Rate** | A4 Epistēmē `base_rate` | `/epi.base_rate` | 基準率無視防止 |

### 1.4 不確実性・確信度

| 思考法 | 定理/派生 | CCL | 説明 |
|:-------|:---------|:----|:-----|
| **Bayesian** | H2 Pistis `bayes` | `/pis.bayes` | ベイズ更新 |
| **Uncertainty** | H2 Pistis `uncertainty` | `/pis.uncertainty` | 不確実性評価 |
| **Calibration** | H2 Pistis `calibrate` | `/pis.calibrate` | 確信度校正 |
| **Sensitivity** | S3 Stathmos `sensitivity` | `/sta.sensitivity` | 感度分析 |

### 1.5 スコープ・境界

| 思考法 | 定理/派生 | CCL | 説明 |
|:-------|:---------|:----|:-----|
| **Scope** | P1 Khōra `scope` | `/kho.scope` | 範囲定義 |
| **Constraint** | P1 Khōra `constraint` | `/kho.constraint` | 制約明示 |
| **Edge** | P1 Khōra `edge` | `/kho.edge` | 境界条件 |
| **Module** | P1 Khōra `module` | `/kho.module` | モジュール分割 |

### 1.6 時間・タイミング

| 思考法 | 定理/派生 | CCL | 説明 |
|:-------|:---------|:----|:-----|
| **Short-term** | K-series `shor` | `/k.shor` | 短期視点 |
| **Medium-term** | K-series `medi` | `/k.medi` | 中期視点 |
| **Long-term** | K-series `long` | `/k.long` | 長期視点 |
| **Deadline** | K2 Chronos `dead` | `/chr.dead` | 締め切り意識 |
| **Stage** | K1 Eukairia `stage` | `/euk.stage` | 段階設計 |

---

## 2. マクロ一覧 (10個)

| マクロ | 用途 | 備え適用 |
|:-------|:-----|:---------|
| `@proof` | 存在証明 | 設計の必然性検証 |
| `@ground` | 接地 | 抽象→具体 |
| `@memoize` | キャッシュ | 計算コスト削減 |
| `@validate` | 検証 | 事前/事後チェック |
| `@scoped` | スコープ | 影響範囲限定 |
| `@chain` | 直列化 | 段階的実行 |
| `@cycle` | 反復 | 洗練サイクル |
| `@repeat` | N回 | 深化・検証強化 |
| `@reduce` | 累積 | 段階的統合 |
| `@partial` | 部分適用 | 文脈固定 |

---

## 3. Pythōsis 専用「備え」ワークフロー提案

### 3.1 `/pythosis.pre` — Premortem Protocol

```ccl
@chain(
  /bou.akra+,           # 失敗要因の想定
  /dia.worst_case,      # 最悪シナリオ
  /hod.backcast,        # 回避経路設計
  /sta.failsafe         # フェイルセーフ策定
)
```

### 3.2 `/pythosis.vet` — Success Vetting

```ccl
@chain(
  /bou.voli+,           # 成功像の明確化
  /gno.analogy_history, # 成功例からの学び
  /epi.reference_class, # 参照クラス予測
  /dia.steelman         # 最強の成功主張
)
```

### 3.3 `/pythosis.scope` — Scope Anchoring

```ccl
@chain(
  /kho.scope,           # 範囲定義
  /kho.constraint,      # 制約明示
  /kho.edge,            # 境界条件
  /sta.done             # 完了条件
)
```

---

## 4. 派生カタログ (全 200+ 派生)

### 分類別集計

| シリーズ | WF 数 | 派生総数 |
|:---------|------:|--------:|
| O-series | 4 | 12+ |
| S-series | 4 | 50+ |
| H-series | 4 | 20+ |
| P-series | 4 | 40+ |
| K-series | 4 | 20+ |
| A-series | 4 | 60+ |
| Hub/Other | 8 | (振動) |

---

## 5. 「備え」思考の CCL プログラム

```ccl
# Pythōsis 開発準備プログラム
@program pythosis_sonae

# Phase 1: リスク分析
/bou.akra+ _/dia.worst_case _/why+
# → 失敗要因・最悪シナリオ・根本原因

# Phase 2: 成功分析  
/bou.voli+ _/hod.backcast _/gno.analogy_cs
# → 成功像・逆算経路・CS アナロジー

# Phase 3: スコープ固定
/kho.scope _/kho.constraint _/sta.done
# → 範囲・制約・完了条件

# Phase 4: 不確実性評価
/pis.uncertainty _/pis.calibrate _/sta.sensitivity
# → 不確実性・校正・感度分析
```

---

*Pythōsis Foundation Catalog | `/tak+*^/noe+`*
