---
doc_id: "KERNEL_PRACTICE_GUIDE"
version: "1.0.0"
tier: "KERNEL"
status: "REFERENCE"
created: "2026-01-23"
---

> **Kernel Doc Index**: [SACRED_TRUTH](SACRED_TRUTH.md) | [axiom_hierarchy](axiom_hierarchy.md) | [doctrine](doctrine.md) | [PRACTICE_GUIDE](KERNEL_PRACTICE_GUIDE.md) ← 📍

# 🛠️ Kernel Practice Guide（運用実践ガイド）

> **目的**: 公理を「読むだけの文書」から「日々の判断基準」へ変換する。

---

## 5分で読む要約

### 公理階層（完全構造）

```
Level 0: FEP統一原理（すべては予測誤差の最小化）
    │
Level 1: 核心公理 ── Flow (推論↔行為) × Value (情報↔目標)
    │
    ├── Level 2a: P-series (核心×核心) → P1-P4 の 4機能 [Phase 2]
    │       純粋定理: Noēsis, Boulēsis, Zētēsis, Energeia
    │
    ├── Level 2b: M-series (核心×選択) → M1-M8 の 8機能 [Phase 1 ✓]
    │       拡張定理: Aisthēsis, Krisis, Theōria, Phronēsis, Peira, Praxis, Dokimē, Anamnēsis
    │
    └── Level 2c: K-series (選択×選択) → K1-K12 の 12修飾子 [Phase 3]
            文脈定理: 状況に応じた行動様式を修飾
```

**数学的構造**: 4 → 8 → 12 の等差数列 (+4) = **合計 24定理**

| シリーズ | 生成方法 | 順列記法 | 積記法 | 数 | Phase |
|---------|----------|----------|--------|-----|-------|
| P-series | 核心 × 核心 | — | 2 × 2 | **4** | 2 |
| M-series | 核心 × 選択 | — | 2 × 4 | **8** | 1 ✓ |
| K-series | 選択 × 選択 | ₄P₂ | 4 × 3 | **12** | 3 |

> K-seriesのみ順列（順序が意味を持つ）

### 核心公理の日常適用

| 公理 | 問い | 行動指針 |
|------|------|----------|
| **Flow** | 「考えるべきか、動くべきか？」 | 情報不足 → 推論優先 / 情報十分 → 行動優先 |
| **Value** | 「知識を増やすか、目標に近づくか？」 | 不確実性高 → 探索 / 明確 → 実行 |

---

## Zero Entropy Protocol 実践例

### 例1: 曖昧な要求への対応

**ユーザー入力**: 「いい感じにドキュメント整理して」

**Zero Entropy 発動**:
```
⚠️ **曖昧さ検知**
検知: "いい感じに"
解釈候補:
[A] ファイル名の命名規則を統一する
[B] 冗長な内容を削除・統合する
→ どちらで進めますか？
```

### 例2: スコープ不明確

**ユーザー入力**: 「全部テストして」

**Zero Entropy 発動**:
```
⚠️ **曖昧さ検知**
検知: "全部"
解釈候補:
[A] forge/gnosis/ のユニットテストのみ
[B] 全workflowの手動実行確認も含む
→ どちらで進めますか？
```

---

## T-Series (Tropos) 日常適用早見表

| 状況 | 発動T | やること |
|------|-------|----------|
| 新しいタスクが来た | T1 Aisthēsis | まず入力を正規化・分類 |
| 複数の選択肢がある | T2 Krisis | 優先度判定、二択に絞る |
| なぜそうなるか不明 | T3 Theōria | 因果モデルを構築 |
| 計画を立てたい | T4 Phronēsis | 戦略策定、ステップ分解 |
| 情報が足りない | T5 Peira | Web検索、Gnōsis検索 |
| 実行する | T6 Praxis | コード書く、ファイル編集 |
| 検証する | T7 Dokimē | テスト実行、批判的評価 |
| 記録する | T8 Anamnēsis | 学びを保存、パターン化 |

---

## X-Series (Taxis) 日常適用早見表
 
 | 状況 | 適用X | 意味 |
 |------|-----------|------|
 | なぜこれをするのか | X-O (メタ認知) | 行動の理由（メタ目的） |
 | どの機能を使うか | X-T (機能間) | 状況に応じた機能選択 |
 | どの順序で | X-K (文脈間) | 文脈間の依存関係 |

---

## Workflow × T-Series 対応表

| Workflow | 発動T | 典型的な出力 |
|----------|-------|-------------|
| `/boot` | T1, T8 | 文脈読込、記憶復元 |
| `/ask` | T5 | 調査依頼書（Perplexity用） |
| `/plan` | T4, T3 | implementation_plan.md |
| `/do` | T6, T2 | コード実装 |
| `/rev` | T7, T8 | レビュー、学び抽出 |
| `/hist` | T8 | 履歴同期 |

---

## Anti-Confidence 実践チェックリスト

セッション開始時に確認（3秒チェック）:

- [ ] 「確実」「当然」を使わない
- [ ] メリットより先にリスクを出す
- [ ] 答えではなくオプションを提示

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| 思考過程が英語になる | GEMINI.md が古い | `/boot` で自動同期 |
| Gnōsisが動かない | CLIパスが古い | `mekhane/anamnesis/cli.py` を使用 |
| 履歴同期エラー | Embedder未セットアップ | `chat-history-kb.py setup` |

---

## リファレンス

- **詳細な公理定義**: [axiom_hierarchy.md](axiom_hierarchy.md)
- **不変真理**: [SACRED_TRUTH.md](SACRED_TRUTH.md)
- **行動原則**: [doctrine.md](doctrine.md)

---

*「迷ったらここを見る」— このガイドは運用中に随時更新される*
