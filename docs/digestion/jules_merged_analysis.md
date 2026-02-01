# Jules Merged PR 分析レポート

> **Generated**: 2026-02-01 10:12 JST
> **Source**: 11 Merged PRs from Jules API
> **Purpose**: 「なぜ Merge されたか」からの学習

---

## 📊 Merged 11件の内訳

| カテゴリ | 件数 | PR番号 |
|:---------|-----:|:-------|
| ⚡ Performance/Bolt | 6 | #51, #46, #45, #41, #33, #31 |
| 🛡️ Safety/Recovery | 2 | #25, #18 |
| 🔧 Feature | 2 | #20, #5 |
| 🐛 Bugfix | 1 | #2 |

---

## 🏆 成功パターン分析

### Pattern 1: 測定可能な改善 (Measurable Improvement)

**6件中6件** のパフォーマンス PR は具体的な測定値を含んでいた：

| PR | Before | After | 改善率 |
|:---|:-------|:------|:-------|
| #51 | N+1 round-trips | 1 round-trip | O(N)→O(1) |
| #45 | 179.05 MB | Streaming | ~90%削減 |
| #41 | 0.1325 s/text | 0.075 s/text | 43%高速化 |
| #33 | Sequential | aiohttp | 5x高速化 |
| #31 | 1.23s | 0.68s | 1.8x高速化 |

> **原則**: 数値で証明できる改善は Merge される

---

### Pattern 2: 安全性への直接貢献 (Direct Safety Contribution)

# 25, #18 (Vault Backup) は **既知の障害モード** に対処していた：

- `t8-anamnesis/SKILL.md` に記載された "Vault Corruption failure mode"
- アトミック書き込み + バックアップ + フォールバック読み込み

> **原則**: 既知のリスクを軽減する変更は Merge される

---

### Pattern 3: 具体的な機能追加 (Concrete Feature)

# 20 (Prompt-Lang MCP Server) は明確な新機能を提供：

- MCP サーバー実装
- `compile_async` メソッド追加
- テスト付き

# 5 (Incremental Updates) も同様：

- 重複排除の仕組みを実装
- バッチ削除 (batch size 100)
- `sync` コマンドの改善

> **原則**: 明確な機能追加はテスト付きで Merge される

---

### Pattern 4: 環境互換性の修正 (Environment Compatibility)

# 2 (Windows Path Fix) は **プラットフォーム固有の問題** を解決：

- `is_safe_path` 関数の堅牢化
- Windows ドライブマッピング対応
- 大文字小文字の非感受性

> **原則**: 環境依存の問題修正は Merge される

---

## 🎯 Hegemonikón への示唆

### 1. Jules の「良い仕事」の条件

Jules が生成した変更が Merge されるためには：

1. **測定可能** - Before/After の数値がある
2. **具体的** - コード変更が明確
3. **テスト付き** - 検証可能
4. **既知の問題への対処** - 既存のドキュメントで言及されている問題

### 2. 343件の Open PR が Merge されない理由

Open のままの PR は主に **docs/reviews** 形式で：

- コード変更なし（ドキュメントのみ）
- 測定可能な改善なし
- 「視点」は提供するが「実装」は提供しない

これは **意図的な設計** と言える。Jules Synedrion は「実装者」ではなく「評価者」として機能している。

### 3. 消化すべきもの

| カテゴリ | 消化方法 |
|:---------|:---------|
| Merged 11件 | 実装パターンとして学習 |
| Open 343件 | 視点・評価軸として学習 |

---

## 📐 抽出された原則（Gnōmē 候補）

1. **「数値で語れ」** - 測定可能な改善は説得力を持つ
2. **「既知のリスクを狙え」** - ドキュメント化された問題への対処は受け入れられやすい
3. **「コードを書け」** - 視点だけでなく実装を提供すると Merge される
4. **「テストを付けろ」** - 検証可能な変更は信頼される

---

*Analysis completed for Phase 1 of Jules Perspectives Digestion*
