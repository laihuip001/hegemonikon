---
risk_tier: L1
reversible: true
requires_approval: false
risks: []
fallbacks: []
name: Category Theory Engine
description: |
  圏論に基づく構造認識エンジン。
  FEP Skill が「行動選択の objective」なら、本 Skill は「構造認識の言語」。
  前順序圏のガロア接続 + [0,1]-豊穣圏として HGK の圏論を正当化し、
  12随伴対・Trigonon・CCL の圏論的意味を日常の認知に統合する。

triggers:
  - 圏論的な分析を行う時
  - 随伴対/関手/η/ε を扱う時
  - 構造の保存・忘却を問う時
  - Trigonon / X-series を参照する時
  - 「なぜこの変換は正当か」を問う時
---

# 🏛️ Category Theory Engine — 構造認識の言語

> **圏論は「対象が何であるか」ではなく「対象間の関係がどう保存されるか」で世界を記述する。**
> **HGK において、これは「正しさ」ではなく「構造の整合性」を問う言語である。**

---

## Layer 0: なぜ圏論か — 哲学的基盤

### HGK と圏論の関係

HGK の 96要素体系（7公理→24定理→72関係）は圏論的構造を持つ。
ただし、HGK の圏論は **一般の圏 (Category)** ではなく、
**前順序圏 (Preorder Category)** のガロア接続として正当化される。

| 主張 | 正当性 | 根拠 |
|:-----|:-------|:-----|
| HGK の随伴は数学的に正しい | ✅ | ガロア接続 = 随伴の特殊ケース |
| Drift ∈ [0,1] は定量化できる | ✅ | [0,1]-豊穣圏の Hom 値に対応 |
| 一般の圏と同一視できる | ❌ | 関手性（合成保存）が破れる |

> **正直さ**: HGK は前順序圏の枠内で正当。それ以上を主張しない。

### なぜ前順序圏で十分か

前順序圏は「AからBに行けるか行けないか」という二値判断だが、
[0,1]-豊穣圏にすることで「どの程度行けるか」が表現できる。

- Hom(A,B) ∈ [0,1] → A から B への変換の「質」
- Drift = 1 - ε → 構造の非冗長性の欠損
- 完全忠実 (ε = 1.0) は理想。現実では ε ∈ [0.7, 0.95]

---

## Layer 1: 操作的定義 — 使えるレベルで

### 基本概念

| 概念 | 前順序圏での意味 | HGK での操作 | 口語 |
|:-----|:----------------|:-------------|:-----|
| **関手 (Functor)** | 順序保存写像 | 構造を壊さない変換 | 「関手張って」 |
| **随伴 (F⊣G)** | ガロア接続 | 左=構造付与、右=構造剥離 | 「随伴立てて」 |
| **η (unit)** | G∘F ≥ Id | 取り込んで忘却→元以上 | 「η 通る？」 |
| **ε (counit)** | F∘G ≤ Id | 忘却して取り込み→元以下 | 「ε どのくらい？」 |
| **Drift** | 1 - ε | 構造の欠損量 | 「Drift 測って」 |
| **Limit (meet)** | 下限 (inf) | 全条件を満たす最豊かなもの | 「下限取って」 |
| **Colimit (join)** | 上限 (sup) | 共通基底で統合 | 「上限取って」 |
| **Kan 拡張** | 最良の近似 | 部分情報からの全体推定 | 「延長して」 |
| **Kalon (Fix)** | Fix(G∘F) | 収束×展開の不動点 | 「kalon か？」 |

**Kan 拡張の HGK 使用例**:

- /sop (調査): 少数の既知論文から、未知の関連領域を「最良の近似」で推定する
- /boot (起動): 過去の Handoff（部分情報）から、セッション全体（全体）を復元する
- /noe (認識): 表面的な観察（部分）から、深い構造（全体）を「延長」する

### 方向の絶対規則

```
左随伴 F = 自由 = 構造付与 = 外→内
右随伴 G = 忘却 = 構造剥離 = 内→外

この方向は HGK 全体で一貫。逆にすると全体が崩れる。
```

### η/ε の操作的解釈

```
η: G(F(x)) ≥ x   — 取り込んで忘却しても元以上（情報保存）
ε: F(G(y)) ≤ y   — 忘却して取り込んでも元以下（冗長性なし）

完全随伴: η = Id かつ ε = Id → 完全な可逆変換（理想）
現実: η ≈ 0.9, ε ≈ 0.8 → Drift = 0.2
```

---

## Layer 2: HGK 対応

### 12随伴対 一覧

| # | F (左随伴) | G (右随伴) | 意味 | WF |
|:--|:-----------|:-----------|:-----|:---|
| 1 | **Noēsis** | **Zētēsis** | 深い認識 ⊣ 問いの発見 | /noe ⊣ /zet |
| 2 | **Energeia** | **Boulēsis** | 行為 ⊣ 意志 | /ene ⊣ /bou |
| 3 | **Krisis** | **Epistēmē** | 判定 ⊣ 知識 | /dia ⊣ /epi |
| 4 | **Mekhanē** | **Praxis** | 方法 ⊣ 実践 | /mek ⊣ /pra |
| 5 | **Pistis** | **Doxa** | 確信 ⊣ 信念 | /pis ⊣ /dox |
| 6 | **Propatheia** | **Orexis** | 前感情 ⊣ 欲求 | /pro ⊣ /ore |
| 7 | **Metron** | **Stathmos** | 測定 ⊣ 評価 | /met ⊣ /sta |
| 8 | **Eat** | **Fit** | 取り込み ⊣ 検証 | /eat ⊣ /fit |
| 9 | **Boot** | **Bye** | 起動 ⊣ 終了 | /boot ⊣ /bye |
| 10 | **Tropos** | **Hodos** | 方向転換 ⊣ 道程 | /tro ⊣ /hod |
| 11 | **Gnōsis** | **Eukrineia** | 知識 ⊣ 判明 | /gno ⊣ /euk |
| 12 | **Khōra** | **Stasis** | 場 ⊣ 配置 | /kho ⊣ /sta |

### Trigonon (K₃三角形)

```
           O (Ousia)
          L1 × L1
         ╱     ╲
        S       H
      (Schema) (Hormē)
      ╱         ╲
    P ─── K ─── A
 (Perigraphē) (Akribeia)
  L1.5²   (Kairos)  L1.75²
```

| 構造 | 要素 | 接続 | 意味 |
|:-----|:-----|:-----|:-----|
| **Pure (頂点)** | O, P, A | 自己積 | 座標空間の原点 |
| **Mixed (辺)** | S, H, K | 異種積 | 頂点間の橋渡し |
| **Bridge** | S↔H, S↔K, H↔K | 同型的 | 必然的接続 (24関係) |
| **Anchor** | O↔S, O↔H 等 | 類比的 | 妥当な接続 (48関係) |

### CCL 演算子の圏論的意味

| CCL | 統一的意味 | L1 (前順序) | L2 (豊穣) | L3 (弱2-圏) |
|:----|:----------|:-----------|:----------|:-----------|
| `/` | 関手適用 | 順序保存写像 | Hom 値付き変換 | 1-cell の適用 |
| `+` | **精度を上げる** | meet (下限) | precision ↑ | 1-cell への精度加重 |
| `-` | **精度を下げる** | join (上限) | precision ↓ | 1-cell への粗さ加重 |
| `~` | **振動する** | ≤ の往復 | Hom 上の振動 | 1-cell ペアの交互適用 |
| `>>` | 合成 | パイプライン | Hom の合成 | 1-cell の水平合成 |
| `{}` | 群 | 並列実行 | 積 | 1-cell の集合 |

> **設計判断 (2026-02-11)**: +/- は 1-cell (WF) への修飾であり、2-cell (派生遷移) ではない。
> meet/join = 詳細/要点 は同一操作の L1/CCL 両面。
> 2-cell は派生間の遷移 (nous⇒phro) であり、`two_cell.py` で実装。

---

## Layer 3: 実装手順

### 既存ツール

| ツール | パス | 用途 |
|:-------|:-----|:-----|
| **cone_builder** | `mekhane/fep/cone_builder.py` | Limit (Cone) の構築・検証 |
| **attractor** | `mekhane/fep/attractor.py` | Series attractor（oscillation スコア） |
| **two_cell** | `mekhane/fep/two_cell.py` | 弱2-圏: 派生間の 2-cell 構造 (L3) |
| **drift_calculator** | `mekhane/fep/drift_calculator.py` | TF-IDF Drift 計算 (L2) |
| **CCL dispatch** | Hermēneus MCP `dispatch()` | CCL 式の解析と実行 |
| **Gnōsis CLI** | `mekhane/anamnesis/cli.py` | 339 CT論文のベクトル検索 |

### 随伴検証の手順

```
1. 随伴対を特定: F⊣G を宣言
2. η を検査: G(F(x)) → 元に戻るか？
   例: /eat + /fit → 消化して検証 → η 通るか
3. ε を検査: F(G(y)) → 再現するか？
   例: /bye + /boot → 終了して起動 → ε 通るか
4. Drift を測定: 1 - ε = 構造欠損量
5. 三角恒等式: F→F∘G∘F→F, G→G∘F∘G→G が成立するか
```

### Gnōsis 検索ガイド

```bash
# 基本検索
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/anamnesis/cli.py search "query"

# 有用なクエリ例
"adjoint functor category theory software"        # 随伴×ソフトウェア
"Galois connection abstract interpretation"        # ガロア接続×抽象解釈
"compositional distributional semantics"           # 合成的意味論
"polynomial functor category theory"               # 多項式関手
"Kan extension best approximation"                 # Kan拡張
"string diagram monoidal category"                 # ストリング図
"category theory cognitive science"                # 圏論×認知
```

---

## Layer 4: 判断支援 — 5つの問い

### Q1: この変換は構造を保存しているか？ （関手性チェック）

> 関手 = 「構造を壊さない変換」。前順序圏では順序保存。

| チェック | 具体例: OK | 具体例: NG |
|:---------|:----------|:----------|
| **順序保存** | /noe→/dia の順序が変換後も保たれる | リファクタ後に依存関係が暗黙的に変わる |
| **合成保存** | A→B→C のパイプラインが一貫 | commit A+B は通るが A+B+C で壊れる |
| **恒等保存** | 何もしないデプロイが安全 | no-op のはずが副作用を持つ |

**コード判断での Q1**:

- リファクタ: 元のテストが全て通るか？ → 順序保存
- API 変更: 既存クライアントが壊れないか？ → 合成保存
- 抽象化: 具体型→インターフェース化で失われる制約は？ → 忘却の検出

### Q2: この随伴の η/ε は何か？ （往復の質を問う）

> 全ての F⊣G に対して: η（取り込んで忘却→元に戻るか）と ε（忘却して取り込み→再現するか）。

- /eat ⊣ /fit: η = 消化して元に戻るか？ ε = 原文を再現できるか？
- /boot ⊣ /bye: η = 起動→終了→起動で文脈が保存されるか？ ε = 終了→起動→終了で Handoff が保存されるか？

**Drift > 0.3 は要注意。何が失われたかを明示的に記録すべき。**

### Q3: この判断の普遍性は何か？ （Limit の問い）

> Limit (meet) = 全条件を満たす最も豊かなもの。Cone = 候補。

| 場面 | Limit の問い | 具体的チェック |
|:-----|:------------|:---------------|
| 設計 | 「全要件を満たす最も単純な設計は？」 | YAGNI を超える複雑さがないか |
| /noe | 「Kalon は全 Cone より優れているか？」 | 他の候補を排除した理由を明示 |
| 意思決定 | 「全ステークホルダーが受容できるか？」 | 却下された代替案のリスト |

**普遍性テスト**: 「この解は、同じ制約を持つ別の問題にも使えるか？」

### Q4: 何を忘却して、何を保存したか？ （忘却関手の自覚）

> 右随伴 G = 忘却関手。抽象化は常に何かを捨てている。

| 判断するとき | 問うべきこと |
|:-------------|:-------------|
| 要約を書く | 何を削ったか？ 本質は残ったか？ |
| API を設計する | 実装の何を隠したか？ 隠すべきでないものは？ |
| 判断を下す | どの代替案を排除したか？ 排除は正当か？ |

### Q5: この構造の双対は何か？ （反転の発見）

> 圏論の強力な原理: 全ての概念には双対がある。

| 概念 | 双対 | HGK での意味 |
|:-----|:-----|:-------------|
| 分析 (分解) | 合成 (統合) | /noe (分析) ↔ Cone (統合) |
| 探索 | 実行 | O3 Zētēsis ↔ O4 Energeia |
| 具体化 | 抽象化 | F (自由) ↔ G (忘却) |
| 生成 (Poiēsis) | 審査 (Dokimasia) | Star(O) ↔ Complement(O) |

**→ 「反対のことを考える」だけで、盲点を発見できる。**

### Q6: これは kalon か？ （不動点の判定）

> Fix(G∘F): 蒸留(G)しても変わらず、展開(F)してもなお豊か。
> 詳細: [kernel/kalon.md](file:///home/makaron8426/oikos/hegemonikon/kernel/kalon.md)

| Step | チェック | 結果 |
|:-----|:---------|:-----|
| **G テスト** | 蒸留しても変化しないか？ | 不変 → lim 条件 ✅ |
| **F テスト** | 展開して3つ以上導出可能か？ | 3+ → colim 条件 ✅ |
| **Fix 判定** | 両方 ✅ → ◎ kalon | G∘F の不動点 |

**三属性**: Fix(G∘F) ∧ Presheaf ∧ Self-referential

| 属性 | 意味 | 判定 |
|:-----|:-----|:-----|
| Fix(G∘F) | 収束と展開の結節点 | G/F テスト |
| Presheaf | 概念は数式を包含する（多面性） | 抽象1+具体3 を満たすか |
| Self-referential | 定義が定義を実証する | 定義プロセスが内容と一致するか |

---

## Layer 5: 理論的基盤

### 推奨文献

| 文献 | 著者 | 理由 |
|:-----|:-----|:-----|
| *Seven Sketches in Compositionality* | Fong & Spivak | Applied CT の入門。HGK に最も近い |
| *Categories for the Working Mathematician* | Mac Lane | 標準教科書。随伴の厳密な定義 |
| *Physics, Topology, Logic and Computation* | Baez & Stay | 4分野の圏論的統一 |
| *Categorical Quantum Mechanics* | Coecke & Kissinger | ストリング図の実践 |

### Gnōsis 知識基盤

- **339論文** を LanceDB にインデックス
- Applied CT, adjoint functors, Kan extensions, string diagrams, 圏論×認知科学
- `cli.py search "query"` でセマンティック検索可能

### 批判と限界

| 限界 | 対処 |
|:-----|:-----|
| HGK は前順序圏に限定 | **限定ではなく出発点**。L2 ([0,1]-豊穣), L3 (弱2-圏) が共存 |
| 関手性の破れ | 合成保存を仮定しない。個別に検証する |
| 自然変換の多義性 | L1 では ≤ に退化するが、L2/L3 では豊かな構造。層を明示する |
| 数学的厳密性 vs 実用性 | Level B（精密な比喩）を目標。Level A（厳密な証明）は個別に追求 |

---

## 発動条件

| キーワード | 発動する Layer |
|:-----------|:--------------|
| 随伴、F⊣G、ガロア接続 | L1 + L2 |
| η、ε、Drift | L1 + L3 |
| Trigonon、K₃、Bridge/Anchor | L2 |
| 関手、構造保存 | L1 + L4 (Q1) |
| 忘却、抽象化 | L4 (Q4) |
| 双対、反転 | L4 (Q5) |
| 普遍性、Limit | L4 (Q3) |
| Kalon、kalon か、不動点、Fix | L1 + L4 (Q6) |
| CCL の圏論的意味 | L2 |
| Kan 拡張、最良近似 | L1 + L3 |
| 圏論 × AI、Gnōsis 論文 | L5 (検索) |

---

## FEP Skill との関係

| FEP Skill | Category Skill | 関係 |
|:----------|:---------------|:-----|
| VFE/EFE = 行動選択の目的関数 | 関手/随伴 = 構造認識の言語 | **Why ↔ How** |
| 精度 = チャネルの信頼性 | η/ε = 変換の品質 | 情報の質を問う |
| 探索/実行 = EFE 2項分解 | F/G = 自由/忘却 | 行動の方向 |
| Markov blanket = 観測境界 | 忘却関手 = 何が見えないか | 盲点への自覚 |

> **FEP が「なぜそう行動すべきか」を問い、圏論が「その行動は構造を保存しているか」を問う。**

---

*Category Theory Engine v3.2 — CCL多層定義 + two_cell/drift_calculator 統合 (2026-02-11)*
*v1.0 (291行) → v2.0 (F/G統一+Q1/Q3具体化+Kan拡張) → v3.0 (Kalon認定) → v3.1 (Q6 Kalon判定統合) → v3.2 (CCL修飾子のL1/L2/L3統一)*
*対称: FEP Skill v2.1 と同じ6層構造*
