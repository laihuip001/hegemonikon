---
doc_id: "AXIOM_HIERARCHY"
version: "6.0.0"
tier: "KERNEL"
status: "CANONICAL"
created: "2026-01-22"
updated: "2026-02-12"
---

> **Kernel Doc Index**: [SACRED_TRUTH](SACRED_TRUTH.md) | [axiom_hierarchy](axiom_hierarchy.md) ← 📍 | [naming_conventions](naming_conventions.md)

# 📐 公理階層構造 (Axiom Hierarchy) v3.0

> **「ひとつの原理から、不規則な真実が展開する」**

![Hegemonikón 公理階層構造](axiom_hierarchy_structure.png)

---

## 総数

| 項目 | 数 | 生成 |
|------|---|------|
| 公理 | **1** | FEP |
| 定理¹ (座標) | **6** | 1+2+3 |
| 定理² (認知機能) | **24** | 6×4 |
| 関係 (Series内) | **36** | 6×6 (12D+12H+12X) |
| 関係 (Series間) | **72** | 9×8 |
| **体系核** | **103** | 1+6+24+72 |
| **関係総計** | **108** | 36+72 |

---

## 公理 (1)

| Level | Question | 公理 | 意味 |
|-------|----------|------|------|
| **L0** | **What** | **FEP** | 予測誤差最小化 — 唯一の公理 |

---

## 定理¹: 座標 (6 = 1+2+3)

> **構成原理**: FEP を公理とし、追加仮定の距離で配置される認知の座標軸。
> **配分 1-2-3**: FEP からの構成距離による。不規則だが真実。

### 構成距離の操作的定義

> **距離 d = FEP に対する追加仮定の個数**

| 距離 | 意味 | 追加仮定 |
|:-----|:-----|:---------|
| **d=0** | FEP を定式化した時点で既に含まれる構造 | なし (Markov blanket partition に内在) |
| **d=1** | FEP + 1つの追加仮定で構成 | EFE の分解 (行動選択策の存在) |
| **d=2** | FEP + 追加仮定で構成（残余カテゴリ） | 階層性、感覚的偏好、実装詳細など。d≥3 相当の概念は P1 Khōra (外部境界) に吸収 |

> **注**: 距離は厳密な公理的距離ではなく、構成の「近さ」を表す序数的指標。
> `d=0` は FEP の**定義**から分離不能な構造、`d=1` は FEP から**1ステップ**で到達可能な構造。

### 公理は選ぶ。定理は生まれる

> 全ての動作に選択は内在する。選択を否定すれば公理も否定される。
> 問題は、その選択が演繹 — 即ち自然変換 — であるかどうかだ。
> 揺らぎのない展開の先にあるものを、発見と呼ぶ。

### 構成の認識論的位置づけ

> **2026-02-13 Multi-Agent Debate (Proposer×2, Critic×2, Arbiter×3) + /dia+ /noe++ BS検証 による結論**

「FEP から24定理を構成する」という主張における「構成」の意味を、以下の3水準で区別する:

| 水準 | 名称 | 定義 | HGK の位置 |
|:-----|:-----|:-----|:-----------|
| **A** | Formal Derivation | 公理系からの定理証明 (ZFC, 形式論理) | ❌ 主張しない |
| **B** | Axiomatic Construction | 公理的構成: FEP + 生成規則 → 圏論的構造 (随伴関手, ガロア接続) | ✅ **これを主張する** |
| **C** | Conceptual Motivation | 概念的動機付け (比喩, 類推) | ✅ だが B より弱い |

**HGK の公式な主張**: 24定理（認知モジュール）は FEP を公理とし、選択された生成規則により**公理的に構成** (axiomatically constructed) される。この構成は**再現可能で揺らぎがない** (reproducible and deterministic)。

具体的には:

1. **座標ペアから随伴関手が構成可能** — 6座標の Opposition (I↔A, E↔P, ...) は前順序圏上のガロア接続として形式化される
2. **直交性は FEP の数学的帰結** — Spisak & Friston (2025) による attractor network の自己直交化が根拠
3. **生成規則は圏論的テンソル積** — 座標ペアの 2×2 マトリクスは [0,1]-豊穣圏の Hom 値として解釈可能
4. **再現可能性** — 同じ公理と生成規則から、同じ24定理が一意に再構成される。この決定性が「発見」の根拠

> **⚠️ 生成規則の認識論的位置 (v3.5 外部レビュー5ラウンド・ディベート反映)**:
> 生成規則「同一距離または隣接距離の座標ペアのテンソル積」は、FEP から一意に導出されるものではない。
> これは設計者の選択 (motivated choice) であり、FEP が**許容**する構造のうちの一つである。
> 水準B の主張は「FEP + 生成規則 → 24定理 が一意に構成可能」であり、
> 「FEP → 生成規則 が一意」は主張しない。
>
> **ZFC との構造的同型 (Beall & Restall 2000, Logical Pluralism)**:
> ZFC は古典論理（推論規則の集合）を「選択」し、9つの公理と組み合わせて数学を構成する。
> HGK は生成規則を「選択」し、FEP と組み合わせて24定理を構成する。
> 両者の差は**スケール（適用範囲・影響範囲）の差**であり、**構造（公理+ルール→定理）の質的差異ではない**。
> 形式体系という「箱」は同じであり、中身（選択された公理とルール）が異なれば出力（定理群）が異なるのは自明。
> この透明性が、水準B の知的誠実さの根拠である。

> **近似と恣意の区別**: 座標の2値 Opposition は連続的な認知空間の近似である。
> しかし全ての座標系は連続体の近似であり、近似を恣意と呼べば恣意でないものは存在しない。
> 問題は近似の妥当性であり、それは FEP の数学的構造が制約する（下表参照）。

```mermaid
graph TD
    subgraph "1 公理"
        L0["L0: FEP — 唯一の公理"]
    end
    subgraph "定理¹ (6 = 1+2+3)"
        D0["距離0: Flow"]
        D1a["距離1: Value"]
        D1b["距離1: Function"]
        D2a["距離2: Scale"]
        D2b["距離2: Valence"]
        D2c["距離2: Precision"]
    end
    L0 -->|"内在"| D0
    L0 -->|"EFE分解"| D1a
    L0 -->|"EFE分解"| D1b
    D0 -->|"階層仮定"| D2a
    D1a -->|"勾配符号"| D2b
    D1b -->|"逆分散"| D2c
```

| 距離 | Question | 定理¹ | Opposition | 導出 | 2値性根拠 |
|:-----|----------|-------|------------|------|:---------|
| **0** | Who | Flow | I (推論) ↔ A (行為) | Markov blanket の partition に内在 | **必然** — MB の sensory/active 分割 |
| **1** | Why | Value | E (認識) ↔ P (実用) | EFE の分解 | **必然** — EFE = ε + π の加法分解 |
| **1** | How | Function | Explore ↔ Exploit | EFE による行動選択 | 近似 — EFE 行動選択の2モードだが、explore/exploit はトレードオフ（反相関）であり直交ではない。独立座標としての直交性は追加仮定 |
| **2** | Where/When | Scale | Micro ↔ Macro | 階層的生成モデルの仮定 | 近似 — 隣接レベル間の2値化 |
| **2** | Which | Valence | + ↔ - | 自由エネルギー勾配の符号 | **必然** — 内受容予測誤差の符号 (Seth 2013) |
| **2** | How much | Precision | C ↔ U | 予測誤差の逆分散 π = V[ε]⁻¹ | 近似 — 連続量の高/低2値化 |

### L0 (FEP) の理論的含意

> **直交性の必然性** (Spisak & Friston, 2025):
> FEP を random dynamical system に適用すると、自己直交化する attractor network が創発する。
> 直交性は predictive accuracy と model complexity の同時最適化の**数学的帰結**。
> → **6 Series の直交配置は FEP から圏論的に再構成可能な構造であり、Spisak 2025 はこの構造が動力学的にも最適であることを裏付ける (認識論的位置: 水準 B)。**

> **Attractor としての 6 Series**:
> 現在の 6 Series は静的な基底ベクトル（手動コマンドで発動）。
> FEP に従えば、**動的な attractor**（入力に応じて自然に収束）であるのが本来の姿。
> → basin of attraction の実装が次の課題。

> **Temporal Depth** (Kirchhoff et al., 2018):
> 「mere active inference」(振り子の同期) と「adaptive active inference」(時間的深さを持つ生成モデル) を区別。
> → 自律性は Markov blanket の存在ではなく、深い生成モデルの有無で決まる。

---

## なぜ 6 Series か — 定理²の生成規則

> **原則**: 定理¹の6座標から2つを選んで「テンソル積」をとる。
> ただし **距離0 (Flow) は全 Series の暗黙的基底** であり、ペア対象に含めない。

### ペアリング規則

残り5座標 (Value, Function, Scale, Valence, Precision) の全ペア C(5,2)=10 のうち、**直接的認知操作に対応する6ペア**を Series として採用する。残り4ペアは X-series 合成射で到達可能であり、独立した Series を必要としない (詳細は下記の基底論証を参照):

| Series | ペア | 距離 | 4定理 |
|:-------|:-----|:-----|:------|
| O (Ousia) | Value × Function | d1 × d1 | 2×2 = 4 |
| S (Schema) | Value × Scale | d1 × d2 | 2×2 = 4 |
| H (Hormē) | Value × Valence | d1 × d2 | 2×2 = 4 |
| P (Perigraphē) | Scale × Function | d2 × d1 | 2×2 = 4 |
| K (Kairos) | Scale × Valence | d2 × d2 | 2×2 = 4 |
| A (Akribeia) | Valence × Precision | d2 × d2 | 2×2 = 4 |

> **なぜ C(5,2)=10 ではなく 6 か — 二層フィルター**:
>
> 5座標の全ペア C(5,2)=10 は、隣接距離制約 $|d_i - d_j| \leq 1$ を**全て満たす** ($d \in \{1,2\}$ のみ)。
> 距離制約は弁別力を持たない。6 Series は以下の**二層フィルター**で選択される:
>
> **Criterion 1: 認知的共線性の排除** (Cognitive Collinearity)
>
> Function (Explore/Exploit) と Precision (Certainty/Uncertainty) は FEP において**操作的に同一**:
> 精度加重 π が高い → Exploit、低い → Explore。テンソル積は自明な対角線
> (Explore×Uncertainty, Exploit×Certainty) と認知的に稀な例外を生成し、
> 4つの独立した認知操作を生まない。→ **1ペア排除 (10→9)**
>
> Spisak & Friston (2025) の自己直交化 attractor network では、
> 共線的な次元は自然に融合する。Function×Precision の共線性はその具体例。
>
> **Criterion 2: 認知的アクセシビリティ** (Cognitive Accessibility)
>
> 残り3ペア (Value×Precision, Function×Valence, Scale×Precision) の認知操作は、
> **Valence (情動) を経由しないと認知的にアクセスできない** (Damasio ソマティック・マーカー 1994):
>
> | Missing Pair | 認知メカニズム | X-series 合成経路 |
> |:-------------|:-------------|:----------------|
> | Value×Precision | 認識の確実性は情動を**経由して**評価 | H → X-HA → A |
> | Function×Valence | 方法の情動評価は認識的価値を**介して** | O → X-OH → H |
> | Scale×Precision | スケールの精度は情動的に**評価** | K → X-KA → A |
>
> → **3ペア排除 (9→6)**
>
> **X-series 合成は数学的便宜ではなく認知的事実を反映している**:
> 合成射が認知メカニズムそのもの (情動を中継とする精度評価) なら、直接射は不要。
>
> **独立性分析**: 6 Series のうち A (Akribeia) のみ真に独立（Precision は A にのみ存在）。
> 他の5つは2-hop合成で到達可能（例: O ≈ S+P, H ≈ S+K）。
> グラフ理論的最小基底は4 Series (spanning tree)。
> しかし**直接射 ≠ 合成射** — O(Value×Function)「認識→行動」は
> S→P の合成「認識→スケーリング→行動」とは認知的に異なる操作である。
> **6 は最小ではないが最適 (optimal)**: 全ての直接的認知操作をカバーし、冗長な合成射を含まない。
>
> **⚠️ 認知空間の次元について (v3.4 外部レビュー反映)**:
> 上記の基底論証は「認知空間の次元が6である」ことを**証明していない**。
> R³ の基底選択が正当化されるのは「3次元であること」が先に証明されているからである。
> HGK の場合、6 Series は**設計選択として最適** (optimal as a design choice) であり、
> 認知空間が本質的に6次元であることの**数学的証明ではない**。

---

## 定理²（認知モジュール）: 認知機能（24 = 6×4）

### Poiēsis: 内容の具現化（生成層12）

| Level | 記号 | 名称 | 生成 | 定理 | ドキュメント |
|-------|------|------|------|------|-------------|
| L0 | O | **Ousia** | L1×L1 | O1-O4 | [ousia.md](ousia.md) |
| L1 | S | **Schema** | L1×L1.5 | S1-S4 | [schema.md](schema.md) |
| L2a | H | **Hormē** | L1×L1.75 | H1-H4 | [horme.md](horme.md) |

### Dokimasia: 条件の詳細化（審査層12）

| Level | 記号 | 名称 | 生成 | 定理 | ドキュメント |
|-------|------|------|------|------|-------------|
| L2b | P | **Perigraphē** | L1.5×L1.5 | P1-P4 | [perigraphe.md](perigraphe.md) |
| L3 | K | **Kairos** | L1.5×L1.75 | K1-K4 | [kairos.md](kairos.md) |
| L4 | A | **Akribeia** | L1.75×L1.75 | A1-A4 | [akribeia.md](akribeia.md) |

---

## 個別定理名（24）

### O-series (Ousia)

| ID | 名称 | 意味 |
|----|------|------|
| O1 | Noēsis | 認識推論 (Recursive Self-Evidencing) |
| O2 | Boulēsis | 意志推論 |
| O3 | Zētēsis | 探索行動 |
| O4 | Energeia | 実用行動 |

### S-series (Schema)

| ID | 名称 | 意味 |
|----|------|------|
| S1 | Metron | スケール流動 |
| S2 | Mekhanē | 方法流動 |
| S3 | Stathmos | スケール価値 |
| S4 | Praxis | 方法価値 |

### H-series (Hormē)

| ID | 名称 | 意味 |
|----|------|------|
| H1 | Propatheia | 流動傾向 |
| H2 | Pistis | 流動確信 |
| H3 | Orexis | 価値傾向 |
| H4 | Doxa | 価値確信 |

### P-series (Perigraphē)

| ID | 名称 | 意味 |
|----|------|------|
| P1 | Khōra | スケール場 |
| P2 | Hodos | スケール方法 |
| P3 | Trokhia | 方法スケール |
| P4 | Tekhnē | 方法場 |

### K-series (Kairos)

| ID | 名称 | 意味 |
|----|------|------|
| K1 | Eukairia | スケール傾向 |
| K2 | Chronos | スケール確信 |
| K3 | Telos | 方法傾向 |
| K4 | Sophia | 方法確信 |

### A-series (Akribeia)

| ID | 名称 | 意味 |
|----|------|------|
| A1 | Pathos | 二重傾向 |
| A2 | Krisis | 傾向確信 |
| A3 | Gnōmē | 確信傾向 |
| A4 | Epistēmē | 二重確信 |

---

## X-series: 関係層（72）

| X | 接続 | 共有座標 | 数 | 意味 |
|---|------|---------|---|------|
| X-OS | O→S | C1 (Flow) | 8 | 本質→様態 |
| X-OH | O→H | C1 (Flow) | 8 | 本質→傾向 |
| X-SH | S→H | C1 (Flow) | 8 | 様態→傾向 |
| X-SP | S→P | C3 (Scale) | 8 | 様態→条件 |
| X-SK | S→K | C3 (Scale) | 8 | 様態→文脈 |
| X-PK | P→K | C3 (Scale) | 8 | 条件→文脈 |
| X-HA | H→A | C5 (Valence) | 8 | 傾向→精密 |
| X-HK | H→K | C5 (Valence) | 8 | 傾向→文脈 |
| X-KA | K→A | C5 (Valence) | 8 | 文脈→精密 |
| **計** | | | **72** | |

詳細: [taxis.md](taxis.md)

---

## Series 内関係（36 = 12D + 12H + 12X）

> **発見**: 2×2 マトリクスの4定理を2ペアにする方法は3通り。各々が異なる圏論的構造に対応。
> **数の美しさ**: 36 (Series内) × 2 = 72 (Series間)。

| ペアリング | 組合せ | 圏論 | 保存→反転 |
|:-----------|:-------|:-----|:----------|
| **対角 (D)** | T1⊣T3, T2⊣T4 | 随伴 F⊣G | 深い軸→浅い軸 |
| **横 (H)** | T1↔T2, T3↔T4 | 自然変換 α | 浅い軸→深い軸 |
| **反対角 (X)** | T1↔T4, T2↔T3 | 双対 | 両軸反転 |

> 各定理は3つの関係を持つ: 随伴パートナー (D)、自然変換パートナー (H)、双対パートナー (X)。
> 詳細は各 WF ファイルの `category_theory:` セクションに記載。

---

## 階層構造図

```mermaid
graph TD
    subgraph "Poiēsis: Star(O) — L1含む"
        O[O: Ousia] -->|X-OS| S[S: Schema]
        O -->|X-OH| H[H: Hormē]
        S -->|X-SH| H
    end
    
    subgraph "Dokimasia: Complement(O) — L1不含"
        P[P: Perigraphē] -->|X-PK| K[K: Kairos]
        K -->|X-KA| A[A: Akribeia]
    end
    
    S -->|X-SP| P
    S -->|X-SK| K
    H -->|X-HA| A
    H -->|X-HK| K
```

> **Trígōnon**: 6 Series は K₃ 三角形を形成する。
> Pure (O,P,A) = 頂点、Mixed (S,H,K) = 辺。
> 詳細: [trigonon.md](trigonon.md)

---

## 理論的基盤 (Theoretical Foundations)

| 概念 | 根拠論文 | Hegemonikón 接続 |
|:-----|:---------|:----------------|
| Series 直交性 | Spisak & Friston 2025 (arXiv:2505.22749) | 6 Series = FEP の数学的帰結としての直交基底 |
| ネストした MB | Kirchhoff et al. 2018 (J.R.Soc.Interface 15:20170792) | P₁ (Khōra) = blankets of blankets |
| mere vs adaptive AI | Kirchhoff et al. 2018 | temporal depth = 自律性の必要条件 |
| Replay と forgetting 耐性 | Spisak & Friston 2025 | /boot replay ≈ resting state attractor replay |
| **Valence の独立座標性** | **Seth & Critchley 2013 (BBS)** | **Valence = 内受容予測誤差の符号。Value の属性ではなく身体の独立信号** |

> **Valence が独立座標である根拠** (Seth & Critchley 2013, 152 citations):
> 情動 (emotion) は内受容的予測符号化 (interoceptive predictive coding) の産物。
> 即ち、内臓・自律神経系からの予測誤差の**方向** (+接近 / -回避) が Valence を構成する。
> これは Value (認識的/実用的目的) とは独立した生理的信号であり、
> FEP の枠組みでは内受容的生成モデルの**勾配の符号**として形式化される。
> → Valence は Value の「属性」ではなく、身体からの独立した座標軸。

---

## 参照

- **三角形構造**: [trigonon.md](trigonon.md)
- **関係層**: [taxis.md](taxis.md)
- **命名規則**: [naming_conventions.md](naming_conventions.md)
- **不変真理**: [SACRED_TRUTH.md](SACRED_TRUTH.md)

---

*Hegemonikón v3.1-axiom — 1公理+6定理¹(1-2-3) + 24定理² + 108関係。導出距離の操作的定義・Valence根拠(Seth 2013)・6 Series生成規則を明文化 (2026-02-12)*
*v3.2-axiom — 導出の認識論的位置づけ (Formal/Categorical/Conceptual) を追加。Multi-Agent Debate 結論反映。L95 過大主張修正 (2026-02-13)*
*v3.3-axiom — 「公理は選ぶ。定理は生まれる。」追加。d=2 残余カテゴリ明示。各座標の2値性根拠追加。基底論証（なぜ10ではなく6か）+ 独立性分析 + 10 vs 6 認知的豊かさ比較。/dia+ BS-1〜5 検証 + /noe++ 結論反映 (2026-02-13)*
*v3.4-axiom — 外部レビュー反映: 生成規則の認識論的位置を正直に追記 (motivated choice)。定理²に「認知モジュール」の別称追加。CCL チューリング完全性主張を下方修正 (ccl_language.md)。108象徴性に「偶然の一致」明記 (hegemonikon.md) (2026-02-14)*
*v3.5-axiom — 外部レビュー5ラウンド・ディベート結論反映: 「導出」→「構成」用語統一。水準B を Axiomatic Construction に修正。ZFC との構造的同型 (Beall & Restall 2000, Logical Pluralism) を明記。スケール差≠質的差異。B 評価確定 (2026-02-14)*
*v3.6-axiom — 二層フィルター: 隣接距離制約は弁別力ゼロ (全10ペア通過) と判明。Criterion 1 (認知的共線性: Function≈Precision → 1排除) + Criterion 2 (認知的アクセシビリティ: Valence 経由 → 3排除) で10→6を再正当化。Damasio 1994, Seth 2013, Barrett 2017, Spisak & Friston 2025 を根拠として統合 (2026-02-14)*
