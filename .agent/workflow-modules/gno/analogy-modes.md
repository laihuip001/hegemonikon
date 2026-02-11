---
summary: A3 Gnōmē analogy 拡張モード。アナロジーの深度・領域別8派生モード。
parent: "../gno.md"
hegemonikon: Akribeia
modules: [A3]
version: "1.0"
lineage: "gno.md v1.3 Hub-and-Spoke分離 → v1.0"
derivatives: [analogy_structure, analogy_surface, analogy_negative, analogy_cross, analogy_history, analogy_cs, analogy_physics, analogy_ecology]
ccl_signature: "/gno.analogy+{...}"
---

# /gno analogy 拡張モード

> **Hub**: [gno.md](file:///home/makaron8426/oikos/hegemonikon/.agent/workflows/gno.md)
> **基本 analogy モード**: Hub 内 `/gno.analogy` を参照
> **前提**: 基本 analogy の5段階プロセス (Candidates→Correspondence→Breakdown→Extract→Counter) を理解済みであること

---

## 派生概要

| 派生 | CCL | 目的 | Scale |
|:-----|:----|:-----|:------|
| **analogy_structure** | `/gno.analogy+{depth=structural}` | 構造に基づく深い類推 | Macro |
| **analogy_surface** | `/gno.analogy+{depth=surface}` | 表面的類似に基づく類推 | Micro |
| **analogy_negative** | `/gno.analogy+{type=disanalogy}` | 類推の破綻点・限界発見 | Meso |
| **analogy_cross** | `/gno.analogy+{scope=cross_domain}` | 異領域からの類推 | Macro |
| **analogy_history** | `/gno.analogy+{source=history}` | 歴史的事例からの類推 | Macro |
| **analogy_cs** | `/gno.analogy+{source=computer_science}` | CS概念からの類推 | Meso |
| **analogy_physics** | `/gno.analogy+{source=physics}` | 物理法則からの類推 | Macro |
| **analogy_ecology** | `/gno.analogy+{source=ecology}` | 生態系からの類推 | Macro |

---

## --mode=analogy_structure (構造的類推)

> **CCL**: `/gno.analogy_structure` = `/gno.analogy+{depth=structural}`
> **目的**: 表面ではなく構造に基づく深い類推を行う
> **Scale**: 🌍 Macro

**発動**: `/gno analogy_structure` または「構造的類推」「深い類似」

**プロセス**:

1. 源泉と目標の構造を抽出
2. 構造的対応を発見 ([源泉のA] ↔ [目標のA'], [源泉のR] ↔ [目標のR'])
3. 写像の信頼性を評価
4. 出力: 構造対応 + 構造的洞察

---

## --mode=analogy_surface (表面的類推)

> **CCL**: `/gno.analogy_surface` = `/gno.analogy+{depth=surface}`
> **目的**: 表面的な類似に基づく類推を行う
> **Scale**: 🔬 Micro

**発動**: `/gno analogy_surface` または「表面的」「見た目の類似」

**プロセス**:

1. 表面的特徴を抽出し類似点を発見
2. 表面類似の有用性を評価(HIGH/MED/LOW)
3. 深層との比較
4. 出力: 表面類推 + 有用性 + 限界

---

## --mode=analogy_negative (否定的類推)

> **CCL**: `/gno.analogy_negative` = `/gno.analogy+{type=disanalogy}`
> **目的**: 類推の破綻点・限界を発見する
> **Scale**: 🔭 Meso

**発動**: `/gno analogy_negative` または「類推の限界」「どこで破綻」

**プロセス**:

1. 既存の類推を確認し破綻点を探索
2. 破綻の原因を分析(❌ 破綻点 + 理由)
3. 修正類推を提案
4. 出力: 破綻点一覧 + 修正類推

---

## --mode=analogy_cross (領域横断類推)

> **CCL**: `/gno.analogy_cross` = `/gno.analogy+{scope=cross_domain}`
> **目的**: 異なる領域からの類推を行う
> **Scale**: 🌍 Macro

**発動**: `/gno analogy_cross` または「別の分野から」「異業種」

**プロセス**:

1. 異なる領域を選択し共通構造を探索
2. 転移可能性を評価
3. 移植アイデアを生成
4. 出力: 源泉領域 + 共通構造 + 移植アイデア

---

## --mode=analogy_history (歴史類推)

> **CCL**: `/gno.analogy_history` = `/gno.analogy+{source=history}`
> **目的**: 歴史的事例からの類推を行う
> **Scale**: 🌍 Macro

**発動**: `/gno analogy_history` または「歴史から学ぶ」「過去の事例」

**プロセス**:

1. 類似の歴史事例を探索
2. 類似点・相違点を分析(時代差を考慮)
3. 歴史的教訓を抽出
4. 出力: 歴史事例 + 類似点 + 相違点 + 教訓

---

## --mode=analogy_cs (CS類推)

> **CCL**: `/gno.analogy_cs` = `/gno.analogy+{source=computer_science}`
> **目的**: コンピュータサイエンスからの類推
> **Scale**: 🔭 Meso

**発動**: `/gno analogy_cs` または「CSから」「アルゴリズム的に」

**プロセス**:

1. 問題をCS用語で再定義
2. 関連するCSパターン/アルゴリズムを探索
3. アルゴリズム的解決策を生成
4. 出力: CS概念 + 解法 + 実世界への翻訳

---

## --mode=analogy_physics (物理類推)

> **CCL**: `/gno.analogy_physics` = `/gno.analogy+{source=physics}`
> **目的**: 物理法則からの類推を行う
> **Scale**: 🌍 Macro

**発動**: `/gno analogy_physics` または「物理的に」「力学的に」

**プロセス**:

1. 問題を物理系として捉える
2. 適用可能な物理法則を特定(F=ma, エントロピー等)
3. 類推的解釈を生成し非物理領域へ翻訳
4. 出力: 物理法則 + 類推 + 洞察

---

## --mode=analogy_ecology (生態類推)

> **CCL**: `/gno.analogy_ecology` = `/gno.analogy+{source=ecology}`
> **目的**: 生態系からの類推を行う
> **Scale**: 🌍 Macro

**発動**: `/gno analogy_ecology` または「生態系から」「自然界」

**プロセス**:

1. 問題を生態系として捉える
2. 類似の生態パターンを探索
3. 生態学的洞察を抽出し人工システムへ翻訳
4. 出力: 生態系モデル + パターン + 洞察

---

*v1.0 — gno.md Hub-and-Spoke分離 (2026-02-07)*
