# K-series 構造最適化 熟考ログ

> **Hegemonikón**: M4 Phronēsis-S + M3 Theōria-S + M5 Peira
> **日時**: 2026-01-25 12:35
> **入力**: パプ君調査レポート（ask_k-series_structure_review.md）

---

## Step 0: 壁の認識 + 複雑度判定

### 問題特定
- **局所最適**: T-series のフォーマットを「そのまま」K-series に適用
- **見落とし**: LLM 認知プロセスへの最適化が不足

### 複雑度判定
**Medium**: 複数視点が必要（構造設計 + LLM認知 + 美学）

---

## Step 1: 前提の洗い出し

| 前提 | 確信度 | 検証結果 |
|------|--------|---------|
| T-series フォーマットは K-series にも最適 | 0.7 | ❌ K-series は用途が異なる |
| セクション順序は「説明順」が良い | 0.6 | ❌ 「検証ファースト」が LLM に有効 |
| 多いセクション = 網羅的 = 良い | 0.5 | ❌ 認知負荷増加のトレードオフ |
| 日本語で統一が良い | 0.8 | ⚠️ メタデータは英語/ID ベースが機械向き |
| ギリシャ文字(Κ)は美しい | 0.9 | ⚠️ 美しいが検索性に難あり |

---

## Step 2: 多視点分析

### 🔴 Pessimist（悲観的視点）
**最悪のケースは？**

1. **YAML frontmatter のスキーマ不統一**
   - IDE が triggers/keywords を解析できず、スキル検索が機能しない
   - 解決: スキーマを固定化し、バリデーションを追加

2. **セクション過多による認知負荷**
   - LLM が 12 セクションを全て読み込むとトークン浪費
   - 解決: 必須セクションを 9-10 に削減

3. **ギリシャ文字 (Κ) の検索問題**
   - 検索ボックスで「K」と打っても「Κ」がヒットしない
   - 解決: ID ベース (K1, K2...) を frontmatter に追加

### 🟢 Optimist（楽観的視点）
**隠れた可能性は？**

1. **検証ファースト設計の威力**
   - Trigger を Core Function より前に配置 → LLM が「使うべきか」を即判断
   - 効果: 推論精度 +10%（論文根拠あり）

2. **フロー図の導入**
   - Processing Logic を ASCII/Mermaid 図に
   - 効果: 認知負荷 -31.5%（論文根拠あり）

3. **Configuration の標準化**
   - YAML 形式でパラメータを定義
   - 効果: 将来的な自動チューニングに対応可能

### 🟡 Realist（現実的視点）
**制約とリソースは？**

1. **12 Skills を全て書き直すコスト**
   - 1 Skill あたり 30-45 分 → 約 6-9 時間
   - 対策: テンプレート化 + バッチ処理

2. **既存 T-series との一貫性**
   - K-series だけ異なる構造だと混乱
   - 対策: T-series も同じ構造に段階的移行

3. **IDE 統合の未確定要素**
   - Antigravity の schema 対応が不明
   - 対策: schema はオプショナルに

---

## Step 3: 外部探索結果の統合

### パプ君レポートの主要知見

| 知見 | 根拠 | 採用判定 |
|------|------|---------|
| **検証ファースト** | LLM は「評価 < 生成」（認知負荷） | ✅ 採用 |
| **3レベル階層 (H1-H2-H3)** | StructRAG 研究 | ✅ 採用 |
| **Trigger 早期配置** | 初期決定の影響大 | ✅ 採用 |
| **Edge Cases 5-8 例** | 網羅的エラー認識で転移学習↑ | ⚠️ 部分採用（5例に） |
| **Test Cases 2-3 例** | 多いと認知負荷↑ | ✅ 採用 |
| **フロー図追加** | 視覚化で認知負荷 -31.5% | ✅ 採用 |
| **frontmatter 拡張** | IDE 統合向上 | ✅ 採用 |
| **50-70 トークン目標** | メタデータはcompact | ⚠️ 目標として設定 |

---

## Step 4: 統合と批判

### 統合結論

**改善版 K-series SKILL.md 構造:**

```
1. YAML Frontmatter（拡張版）
   - id, name, category, description
   - triggers[], keywords[]
   - when_to_use, when_not_to_use
   - schema（オプション）

2. Header（問い・公理・役割）

3. When to Use（=早期判定）★新規
   - ✓ Trigger となる条件
   - ✗ Not Trigger

4. Core Function

5. Processing Logic（フロー図）★図追加

6. Matrix（簡潔版）

7. 適用ルール（if-then-else）

8. Edge Cases / Failure Modes（5例）★拡張

9. Test Cases（3例）★削減

10. Configuration

11. Integration（オプション）
```

### 自己批判

**Q: この結論の弱点は？**
- 実装コストが 6-9 時間と高い
- 対策: Phase 分割で漸進的に実装

**Q: 何を見落としている？**
- T-series との一貫性問題
- 対策: K-series 完了後、T-series へ同じ構造を適用

---

## Step 5: 結論

| 選択肢 | 判定 |
|--------|------|
| **パラダイムシフト採用** | ✅ |
| 局所解維持 | ❌ |

**採用する改善:**
1. セクション順序変更（Trigger を Core より前へ）
2. YAML frontmatter 拡張（triggers, when_to_use）
3. Processing Logic に図追加
4. Edge Cases 5例、Test Cases 3例
5. ID ベース命名（Κ1 → K1）

**棄却する改善（過剰）:**
- schema フィールド（IDE 未対応）
- Integration のオプション化（既存を維持）

---

## 実装計画

### Phase 1: テンプレート作成
- 改善版 SKILL.md テンプレートを 1 つ作成
- Creator レビュー

### Phase 2: K-series 一括更新
- 12 Skills を新テンプレートで書き直し
- Git コミット

### Phase 3: T-series 移行（将来）
- K-series の結果を検証後、T-series へ適用

---

┌─[Hegemonikón]──────────────────────┐
│ M4 Phronēsis-S: 深層戦略完了       │
│ M3 Theōria-S: パラダイム分析完了   │
│ M5 Peira: 外部探索 [パプ君レポート]│
│ 複雑度: Medium                     │
│ 局所解: T-series フォーマットコピー│
│ 大域解: 検証ファースト構造         │
│ 結論: 採用 (根拠: LLM認知最適化)   │
└────────────────────────────────────┘

📝 /think 完了
