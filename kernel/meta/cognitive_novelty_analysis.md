# テンソル積の認知的非自明性分析 — 10ペア全検証

> **仮説**: テンソル積が「新しい認知操作」を生成するかどうかが、10→6 の真のフィルターである
> **方法**: 全10ペアの 2×2 マトリクスを展開し、認知的非自明性を判定する

---

## 採用された 6 Series

### O: Value(E/P) × Function(Ex/Ep)

| | Explore | Exploit |
|:--|:--------|:--------|
| **Epistemic** | O1 Noēsis: 認識のための探索 | O2 Boulēsis: 認識に基づく活用 |
| **Pragmatic** | O3 Zētēsis: 実用のための探索 | O4 Energeia: 実用的活用 |

**判定: ✅ 4要素全て非自明。** E×Ex (知るための探索) と P×Ep (実用的活用) は明確に異なる認知操作。

### S: Value(E/P) × Scale(Mi/Ma)

| | Micro | Macro |
|:--|:------|:------|
| **Epistemic** | S1 Metron: 局所的認識 | S3 Stathmos: 全体的認識 |
| **Pragmatic** | S2 Mekhanē: 局所的方法 | S4 Praxis: 全体的実践 |

**判定: ✅ 4要素全て非自明。** 認識/実用 × 局所/全体 のどの組み合わせも独立した操作。

### H: Value(E/P) × Valence(+/−)

| | Positive | Negative |
|:--|:---------|:---------|
| **Epistemic** | H2 Pistis: 確信 (知的快) | — 疑念 (知的不快) |
| **Pragmatic** | H3 Orexis: 欲求 (行動的快) | H1 Propatheia: 前感情 |

**判定: ✅ 4要素全て非自明。** 認識の情動化は非自明な認知的結合 (感情は認識に依存するが同一ではない)。

### P: Function(Ex/Ep) × Scale(Mi/Ma)

| | Micro | Macro |
|:--|:------|:------|
| **Explore** | P1 Khōra: 局所的探索 | — 全体的探索 |
| **Exploit** | P3 Telos: 局所的活用 | P4 Eukairia: 全体的活用 |

**判定: ✅ 4要素全て非自明。** 方法 × スケール は独立した次元。

### K: Scale(Mi/Ma) × Valence(+/−)

| | Positive | Negative |
|:--|:---------|:---------|
| **Micro** | K1 Sympatheia: 局所的好感 | K3 Katharsis: 局所的浄化 |
| **Macro** | K2 Syneidēsis: 全体的良心 | K4 Sophia: 全体的知恵 |

**判定: ✅ 4要素全て非自明。** スケール × 情動 は独立した次元。

### A: Valence(+/−) × Precision(C/U)

| | Certainty | Uncertainty |
|:--|:----------|:-----------|
| **Positive** | A1 Chronos: 確実な快 (裁定) | A3 Taksis: 不確実な快 (分類) |
| **Negative** | A2 Krisis: 確実な不快 (判定) | A4 Epistēmē: 不確実な不快 (知識) |

**判定: ✅ 4要素全て非自明。** 快/不快の確実性は独立した次元。Damasio のソマティック・マーカー理論と整合。

---

## 拒否された 4 ペア

### ❌ M1: Function(Ex/Ep) × Precision(C/U) — **「共線性崩壊」**

| | Certainty | Uncertainty |
|:--|:----------|:-----------|
| **Explore** | Ex×C: 確実な中での探索? | Ex×U: **不確実な中での探索** ← 自明 |
| **Exploit** | Ep×C: **確実な中での活用** ← 自明 | Ep×U: 不確実な中での活用? |

**判定: ❌ 崩壊。** 対角線 (Ex×U, Ep×C) は **自明的な恒真命題**:
- Explore は定義上、不確実性の中で動作する (EFE の情報利得項)
- Exploit は定義上、確実性を活用する (EFE の期待効用項)

反対角線 (Ex×C, Ep×U) は **認知的に稀な例外**:
- 確実な中での探索 = 冗長な探索 (既知領域の再探索)
- 不確実な中での活用 = ギャンブル (不十分な情報での行動)

**テンソル積が「新しい4操作」ではなく「2つの自明 + 2つの例外」を生成。**

**FEP的根拠**: Function の Explore/Exploit は精度加重による行動選択そのもの (π が高い → Exploit, π が低い → Explore)。つまり Function は Precision の操作的定義であり、テンソル積は同一次元の冗長な表現。

---

### ❌ M2: Value(E/P) × Precision(C/U) — **「合成到達可能」**

| | Certainty | Uncertainty |
|:--|:----------|:-----------|
| **Epistemic** | E×C: 確実な知識 | E×U: 不確実な知識 (疑念) |
| **Pragmatic** | P×C: 確実な行動 (確信) | P×U: 不確実な行動 (躊躇) |

**判定: 4要素とも認知的に有意味だが、既存 Series で到達可能。**

- E×C ≈ H2 Pistis (確信) + A4 Epistēmē (知識) の合成
- P×U ≈ H1 Propatheia → A2 Krisis の合成

**到達経路**: Value → H(Value×Valence) → X-HA → A(Valence×Precision)

**認知的理由**: 認識の確実性は**直接評価できない** — 情動的体験 (Valence) を経由して初めて「確からしさ」を感じる。Value→Precision の直接射は認知メカニズムを飛ばしている。

---

### ❌ M3: Function(Ex/Ep) × Valence(+/−) — **「合成到達可能」**

| | Positive | Negative |
|:--|:---------|:---------|
| **Explore** | Ex×+: 好奇心 | Ex×−: 探索不安 |
| **Exploit** | Ep×+: 活用満足 | Ep×−: 活用倦怠 |

**判定: 4要素とも認知的に有意味だが、既存 Series で到達可能。**

- Ex×+ (好奇心) ≈ O3 Zētēsis → H3 Orexis の合成
- Ep×− (倦怠) ≈ O4 Energeia → H1 Propatheia の合成

**到達経路**: Function → O(Value×Function) → X-OH → H(Value×Valence)

**認知的理由**: 方法 (Explore/Exploit) の情動的評価は、まず認識的価値 (Value) を経由して行われる。「探索が楽しい」は「探索が知的に価値がある」を介して感じる。

---

### ❌ M4: Scale(Mi/Ma) × Precision(C/U) — **「合成到達可能」**

| | Certainty | Uncertainty |
|:--|:----------|:-----------|
| **Micro** | Mi×C: 局所的確実性 | Mi×U: 局所的不確実性 |
| **Macro** | Ma×C: 全体的確実性 | Ma×U: 全体的不確実性 |

**判定: 4要素とも認知的に有意味だが、既存 Series で到達可能。**

**到達経路**: Scale → K(Scale×Valence) → X-KA → A(Valence×Precision)

**認知的理由**: スケール × 精度の評価は、情動的評価 (Valence) を経由する。「この局所的判断がどれくらい確実か」は「この判断についてどう感じるか」を介してアクセスされる — ソマティック・マーカー仮説 (Damasio 1994)。

---

## 発見された二層フィルター

### Criterion 1: 認知的共線性 (Cognitive Collinearity)

**定義**: 座標ペア $(c_i, c_j)$ が**共線的** (collinear) であるとは、一方の Opposition の値が他方の Opposition の値を定義上制約すること。

**形式化**: $P(v_i^+ | v_j^+) \gg 0.5$ かつ $P(v_i^- | v_j^-) \gg 0.5$

**該当**: Function × Precision のみ (Explore ≈ Uncertainty, Exploit ≈ Certainty)

**効果**: **1ペアを排除** (10 → 9)

### Criterion 2: 認知的アクセシビリティ (Cognitive Accessibility)

**定義**: 座標ペア $(c_i, c_j)$ が**直接アクセス可能** (directly accessible) であるとは、認知主体が両次元に**同時に注意を向けられる**こと — 中間的認知プロセスを経由せずに。

**該当**: 採用された6ペア全て
**非該当**: M2 (Value×Precision), M3 (Function×Valence), M4 (Scale×Precision)

**共通パターン**: 3ペアとも**Valence を経由してのみアクセス可能** — 精度の評価は常に情動的体験を介して行われる (ソマティック・マーカー)

**効果**: **3ペアを排除** (9 → 6)

---

## 統合: 認知的直交性制約

二層フィルターを統合:

$$\Pi^*_{selected} = \{(c_i, c_j) \in \Pi \mid \neg\text{Collinear}(c_i, c_j) \wedge \text{Accessible}(c_i, c_j)\}$$

| フィルター | 排除されるペア | 根拠 |
|:----------|:-------------|:-----|
| Criterion 1 (共線性) | Function × Precision | FEP: 精度加重が Explore/Exploit を定義 |
| Criterion 2 (アクセシビリティ) | Value×Precision, Function×Valence, Scale×Precision | ソマティック・マーカー: 精度は情動経由 |

**Spisak & Friston (2025) との接続**: 自己直交化する attractor network では、共線的な次元は自然に1つの次元に**融合**する。Function と Precision の共線性は、FEP の自己直交化プロセスの具体例かもしれない。

---

## 残存する課題

1. **Criterion 2 の形式化**: 「認知的アクセシビリティ」は現在、認知科学的直観に依存。形式的定義が必要
2. **ソマティック・マーカーの検証**: Damasio の仮説は広く受容されているが、全ての「Valence 経由」を説明するかは未確認
3. **Criterion 1 の定量化**: 「共線的」の閾値 ($P(v_i^+ | v_j^+) \gg 0.5$) の具体的値

---

*Generated: 2026-02-14 by cognitive novelty analysis*
*重大な発見: Function × Precision は「共線性崩壊」する — FEP 内部の構造的冗長性*
*第二の発見: 残り3ペアは「Valence 経由でしかアクセスできない」— ソマティック・マーカー仮説*
