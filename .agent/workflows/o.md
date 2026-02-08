---
description: O-series Peras。L1×L1 の極限演算で純粋認知の統合判断を生成。
hegemonikon: Ousia
modules: [O1, O2, O3, O4]
skill_ref:
  - ".agent/skills/ousia/o1-noesis/SKILL.md"
  - ".agent/skills/ousia/o2-boulesis/SKILL.md"
  - ".agent/skills/ousia/o3-zetesis/SKILL.md"
  - ".agent/skills/ousia/o4-energeia/SKILL.md"
version: "5.0"
lcm_state: stable
category_theory:
  yoneda: "Hom(-, Tn) ≅ F(Tn) — 各定理はその射の集合で完全に決まる"
  limit: "Cone の頂点 — 全ての射が一致する点"
  converge_as_cone: "C1=射の列挙, C2=Coneの中介射, C3=普遍性検証"
  cone_builder: "mekhane/fep/cone_builder.py"
layer: "Δ"
lineage: "v3.2 + Limit演算復元 → v4.0"
derivatives:
  O1: [nous, phro, meta]
  O2: [desir, voli, akra]
  O3: [anom, hypo, eval]
  O4: [flow, prax, pois]
cognitive_algebra:
  generation: "L1 × L1"
  coordinates:
    axis_1: "Flow (I/A)"
    axis_2: "Value (E/P)"
  definition: "/o = lim(O1·O2·O3·O4)"
  interpretation:
    strict: "テンソル積 (Flow⊗Value) の Limit 射影"
    short: "4定理の内積 → 最適収束点"
  operators:
    "+": "Limit強度↑ — 全4定理を詳細に収束"
    "-": "Limit強度↓ — 縮約収束"
    "*": "Limit対象自体を問う: なぜ純粋認知層か"
sel_enforcement:
  "+":
    description: "MUST execute ALL 4 theorems with deep convergence"
    minimum_requirements:
      - "全4定理実行"
      - "各定理詳細モード"
      - "融合ステップ必須"
  "-":
    description: "MAY execute with condensed convergence"
    minimum_requirements:
      - "サマリーのみ"
  "*":
    description: "MUST meta-analyze: why use pure cognition layer?"
    minimum_requirements:
      - "認知層選択の理由を問う"
ccl_signature: "/o+*dia"
anti_skip: enabled
---

# /o: 純粋認知 Peras (Ousia)

> **Hegemonikón Layer**: Ousia (O-series)
> **定義**: `/o` = `lim(O1·O2·O3·O4)` — L1×L1 の極限演算
> **目的**: 認識・意志・探求・行為の4定理を**1つの統合判断に収束**させる
>
> **制約**: 全4定理 → 融合(Convergence)。途中の省略は`-`モード実行時のみ許容。

---

## Limit / Colimit

| 演算 | 記号 | 圏論 | 意味 |
|:-----|:-----|:-----|:-----|
| `/o` | `/` | **Limit** | 4定理 → 最適な1収束点 |
| `\o` | `\` | **Colimit** | 4定理 → 全組み合わせに展開 |
| `/o+` | `+` | Limit強度↑ | より深い収束（詳細モード） |
| `/o-` | `-` | Limit強度↓ | 軽い収束（縮約モード） |

### 米田の補題 (Yoneda)

> **各定理 T は Hom(-, T) で完全に決まる**: 定理への全ての射（X-series）が、その定理の「意味」そのもの。
> Limit 演算 `/o` は、この Yoneda embedding の計算に相当する。
> 4定理の出力を収束させる = 全ての射が一致する Cone の頂点を見つけること。

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/o` | O-series Limit（4定理 → 収束） |
| `/o~k` | O-series ↔ K-series 間を振動 |
| `/o+` | Limit強度↑: 全4定理を詳細に収束 |
| `/o-` | Limit強度↓: 縮約収束 |
| `/o*` | 「なぜO-seriesを使うか」を問う |
| `\o` | O-series Colimit（全展開） |

---

## 処理フロー

### `/o` (Limit — 収束) `@converge`

> **米田の補題による解釈**: 各定理 Tn は Hom(-, Tn) で完全に決まる。
> Limit = 「全ての定理の出力が整合する唯一の点」= Cone の頂点。
> @converge はこの Cone を構築し、頂点を見つける操作。

#### ⊕ C0: Precision Weighting (PW) — 実行時精度の決定

> **FEP**: Precision Weighting = 各情報チャネルの信頼度を動的に決定する操作。
> `+`/`-` は均等 PW（全定理に同じ重み）。`pw:` は不均等 PW（定理ごとに異なる重み）。
> **`+` と `-` は `pw:` の省略形。`pw:` は +/- の一般化。**

**明示指定** (Creator が `pw:` を指定した場合):

```ccl
/o{pw: O1+, O3+}  → pw = [O1=+1, O2=0, O3=+1, O4=0]
```

**暗黙推定** (指定がない場合):

| 条件 | PW 推定 | 理由 |
|:-----|:--------|:-----|
| 直前が `/noe` | O1+ | 直前の定理の出力を活かす |
| V[] > 0.5 | O3+ (Zētēsis) | 不確実性高 → 探求強化 |
| バイアス警告あり | バイアス元- | `/ore.bias` 結果を反映 |
| 指定なし + 条件なし | 全0 (均等) | default |

→ **pw[O1..O4]** = 各定理の実行時精度重み [-1, +1]

---

**Cone 自動構築** (C1 の射の対比完了後に実行):

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.cone_builder import converge, describe_cone
from mekhane.fep.category import Series
cone = converge(Series.O, {'O1': '<O1出力>', 'O2': '<O2出力>', 'O3': '<O3出力>', 'O4': '<O4出力>'})
print(describe_cone(cone))
"
```

**射の列挙** (各定理の Yoneda 表現を計算):

1. **[O1 Noēsis]** I×E: Hom(-, O1) = 認識の射 — 何を認識すべきか
2. **[O2 Boulēsis]** I×P: Hom(-, O2) = 意志の射 — 何を望むか
3. **[O3 Zētēsis]** A×E: Hom(-, O3) = 探求の射 — 何を問うべきか
4. **[O4 Energeia]** A×P: Hom(-, O4) = 行動の射 — 何を実行するか

#### ⊕ C1: 射の対比 (Contrast) — Cone の射後を検査

> **圏論**: 4つの射 (Hom(X, O1), Hom(X, O2), Hom(X, O3), Hom(X, O4)) を並列に並べ、
> 「全ての射が整合するか」を検査する。整合しない = Cone が存在しない。

| 定理 | Hom(X, Tn) | pw | 出力要点 (1行) |
|:-----|:-----------|:--:|:---------------|
| O1 | 認識の射 | {pw₁} | {認識の結論} |
| O2 | 意志の射 | {pw₂} | {意志の結論} |
| O3 | 探求の射 | {pw₃} | {探求の結論} |
| O4 | 行動の射 | {pw₄} | {行動の結論} |

→ **V[outputs]** = 射の散布度 (矛盾度: 0.0-1.0)
　V = 0 なら全射が一致 = Cone が自明に存在
　V > 0 なら射が不整合 = Cone の頂点を探索する必要がある

#### ⊕ C2: Cone の頂点探索 (Resolve) — PW 加重融合

> **圏論**: V[outputs] + PW 重み に応じて、加重融合で中介射を構築する。
> 統合出力 = Σ(定理_i × (1 + pw_i)) / Σ(1 + pw_i)

| V[outputs] | Cone 状態 | 中介射の構築法 |
|:-----------|:---------|:-------------------|
| > 0.3 | 射の不整合が大きい | `/dia.root` + **PW 加重融合** |
| > 0.1 | 幾何学的ズレ | **PW 加重融合** (`@reduce(*, pw)`) |
| ≤ 0.1 | 射がほぼ一致 | PW ≠ 0 なら加重集約、= 0 なら `Σ` |

#### ⊕ C3: 普遍性検証 (Verify) — Cone の普遍性

> **圏論**: Limit = **普遍的な** Cone。つまり、他のどんな Cone もこの Limit を経由して分解できる。
> 実践的には「この統合判断が唯一の自然な収束点か？」を検証する。

| 項目 | 圏論的意味 | 内容 |
|:-----|:-------------|:-----|
| 矛盾度 | 射の散布 | V[outputs] = {0.0-1.0} |
| 解消法 | 中介射の構築法 | {root/weighted/simple} |
| **統合判断** | **Cone の頂点** | {1文で} |
| **確信度** | **普遍性の強さ** | {C/U} ({confidence}%) |

---

### `\o` (Colimit — 展開) `@diverge`

#### ⊗ D1: スキャン (Scan) — 6対の張力評価

| # | 対 | 交差 | 問い | 張力 |
|:-:|:---|:-----|:-----|:----:|
| 1 | O1⊗O2 | (I×E)⊗(I×P) | 認識が意志をどう形成するか | 低(同軸I) |
| 2 | O1⊗O3 | (I×E)⊗(A×E) | 認識が探求をどう駆動するか | 中(半直交) |
| 3 | O1⊗O4 | (I×E)⊗(A×P) | 認識が行動をどう規定するか | **高(完全直交)** |
| 4 | O2⊗O3 | (I×P)⊗(A×E) | 意志が探求をどう方向づけるか | **高(完全直交)** |
| 5 | O2⊗O4 | (I×P)⊗(A×P) | 意志が行動をどう具現化するか | 中(半直交) |
| 6 | O3⊗O4 | (A×E)⊗(A×P) | 探求が行動をどう導くか | 低(同軸A) |

#### ⊗ D2: 深掘り (Probe) — 上位3対

高張力対 (#3, #4, #2 or #5) に `/zet+` → `/noe-` を適用:

- **O1⊗O4**: 認識(I×E)と行動(A×P)の完全直交 → 最大の盲点
- **O2⊗O3**: 意志(I×P)と探求(A×E)の完全直交 → 目的と手段の乖離

#### ⊗ D3: 盲点レポート

| 項目 | 内容 |
|:-----|:-----|
| 最高張力対 | {pair} (tension: {score}) |
| 盲点 | 1. {発見1} / 2. {発見2} / 3. {発見3} |
| 確信度 | {C/U} ({confidence}%) |
| 記録先 | `/dox.sens` → {path} |

### 個別定理への直接アクセス

| コマンド | 定理 | 生成 |
|:---------|:-----|:-----|
| `/noe` | O1 Noēsis 単体 | I × E |
| `/bou` | O2 Boulēsis 単体 | I × P |
| `/zet` | O3 Zētēsis 単体 | A × E |
| `/ene` | O4 Energeia 単体 | A × P |

---

## 派生マトリックス

| 定理 | 派生1 | 派生2 | 派生3 |
|:-----|:------|:------|:------|
| **O1 Noēsis** | `nous` 本質直観 | `phro` 実践判断 | `meta` メタ認識 |
| **O2 Boulēsis** | `desir` 第一次欲動 | `voli` 第二次意志 | `akra` 意志乖離 |
| **O3 Zētēsis** | `anom` 異常認識 | `hypo` 仮説生成 | `eval` 仮説評価 |
| **O4 Energeia** | `flow` Flow状態 | `prax` 自己目的行為 | `pois` 産出活動 |

**合計**: 12派生

### 派生選択ロジック

```python
from mekhane.fep.derivative_selector import select_derivative

result = select_derivative("O1", problem_context)
# → nous: 抽象原理 → phro: 実践判断 → meta: メタ認知
```

---

## 各定理の概要

### O1 Noēsis（Νόησις / 認識） — I × E

**問い**: 「何を認識すべきか？」「本質は何か？」
**生成**: 推論(I) × 認識(E) = 知識獲得のための思考

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **nous** | 抽象的問題、原理探求 | Nous poietikos | 専門家直観 (System 1) |
| **phro** | 具体的状況、実践的判断 | Phronēsis | エキスパート判断・EI |
| **meta** | 反省が必要、信頼度疑問 | 自己参照的Nous | メタ認知 (pMFC/aPFC) |

→ 詳細: `/noe` または `.agent/skills/ousia/o1-noesis/SKILL.md`

### O2 Boulēsis（Βούλησις / 意志） — I × P

**問い**: 「何を望むか？」「どの欲動を有効にするか？」
**生成**: 推論(I) × 実用(P) = 目標設定のための思考

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **desir** | 明確な望み、欲動表出 | Boulēsis基層 | Implicit wants |
| **voli** | 葛藤解決、意志統合 | Frankfurt階層意志 | Executive function |
| **akra** | 意志-行為乖離 | Akrasia理論 | Implementation intention |

→ 詳細: `/bou` または `.agent/skills/ousia/o2-boulesis/SKILL.md`

### O3 Zētēsis（Ζήτησις / 探求） — A × E

**問い**: 「何を問うべきか？」「どの仮説を追求するか？」
**生成**: 行為(A) × 認識(E) = 知識を得るための行動

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **anom** | 異常・驚き、問題化 | Diaporesis | Curiosity gap |
| **hypo** | 仮説が必要、創造的推測 | Peirce Abduction Ph.1 | Generative reasoning |
| **eval** | 複数候補、評価・選別 | Peirce Abduction Ph.2 | IBE, pursuitworthiness |

→ 詳細: `/zet` または `.agent/skills/ousia/o3-zetesis/SKILL.md`

### O4 Energeia（Ἐνέργεια / 活動） — A × P

**問い**: 「どう活動するか？」「何を実現するか？」
**生成**: 行為(A) × 実用(P) = 目的達成のための行動

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **flow** | 没入・最適経験 | Energeia自己目的性 | Csikszentmihalyi Flow |
| **prax** | 行為自体が目的 | Praxis | Intrinsic motivation |
| **pois** | 外部成果物産出 | Poiesis | Craftsmanship |

→ 詳細: `/ene` または `.agent/skills/ousia/o4-energeia/SKILL.md`

---

## X-series 連携

| 現在 | 推奨先 | 理由 |
|:-----|:-------|:-----|
| O1 Noēsis | S1 Metron | 認識後にスケール決定 |
| O2 Boulēsis | S2 Mekhanē | 意志後に方法配置 |
| O3 Zētēsis | K4 Sophia | 問い発見後に外部調査 |
| O4 Energeia | H4 Doxa | 活動後に記録・永続化 |

---

## Hegemonikon Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| O1-O4 | /o | v4.0 Ready |

---

*v4.0 — Limit演算復元 (2026-02-07)*
*v4.1 — 米田の補題統合 (2026-02-08)*
*v5.0 — 米田深層統合。@converge C1-C3 を Cone 構築として再定義。C1=射の列挙, C2=中介射構築, C3=普遍性検証 (2026-02-08)*
