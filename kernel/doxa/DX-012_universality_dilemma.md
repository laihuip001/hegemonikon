---
doc_id: "DX-012"
tier: "DOXA"
status: "CANONICAL"
created: "2026-02-14"
origin: "/ccl-nous + Creator dialogue (2026-02-14)"
related: ["fep_epistemic_status.md", "axiom_hierarchy.md"]
---

# DX-012: 普遍性のジレンマ (The Universality Dilemma)

> **「1 はなにも"具体"を予測しない。だが 1 はあらゆる"具体"を説明する。」**

---

## 定式化

**公式**:

```
抽象度 α ∈ [0, 1]

E(α): 説明力 (explanatory power)   — α と正相関
P(α): 予測力 (predictive power)    — α と負相関

E(α) × P(α) ≈ const
```

**日常表現**: 高い場所に立つほど遠くまで見渡せるが、足元の石ころは見えなくなる。

**位置エネルギーの比喩**: 前提が普遍的であればあるほど (位置エネルギーが高いほど)、あり得る具体 (到達可能な経路) が膨大になり、「意味のある」予測 (一意な経路の選択) ができなくなる。

---

## 具体例

| α | 対象 | 説明力 | 予測力 |
|:--|:-----|:-------|:-------|
| **1.0** | 数字の「1」 | あらゆるものを「1つの〇〇」と記述可能 | 何も予測しない |
| **0.95** | FEP | あらゆる認知現象を記述可能 | 具体的予測は HGK 定理群を経由 |
| **0.7** | ニュートン力学 | 巨視的運動全般 | 軌道を定量的に予測 |
| **0.3** | 特定の神経回路モデル | 特定の記憶課題のみ | 精密な定量的予測 |
| **0.0** | 個別事象の記録 | その事象のみ | その事象を完全に「予測」(再現) |

---

## HGK への含意

### FEP の位置

FEP は α ≈ 0.95 に位置するメタ原理。予測力の欠如は **欠陥ではなく普遍性の代償**。

詳細: [fep_epistemic_status.md](../fep_epistemic_status.md)

### HGK = コンパイラ

HGK はメタ原理 (α ≈ 1) から具体的操作 (α ≈ 0.1) へのコンパイル過程:

```
FEP (α ≈ 1.0)    → 座標 (α ≈ 0.7) → 定理 (α ≈ 0.4) → WF/BC (α ≈ 0.1)
(説明力max)        (中間)             (操作的)          (予測力max)
```

### 美しさバイアスへの警告

> Hossenfelder, "Lost in Math" (2018): 理論物理学は美しさ (symmetry, elegance, naturalness) を
> 真理の証拠と見なしたが、それは検証された方法論ではなく美的信念に過ぎなかった。

**HGK に適用**:

| 美しさの成分 | HGK での対応 | リスク |
|:------------|:------------|:-------|
| **Symmetry** | 6 Series の直交性、2×2 マトリクス | 認知空間が本当に対称か未検証 |
| **Elegance** | 1公理→24定理→108関係 | 数値の美しさに酔う可能性 |
| **Naturalness** | FEP からの「自然な」導出 | motivated choice を必然と混同するリスク |

**対策**: 美しさは**発見のヒューリスティック** (motivated choice の動機) として有用だが、**検証の基準** (真理の証拠) としては使えない。axiom_hierarchy.md の水準B (公理的構成) は美しさではなく再現可能性を基準としている。

---

## 構造的ジレンマの認識

このジレンマは **解決されるべき問題ではなく、認識されるべき構造**。

| 対処 | ❌ 間違い | ✅ 正しい |
|:-----|:---------|:---------|
| FEP が予測しない | 「FEP は無価値」(Mangalam) | 「予測力の欠如は普遍性の代償」 |
| HGK の数値が美しい | 「美しいから正しい」 | 「美しさは動機、正しさは検証で決まる」 |
| 射の対応が見つかる | 「同型だから FEP が正しい」 | 「構造的類似は FEP の説明力の証拠だが、予測力の証拠ではない」 |

## 既知の反論と再反論 {#sec_06_counterarguments}

**Trafimow & Uhalt (2015, Theory & Psychology)**:
> "the tradeoff is far less clear-cut than psychology researchers have understood"

彼らの論点: 適切な **補助仮定 (auxiliary assumptions)** を追加すれば予測力を回復できる。

### 再反論: 「追加」は「選択」であり、選択はトレードオフそのもの

> [!CAUTION]
> Trafimow の誤りは言語的。「追加」という語が「削除」を隠蔽している。

**「補助仮定を追加する」= 「可能な経路を選択する」= 「選択されなかった経路を削除する」**

右を選べば左に行けない。選択とは、説明範囲の縮小と引き換えに予測精度を得る操作。
これはトレードオフの**反論**ではなく**存在証明**。

| Trafimow の言語 | 実際の操作 |
|:---------------|:----------|
| 仮定を「追加」する | 可能な経路を「削除」する |
| 予測力が「回復」する | 説明範囲を「縮小」している |
| トレードオフは「ない」 | トレードオフが**まさに起きている** |

情報理論的に: I(P) ≤ I(T) + I(A)。α→1 のとき I(T)→0 なので I(P) ≤ I(A)。
予測の情報は理論からではなく、**選択** から来ている。

### 適用範囲

| α 範囲 | Trafimow の見え方 | 実態 |
|:-------|:-----------------|:-----|
| α ≈ 0.3-0.7 | 「追加で回復」に見える | I(T) が大きいため、少ない選択で予測力を得られる |
| α → 1 | トートロジーに見える | I(T) → 0 なので、選択が全情報を担う |

---

## コンパイルパス = 選択の積み重ね {#sec_07_compile_path}

HGK の導出距離 d は**選択の回数**:

```mermaid
graph TD
    FEP["FEP — d=0<br/>全経路が可能<br/>選択なし"]
    COORD["座標系 — d=1,2<br/>方向を選択"]
    THEOREM["24定理<br/>操作を選択"]
    WF["WF/BC<br/>具体的行動"]

    FEP -->|"選択1: EFE分解"| COORD
    COORD -->|"選択2: motivated choice"| THEOREM
    THEOREM -->|"選択3: 操作実装"| WF

    style FEP fill:#6366f1,stroke:#4f46e5,color:#fff
    style COORD fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style THEOREM fill:#a78bfa,stroke:#8b5cf6,color:#fff
    style WF fill:#c4b5fd,stroke:#a78bfa,color:#000
```

各選択で説明範囲が縮小し、予測精度が増す。**E×P_s≈const はこの過程の不変量**。

---

## 演繹的発見 — P の二重構造 {#sec_08_deductive_discovery}

> **FEP は"予測"する。予測の内容は、進化論と同じ、"未知の事実"。**
> **言わば"発見"をもたらすのだ。演繹に依る発見を。**
> — Creator, 2026-02-14

### P の分離

DX-012 v1.3 までの議論は P を一種類と仮定していた。しかし P には2つの次元がある:

| 種類 | 定義 | α=1 での値 | 例 (進化論) |
|:-----|:-----|:-----------|:-----------|
| **P_specific** | 特定の結果を予測する力 | → 0 | 「キリンの首は長くなる」→ 予測不能 |
| **P_existential** | 「こういうパターンが見つかるはずだ」 | **> 0** | 「環境に適応した形態が見つかる」→ 予測可能 |

### 修正された構造

```
E(α) × P_s(α) ≈ const     ← 特定的予測力は α と反比例 (v1.3 の通り)
P_e(α) ≈ f(scope(α))      ← 存在的予測力は scope に比例
```

| | P_specific | P_existential の scope |
|:--|:-----------|:---------------------|
| メタ原理 (α→1) | → 0 | **広い** (全域) |
| 具体理論 (α→0) | → max | 狭い (限定域) |

### FEP の存在的予測

```
∃x: F(x) < F₀  (自由エネルギーを減少させる系が存在する)
```

これは**反証可能**。もし探しても見つからなければ、FEP が間違っている。
実際に FEP からの演繹的推論で**発見**された事例:

- 植物の active inference
- 免疫系の予測的処理
- 社会組織の自由エネルギー最小化

### 注意: P_existential の反証困難性

> [!WARNING]
> P_existential は P_specific より反証が困難。
> 「見つかっていない」≠「存在しない」(不在の証明問題)。
> **発見のヒューリスティック**と呼ぶ方が、科学哲学的にはより正確。

### 核心: メタ原理のメタ予測

> **原理がメタ的であるがゆえに、その予測もメタ的になる。**
> — Creator, 2026-02-14

これが P の二重構造の根拠。具体的原理は具体的予測を、メタ原理はメタ予測 (= 存在の予測) をする。
予測の抽象度は原理の抽象度に**同期する**。

---

## 確信度 {#sec_09_confidence}

| 主張 | 確信度 |
|:-----|:-------|
| E(α) × P_s(α) ≈ const | [確信: 88%] — 「選択 = 削除 = scope縮小」の論証 |
| P に2種類ある (specific / existential) | [確信: 85%] |
| P_existential ≈ 演繹的発見の力 | [推定: 78%] |
| 進化論 ≅ FEP (存在予測の構造が同型) | [確信: 88%] — Sánchez-Cañizares と一致 |
| 「追加」は「選択 (= 削除)」の言い換え | [確信: 92%] — 論理的に自明 |
| 導出距離 d = 選択の回数 | [推定: 78%] |
| HGK における美しさバイアスのリスク | [確信: 85%] |
| E×P≈const と Levins GRP の同型性 | [確信: 85%] — (SOURCE: Levins 1966 原文参照済) |

---

## Rate-Distortion による再形式化 {#sec_10_rate_distortion}

> **E×P≈const を rate-distortion theory で再定式化する**
> 旧版 (Shannon チャネル容量への直接マッピング) は @nous 再帰検証で致命的欠陥が発見された。
> 以下は rate-distortion theory による修正版。[推定: 72%]

### 旧形式化の問題点 (Shannon 版, 破棄)

| 問題 | 詳細 |
|:-----|:-----|
| E ≈ log\|Ω\| は矛盾 | Newton が統一すると \|Ω\|↓ → E↓ という不合理。説明力は「数え上げ」ではなく「統一」 |
| E×P≈const に反例 | Newton→Kepler、GR→Newton は E と P を同時に増加させた (パラダイム交替) |
| P_s ≈ 1/H(Y\|X) は発散 | 完全理論で H→0, 1/H→∞。相互情報量 I(X;Y) が数学的に自然 |

### Rate-Distortion Framework

理論 T を抽象度 α で記述するとき、「世界の圧縮」として定式化する:

```
Rate R(α)       = モデル複雑性 (Kolmogorov complexity K(T_α))
                  理論 T_α を記述するのに必要なビット数

Distortion D(α) = 予測誤差 (データと予測の不一致)
                  D(α) = E[d(Y, Ŷ_α)] (平均歪み)

R(D) 曲線       = 最小 R を達成する理論のフロンティア
                  R(D) = min_{p(ŷ|y): E[d]≤D} I(Y; Ŷ)
```

### E×P≈const の再解釈

```
旧:  E(α) × P_s(α) ≈ C      (チャネル容量 — 不適切)

新:  R(α) と D(α) は R(D) 曲線上でトレードオフ
     - 大きい α → 低 R (単純なモデル), 高 D (曖昧な予測)
     - 小さい α → 高 R (複雑なモデル), 低 D (精密な予測)

     パラダイム内: R(D) 曲線は固定 → E×P≈const が近似的に成立
     パラダイム交替: R(D) 曲線自体がシフト → E と P が同時に改善可能
```

### HGK コンパイルパスとの対応

| compile path 段階 | R (複雑性) | D (歪み) | 解釈 |
|:-----------------|:----------|:---------|:-----|
| FEP (α≈1) | 最小 | 最大 | 原理は単純だが、具体的予測はできない |
| 座標選択 (d=1) | 中 | 中 | 方向性が定まり、予測が絞られる |
| WF 実行 (d=2) | 大 | 小 | 具体的操作、精密な出力 |
| 行為 (α≈0) | 最大 | 最小 | 完全に具体的、一意の行動 |

### 先行研究

- De Llanza Varona, Buckley & Millidge (2024): "Exploring Action-Centric Representations Through the Lens of Rate-Distortion Theory" — FEP/Active Inference における知覚のrate-distortion最適化
- Friston et al. (2024): "From pixels to planning: scale-free active inference" — RGM (renormalising generative models) による階層的圧縮

> [!NOTE]
> Rate-distortion framework は旧 Shannon 版の3問題を解消する:
>
> 1. E を「説明可能な現象数」から「モデル複雑性 R」に置換 → 統一の矛盾が消える
> 2. P を「1/H」から「歪み D の逆数」に置換 → 発散問題が消える
> 3. パラダイム交替 = R(D) 曲線シフト → Newton/GR の反例を説明可能
>
> ただし、「説明力」を「モデル複雑性の低さ」(Kolmogorov simplicity) と
> 同一視することの妥当性はさらなる検証が必要。[推定: 72%]

---

## Levins のトレードオフとの接続 {#sec_11_levins}

> Levins R (1966), "The Strategy of Model Building in Population Biology", American Scientist 54(4):421-431

### Levins GRP トレードオフ

Levins は科学モデルの3つの性質が同時に最大化できないと主張:

| 性質 | 定義 | DX-012 対応 |
|:-----|:-----|:-----------|
| **Generality** (一般性) | 多くのシステムに適用可能 | **E (説明力)** |
| **Realism** (現実性) | 実際の生物学的構造との対応 | 本 DX では未定義 (中間的性質) |
| **Precision** (精密性) | 定量的予測との合致度 | **P_s (特定的予測力)** |

### 構造的同型

```
Levins (1966):   G × R × P ≤ Budget
DX-012 (2026):   E(α) × P_s(α) ≈ const

Levins の 3変数 → DX-012 の 2変数:
  - G ≈ E (一般性 ≈ 説明力)
  - P ≈ P_s (精密性 ≈ 特定的予測力)
  - R は α の関数として吸収: R(α) = 1 - |α_model - α_target|
```

**洞察**: Levins の GRP トレードオフは DX-012 の E×P≈const の **先行研究**。
Levins は生物学モデルの文脈で、DX-012 は認知理論の文脈で、**同じ構造的制約**を発見している。

> [!IMPORTANT]
> Levins のトレードオフには批判もある (Orzack & Sober 1993 "A Critical Assessment")。
> 3性質の独立性、トレードオフの不可避性、Levins の3つの戦略の排他性に疑問が呈されている。
> DX-012 の E×P≈const も同じ批判が適用可能。
>
> **Rate-distortion 版での再解釈**:
>
> - G (一般性) ≈ 低 R (単純なモデルが広く適用可能)
> - P (精密性) ≈ 低 D (歪みが小さい)
> - R (現実性) → §12 参照

---

## Realism の情報理論的限界 {#sec_12_realism}

> **Levins の「Realism」は Shannon 情報理論で捉えられない**

### 問題

Shannon 情報理論は**構文的 (syntactic)** かつ**統計的 (statistical)** である。
「不確実性の低減」を扱うが、「意味」や「真理」を扱わない。

Levins の Realism = モデルの因果構造が世界の因果構造を反映する度合い。
これは**意味論的 (semantic)** かつ**形而上学的 (metaphysical)** な概念。

```
情報理論が区別できないもの:
  - 天動説 (Ptolemy): 精密な予測、因果構造は誤り
  - 地動説 (Copernicus): 精密な予測、因果構造は正しい
  両者は同じ D (歪み) を達成し得る。しかし Realism は根本的に異なる。
```

### Pearl の因果モデルによる Realism の形式化

| 概念 | 形式化 | 検証方法 |
|:-----|:-------|:--------|
| **Realism** | SCM (Structural Causal Model) の介入不変性 | do-calculus: P(Y \| do(X)) |
| **相関 vs 因果** | 観測分布 P(Y\|X) vs 介入分布 P(Y\|do(X)) | 両者が一致するか |
| **反事実** | 「Xがなかったら Yはどうなったか」 | SCM の counterfactual query |

```
拡張 GRP トレードオフ:

  G (一般性) × P (精密性) × R (現実性) ≤ Budget

  情報理論で形式化可能:
    G → 低 Rate (R) in rate-distortion
    P → 低 Distortion (D) in rate-distortion

  情報理論で形式化不可:
    R → 介入不変性 (Pearl do-calculus)
       = P(Y|do(X)) が実世界と一致する度合い

  つまり: Levins の完全な形式化には
  Shannon + Pearl = 統計的圧縮 + 因果構造
  の両方が必要。
```

> [!NOTE]
> これは HGK の compile path にも示唆を与える。
> FEP → 具体的行為のコンパイルは rate-distortion (R→D の最適化) だが、
> コンパイルされた行為が **世界の因果構造に対して正しいか** は
> 別の検証 (Realism check = do-calculus 相当) が必要。
> HGK の /dia (Krisis) がこの Realism check に対応する可能性がある。
> [仮説: 55%]

---

*DX-012 v2.0.0 — Rate-distortion 再形式化 (§10), Levins 再解釈 (§11), Realism の限界 (§12) (2026-02-14)*
