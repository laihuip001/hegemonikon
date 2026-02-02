# Cognitive Algebra 演算子拡張 Phase 4+ 実装計画

> **Hegemonikón**: O1 Noēsis + S2 Mekhanē
> **目的**: CCL (Cognitive Control Language) の演算子体系を完成させる

---

## 📋 背景と目標

### 現状 (Phase 1-3 完了)

| Phase | Operators | Status |
|:------|:----------|:-------|
| Phase 1 | `+` (Deepening), `-` (Reduction) | ✅ 14 WF に展開 |
| Phase 2 | `^` (Expansion) | ✅ 14 WF に展開 |
| Phase 3 | `×` (Fusion), `~` (Oscillation) | ✅ 定義済み |
| Phase 4 | `&`, `/`, `%`, `\|`, `@`, `?` | 🏗️ **本計画** |

### 主要課題

1. **`&` 演算子の正式定義**: `×` との差別化
2. **新規演算子の検討**: プログラミング言語・認知科学に基づく拡張
3. **ドキュメント統一**: operators_and_layers.md への統合

---

## 🎯 提案変更

### 新規演算子一覧

| Symbol | Name | Meaning | Cognitive Action | Example |
|:-------|:-----|:--------|:-----------------|:--------|
| **`&`** | Parallel (並列) | 同時実行 (分離可能) | 2定理を並列に発動、独立した出力 | `/bou&zet` |
| **`/`** | Factor (因子) | 要素分解 | 1つの出力を N 個の構成要素に分解 | `/noe/` |
| **`%`** | Residual (剰余) | 残余・例外 | エッジケース・例外・残された問いに焦点 | `/dia%` |
| **`\|`** | Pipe (連鎖) | 順次合成 | 前の出力を次の入力として連鎖 | `/zet\|bou` |
| **`@`** | Focus (焦点) | 指定焦点 | 特定の派生/観点に焦点を限定 | `/noe@nous` |
| **`?`** | Conditional (条件) | 条件分岐 | 状況に応じた分岐実行 | `/ene?` |

### 演算子分類体系

#### Tier 1: 単項演算子 (Unary)

強度/次元を変更。単一ワークフローに適用。

| Operator | Category | Effect |
|:---------|:---------|:-------|
| `+` | Intensity | 深化 (3-5x 出力) |
| `-` | Intensity | 縮約 (最小出力) |
| `^` | Dimension | メタ層へ移行 |
| `/` | Structure | 分解 (N要素化) |
| `%` | Scope | 例外焦点 |
| `!` | **Forbidden** | 全展開 (禁術) |

#### Tier 2: 二項演算子 (Binary)

2つのワークフロー/定理を結合。

| Operator | Category | Effect |
|:---------|:---------|:-------|
| `×` | Merge | 融合 (不可分化) |
| `~` | Temporal | 振動 (交互発動) |
| `&` | Parallel | 並列 (分離可能) |
| `\|` | Sequential | 連鎖 (順次パイプ) |

#### Tier 3: 修飾演算子 (Modifier)

演算子ではなく「引数」として機能。

| Operator | Effect |
|:---------|:-------|
| `@` | 派生選択 (`/noe@nous` = `/noe --derivative=nous`) |
| `?` | 条件分岐モード |

---

## 📁 変更ファイル

### [MODIFY] [operators_and_layers.md](file:///home/laihuip001/oikos/.gemini/antigravity/knowledge/cognitive_algebra_system/artifacts/architecture/operators_and_layers.md)

- **変更内容**: 新規演算子 (`&`, `/`, `%`, `|`, `@`, `?`) の定義追加
- **セクション追加**:
  - §1.1 Unary Operators (単項)
  - §1.2 Binary Operators (二項)
  - §1.3 Modifier Operators (修飾)
- **Advanced/Future Operators セクション削除**: 正式定義に昇格

### [MODIFY] [overview.md](file:///home/laihuip001/oikos/.gemini/antigravity/knowledge/cognitive_algebra_system/artifacts/overview.md)

- **変更内容**: Operations at a Glance テーブルを更新
- **新セクション**: Tier 分類表を追加

### [MODIFY] [roadmap.md](file:///home/laihuip001/oikos/.gemini/antigravity/knowledge/cognitive_algebra_system/artifacts/implementation/roadmap.md)

- **変更内容**: Phase 4 完了をマーク、Phase 5 (Full Integration) を追加

---

## ✅ 検証計画

### Automated Tests

既存テストスイートを使用して、変更がリグレッションを起こしていないことを確認。

```bash
# hegemonikon ディレクトリで実行
cd /home/laihuip001/oikos/hegemonikon
pytest tests/ mekhane/fep/tests/ -v --ignore=mekhane/symploke/tests/test_jules_client.py
```

**期待結果**: 全テスト PASSED (既存の 8 SKIPPED は許容)

### Manual Verification

1. **演算子ドキュメント確認**: `operators_and_layers.md` をレビューし、定義の一貫性を確認
2. **KI 整合性**: Antigravity の Cognitive Algebra KI 更新がサマリーと整合していることを確認

---

## ⚠️ ユーザー確認事項

> [!IMPORTANT]
> **演算子の優先順位について**
>
> 以下の演算子設計について確認をお願いします:
>
> 1. **`@` 演算子**: `--derivative=` の糖衣構文として導入して良いか？
> 2. **`?` 演算子**: 条件分岐のユースケースが明確か？
> 3. **`/` (Factor) と `%` (Residual)**: 使用頻度が低い可能性。Phase 5 に延期するか？

---

## 📊 実装スケジュール

| Step | Description | Est. |
|:-----|:------------|:-----|
| 1 | `operators_and_layers.md` 更新 | 10 min |
| 2 | `overview.md` 更新 | 5 min |
| 3 | `roadmap.md` 更新 | 5 min |
| 4 | pytest 実行 (リグレッション確認) | 2 min |
| 5 | git commit | 2 min |

---

*Draft 1.0 — 2026-01-29*
