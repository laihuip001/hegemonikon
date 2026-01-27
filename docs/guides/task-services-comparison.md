# タスク自動化サービス比較

## Perplexity Tasks vs Jules Tasks

> **作成日**: 2026-01-27  
> **目的**: Hegemonikón における定時自動化の使い分け指針

---

## 概要

| 観点 | **Perplexity Tasks** | **Jules Tasks** |
|------|---------------------|-----------------|
| **本質** | 情報収集・調査の自動化 | コード変更・PR作成の自動化 |
| **入力** | 自然言語の質問・プロンプト | GitHub リポジトリ + プロンプト |
| **出力** | Markdown レポート | コード変更 + Pull Request |
| **実行環境** | Perplexity クラウド（Web検索） | Ubuntu Linux VM（ビルド可能） |
| **APIアクセス** | ❌ UI内のみ（Tasks機能）<br>✅ Sonar API（検索のみ） | ✅ REST API + CLI |
| **外部自動化** | 不可（UIロック） | GitHub Actions 連携可能 |

---

## 料金体系（2026年1月時点）

### Perplexity

| プラン | 月額 | Tasks機能 |
|--------|------|-----------|
| Free | $0 | ❌ |
| Pro | $20 | ✅ |

### Jules / Google AI

| プラン | 月額 | Jules上限 |
|--------|------|-----------|
| Free | $0 | 日次15 / 同時3 |
| Pro | $19.99 | 日次100 / 同時15 |
| **Google AI Ultra** | $249.99 | **日次300 / 同時60**（Jules Ultra込み） |

> **重要**: Jules Ultra は Google AI Ultra に含まれる。追加料金不要。

---

## 使い分け指針

```
Perplexity Tasks          Jules Tasks
───────────────          ─────────────
「知る」                  「変える」

├─ 最新論文サーベイ       ├─ 依存関係更新
├─ 競合技術動向           ├─ #TODO コード実装
├─ セキュリティCVE監視    ├─ テスト追加
├─ 理論整合性チェック     ├─ リファクタリング
└─ 価格アラート           └─ ドキュメント生成
```

---

## Hegemonikón 観点での対応

| Perplexity Tasks | Jules Tasks |
|------------------|-------------|
| **O1 Noēsis** — 深い認識・直観 | **O4 Energeia** — 行為・具現化 |
| **T3 Theōria** — 理論的思考 | **T6 Praxis** — 実践的行為 |

---

## 自動化アーキテクチャ

### パターン A: UI ベース（手動トリガー）

```
Perplexity UI → Scheduled Task → メール通知
Jules UI → Scheduled Task → GitHub PR
```

### パターン B: GitHub Actions（完全自動化）

```
GitHub Actions (cron)
  ├─→ Perplexity Sonar API（検索のみ、Tasks機能ではない）
  └─→ Jules REST API → 自動PR作成
```

> **注意**: Perplexity の「Tasks」機能自体は API 非公開。  
> 定時調査を完全自動化するなら Sonar API を直接呼び出す。

---

## 推奨構成

### 最小コスト構成

- **Perplexity Pro**: $20/月
- **Jules Pro**: $19.99/月  
- **合計**: $39.99/月

### フル機能構成（推奨）

- **Perplexity Pro**: $20/月
- **Google AI Ultra**: $249.99/月（Jules Ultra 込み）
- **合計**: $269.99/月

---

## 参考リンク

- <https://www.perplexity.ai/hub/tasks>
- <https://jules.google/docs/usage-limits/>
- <https://blog.google/products-and-platforms/products/google-one/google-ai-ultra/>
