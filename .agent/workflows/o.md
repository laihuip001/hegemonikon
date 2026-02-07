---
description: O-series 4定理Limit。L1×L1 の極限演算で純粋認知の統合判断を生成。
hegemonikon: Ousia
modules: [O1, O2, O3, O4]
skill_ref:
  - ".agent/skills/ousia/o1-noesis/SKILL.md"
  - ".agent/skills/ousia/o2-boulesis/SKILL.md"
  - ".agent/skills/ousia/o3-zetesis/SKILL.md"
  - ".agent/skills/ousia/o4-energeia/SKILL.md"
version: "4.0"
lcm_state: stable
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

# /o: 純粋認知ワークフロー (Ousia)

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

1. **[O1 Noēsis]** I×E: 認識推論 — 何を認識すべきか
2. **[O2 Boulēsis]** I×P: 意志推論 — 何を望むか
3. **[O3 Zētēsis]** A×E: 探索行動 — 何を問うべきか
4. **[O4 Energeia]** A×P: 実用行動 — 何を実行するか

#### ⊕ C1: 対比 (Contrast)

4定理の出力を並列に並べ、**矛盾を検出**する。

| 定理 | 出力要点 (1行) |
|:-----|:---------------|
| O1 | {認識の結論} |
| O2 | {意志の結論} |
| O3 | {探求の結論} |
| O4 | {行動の結論} |

→ **V[outputs]** = 分散 (矛盾度: 0.0-1.0) を計算

#### ⊕ C2: 解消 (Resolve)

| V[outputs] | 状態 | 処理 |
|:-----------|:-----|:-----|
| > 0.3 | 高矛盾 | `/dia.root` で根源探索 → 重み付け融合 |
| > 0.1 | 微差 | 通常融合 (`@reduce(*)`) |
| ≤ 0.1 | 合意 | 単純集約 (`Σ`) |

#### ⊕ C3: 検証 (Verify)

| 項目 | 内容 |
|:-----|:-----|
| 矛盾度 | V[outputs] = {0.0-1.0} |
| 解消法 | {root/weighted/simple} |
| **統合判断** | {1文で} |
| **確信度** | {C/U} ({confidence}%) |

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
