---
description: 消化品質診断（可換性検証）。自然変換 α の可換図式が成立しているか検証する。
hegemonikon: Akribeia
modules: [A2]
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
version: "4.0"
parent: "/dia"
lineage: "v3.1 + 自然変換統合 → v4.0"
anti_skip: enabled
category_theory:
  core: "自然変換の可換性検証"
  naturality_condition: "αB ∘ F(f) = G(f) ∘ αA for all f: A→B in Ext"
  levels:
    superficial: "成分 αX が定義できない"
    absorbed: "一部の可換図式が不成立"
    naturalized: "全ての可換図式が成立"
lcm_state: beta
---

# /fit: 消化品質診断 (Naturality Verification)

> **親クラス (抽象)**: [A2 Krisis SKILL.md § 消化原則](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md)
> **目的**: 自然変換 α: F ⟹ G の可換条件が全ての図式で成立しているか検証する
> **親コマンド**: /dia

---

## ⚠️ 実行前必須: 親クラス読み込み

> **このステップは省略禁止。必ず実行すること。**

```text
実行手順:
1. view_file ツールで A2 SKILL.md を読み込む
   パス: /home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md
2. 「消化原則 (Digestion Principle)」セクションを確認
3. 3段階消化レベルと4つのチェックリストを理解
4. 確認後、以下の具体的手順を実行
```

---

## 第一原理: 可換性

> **「消化とは、全ての経路が同じ結果に至ること」**

```
          F(f)
  F(A) --------→ F(B)
   |                |
   | αA              | αB
   ↓                ↓
  G(A) --------→ G(B)
          G(f)

可換 = αB ∘ F(f) = G(f) ∘ αA
意味 = 概念Aを先に調理してから関係fを適用しても、
       先に関係fを辿ってから概念Bを調理しても、結果が同じ
```

| 概念 | 旧定義 | 圏論的定義 |
|:-----|:-------|:-----------|
| 消化 | A + B → A' | 自然変換 α: F ⟹ G |
| 付着 | A に B がくっついている | 成分 αX が未定義 or 可換性が崩壊 |
| Naturalized | 境界消失 | **全ての可換図式が成立** |

### なぜ可換性が本質か

可換性が崩れている = **経路によって結果が変わる** = **整合性がない**

例: 概念 A (評議) と概念 B (批評) に関係 f: A→B (評議は批評の特殊形態) があるとき、

- 経路1: A を /syn に調理 → f で /dia に遷移 → G(B) = /dia の批評機能
- 経路2: A から f で B に遷移 → B を /dia に調理 → G(B) = /dia の批評機能
- 可換 = 両経路が同じ → ✅ Naturalized
- 不可換 = 経路1 で /syn に残ってしまう → ⚠️ Absorbed（境界が残る）

---

## Hegemonikón 哲学

> **「システムの末端、端の端まで、可能な限り統制し、一貫させる」**

| 原理 | 圏論的意味 |
|:-----|:-----------|
| エントロピー最小化 | 可換図式の不成立 = 局所的エントロピー増大 |
| 美的整合性 | 全ての図式が可換 = 美しい |
| 消化 > 吸収 | 自然変換 > 単なるマッピング |

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/fit [対象]` | 特定の統合対象を可換性検証 |
| `/fit` | 直近の統合作業を診断 |
| 「馴染んでる？」 | 自然言語トリガー |
| 「可換？」 | 圏論的トリガー |

---

## 実行手順

// turbo-all

### Step 0: 自然変換の特定

```yaml
診断対象:
  素材: [消化された外部コンテンツ]
  関手F: [素材概念 → HGK対象 の素朴マッピング]
  関手G: [素材概念 → HGK対象 の理想マッピング]
  自然変換α: [各成分 αX の一覧]
```

---

## 階層的可換性検証プロトコル

### Level 0: 成分列挙 (Component Enumeration)

> 旧: 原子分解 → 新: 自然変換の成分を列挙

```yaml
process:
  1. 外部圏 Ext の対象と射を確認:
     Ext:
       対象: [A, B, C, ...]
       射:   [f: A→B, g: B→C, ...]

  2. 自然変換 α の成分を列挙:
     α:
       αA: F(A) → G(A)   # 概念Aの調理結果
       αB: F(B) → G(B)   # 概念Bの調理結果
       αC: F(C) → G(C)   # 概念Cの調理結果

output: 成分の一覧表
```

### Level 1: 成分検証 (Component Verification)

> 旧: 単体消化 → 新: 各成分 αX が well-defined か

```yaml
process:
  FOR EACH 対象 X in Ext:
    1. αX: F(X) → G(X) が定義されているか？
       - F(X) が特定されているか → 素朴マッピング存在確認
       - G(X) が特定されているか → 消化先WF存在確認
       - αX (変換パッチ) が具体的か → 変換内容の明確性
    2. αX が well-defined か？
       - F(X) の全要素が G(X) に写像されているか (情報ロスなし)
       - G(X) に不要な「付着」がないか

判定:
  ✅ 全成分 well-defined → Level 2 へ
  ⚠️ 一部成分が曖昧 → 成分の再設計
  ❌ 成分が定義できない → 関手の再設計
```

### Level 2: 可換性検証 (Commutativity Verification)

> 旧: 分子消化 → 新: 各射 f に対する可換図式の検証

```yaml
process:
  FOR EACH 射 f: A→B in Ext:
    1. 経路1を追跡: αB ∘ F(f)
       F(A) --F(f)--> F(B) --αB--> G(B)
    2. 経路2を追跡: G(f) ∘ αA
       F(A) --αA--> G(A) --G(f)--> G(B)
    3. 両経路の結果を比較:
       経路1 = 経路2 → ✅ 可換
       経路1 ≠ 経路2 → ⚠️ 不可換

判定:
  ✅ 全射で可換 → Level 3 へ
  ⚠️ 一部不可換 → 不可換な成分を特定し再設計
  ❌ 大部分が不可換 → 関手そのものの問題、Phase 1 へ差し戻し
```

### Level 3: 全体検証 (Global Naturality)

> 旧: 統合消化 → 新: 自然変換全体の well-definedness

```yaml
process:
  1. 全成分が well-defined (Level 1 通過)
  2. 全可換図式が成立 (Level 2 通過)
  3. 関手性チェック:
     - F が射の合成を保存: F(g∘f) = F(g)∘F(f)
     - G が射の合成を保存: G(g∘f) = G(g)∘G(f)
  4. 自然変換の一意性:
     - 同じ F, G に対して α が（実質的に）唯一か
     - 複数の α が可能な場合、選択の根拠を文書化

判定:
  🟢 Naturalized — 全検証通過
  🟡 Absorbed — Level 1-2 通過だが Level 3 で関手性に問題
  🔴 Superficial — Level 1 で成分が定義できない
```

---

## 診断ステップ (6-Step Process)

### Step 1: 成分存在チェック (Component Existence)

**問い**: 全ての αX が定義されているか？

```python
for X in Ext.objects:
    if alpha[X] is None:
        return "Superficial"  # 成分未定義
    if not is_well_defined(alpha[X]):
        return "Absorbed"     # 成分が曖昧
```

**チェック項目**:

- [ ] 全概念に対して消化先が特定されている
- [ ] 消化パッチ（αX）が具体的に記述されている
- [ ] 情報ロスが発生していない

### Step 2: 境界残存チェック (Boundary Detection)

**問い**: 素材の「形」がまだ見えるか？（可換性の表面的検証）

**チェック項目**:

- [ ] 素材名がそのまま残っていない
- [ ] 「移行元」への参照が本文中にない（Lineageは可）
- [ ] 統合先の用語体系に統一されている
- [ ] 素材固有の概念が Hegemonikón 用語に翻訳されている

### Step 3: 可換性チェック (Commutativity Check)

**問い**: 全ての射 f で αB∘F(f) = G(f)∘αA が成立するか？

```yaml
FOR EACH f: A→B in Ext:
  経路1: F(A) → F(B) → G(B)  # αB ∘ F(f)
  経路2: F(A) → G(A) → G(B)  # G(f) ∘ αA

  可換性: ✅ / ⚠️
  不可換の場合の原因:
    - αA の設計が射 f を考慮していない
    - G(f) が F(f) と構造的に異なる
    - 消化先に「境界」が残っている
```

### Step 4: 強化度評価 (Empowerment Score)

**問い**: 自然変換 α は価値を生んでいるか？

| 評価軸 | 問い | スコア |
|:-------|:-----|:-------|
| capability_expansion | 消化前にできなかったことができるようになったか？ | 0-3 |
| coherence_improvement | 統合先の一貫性は上がったか？ | -1, 0, +1 |
| cognitive_load_reduction | ユーザーが覚えることは減ったか？ | -1, 0, +1 |

**empowerment_score** = capability + coherence + cognitive (最大5, 最小-2)

### Step 5: 消化レベル判定 (Naturality Level)

| レベル | 圏論的条件 | 実践的意味 |
|:-------|:-----------|:-----------|
| 🟢 Naturalized | 全成分 well-defined ∧ 全図式可換 | 境界消失、「元からあった」 |
| 🟡 Absorbed | 成分定義済だが一部不可換 | 機能するが境界が見える |
| 🔴 Superficial | 成分が未定義 | ファイルはあるが統合されていない |

### Step 6: レポート出力

```
━━━ /fit: 可換性検証レポート ━━━

📋 対象: {素材名}
🔀 自然変換: α: F ⟹ G

━━━ 成分検証 ━━━

| 対象 X | F(X) | G(X) | αX | 状態 |
|:-------|:-----|:-----|:---|:-----|
| A | {F(A)} | {G(A)} | {patch} | ✅/⚠️ |

━━━ 可換性検証 ━━━

  f: A→B
          F(f)
  F(A) --------→ F(B)
   |                |
   | αA              | αB
   ↓                ↓
  G(A) --------→ G(B)
          G(f)
  結果: ✅ 可換 / ⚠️ 不可換（原因: {reason}）

━━━ 判定 ━━━

  消化レベル: [🔴 Superficial / 🟡 Absorbed / 🟢 Naturalized]
  強化スコア: {N}/5
  可換図式充足率: {M}/{Total} ({percentage}%)

━━━ 推奨アクション ━━━

| 優先度 | アクション | 理由 |
|:-------|:-----------|:-----|
| P1 | {action} | {reason} |

📌 結論: {総合評価 - 1文で}
```

---

## 消化失敗時の対応

```mermaid
graph TD
    A["不可換検出"] --> B{"成分 αX は定義済?"}
    B -->|No| C["🔴 Superficial — 関手の再設計 (Phase 1)"]
    B -->|Yes| D{"全図式が可換?"}
    D -->|一部不可換| E["🟡 Absorbed — 不可換成分の再設計 (Phase 2)"]
    D -->|全不可換| F["関手 F or G の問題 — Phase 1 差し戻し"]
```

---

## 使用例

### 例1: 完全消化 (Naturalized)

```
/fit M-1 仮想ユーザー座談会 → /syn

━━━ 成分検証 ━━━
| 対象 X | F(X) | G(X) | αX | 状態 |
| ユーザーペルソナ | 新規WF /vox | /syn Persona Mode | Mode追加 | ✅ |
| 多視点評価 | 新規WF /eval | /syn 既存機能 | 包含 | ✅ |
| 専門家召喚 | 独立機能 | /syn Persona Mode | 吸収 | ✅ |

━━━ 可換性検証 ━━━
  f: ユーザーペルソナ → 多視点評価 (ペルソナは評価の一形態)
  経路1: /vox → /eval → /syn 既存 = /syn 多視点
  経路2: /vox → /syn Persona → /syn 多視点 = /syn 多視点
  結果: ✅ 可換

消化レベル: 🟢 Naturalized
📌 M-1 は /syn の一部として自然変換された。
```

### 例2: 部分消化 (Absorbed)

```
/fit HEPHAESTUS → tekhne-maker v6.0

━━━ 可換性検証 ━━━
  f: ArchReview → StressTest (レビューはストレスの前提)
  経路1: HEPH.arch → HEPH.stress → /mek stress = /mek stress
  経路2: HEPH.arch → /mek SAGE → ??? = 「HEPHAESTUS Architecture」用語が残存
  結果: ⚠️ 不可換（SAGE Mode 内に境界が残存）

消化レベル: 🟡 Absorbed
📌 機能は統合済だが、「HEPHAESTUS」用語の境界が可換性を崩している。
推奨: P2 — SAGE Mode 説明から固有名詞を一般化し、可換性を回復する。
```

---

## Artifact 出力保存規則

**保存先**: `<artifact_directory>/fit_<target>.md`

**保存理由**:

1. **可換性の履歴** — 時系列で可換図式の充足率を追跡
2. **改善アクションの記録** — 不可換成分の特定と修正
3. **セッション跨ぎで継続** — 未完の可換性回復を引き継ぎ

---

## Hegemonikon Status

| Module | Workflow | Skill (親クラス) | Status |
|:-------|:---------|:-----------------|:-------|
| A2 Krisis | /fit | [消化原則](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md) | v4.0 Ready |

---

*v3.1 — 親子アーキテクチャ適用 (2026-02-07)*
*v4.0 — 自然変換統合。消化診断を可換図式の検証として再設計。Superficial/Absorbed/Naturalized を圏論的に再定義 (2026-02-08)*
