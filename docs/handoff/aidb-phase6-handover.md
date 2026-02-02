# 🔄 引継ぎ: AIDB収集 Phase 6 - arXiv論文自動収集

**作成日**: 2026-01-20
**ステータス**: 未着手
**優先度**: 中

---

## 概要

AIDB（AI Database）の記事収集プロジェクトの最終フェーズ。週次まとめ記事からarXiv論文リンクを抽出し、自動収集システムを構築する。

## 前提条件

### 完了済み
- ✅ Phase 1-3: AIDB 795記事収集完了
- ✅ Phase 5: LanceDB KB化（1,331チャンク）
- ✅ 収集スクリプト: `forge/scripts/` に配置済み

### 関連ファイル
- `M:\Hegemonikon\forge\Raw\aidb\` - 収集済み記事
- `M:\Hegemonikon\forge\scripts\` - 収集スクリプト
- `M:\.gemini\antigravity\brain\ec06afb0-35af-4a64-adcd-ddc69f6a093b\` - 元セッション

---

## 残タスク

| # | タスク | 詳細 |
|---|--------|------|
| 6.1 | arXiv API調査 | M5 Peira で arXiv API 仕様を調査（進行中） |
| 6.2 | `arxiv-collector.py` 作成 | arXiv論文自動収集スクリプト |
| 6.3 | リンク抽出 | AIDB週次まとめ記事からarXivリンク抽出 |
| 6.4 | LanceDB統合 | 論文をKBに統合（チャンク数拡張） |
| 6.5 | GitHub Actions自動化 | オプション: 週次自動収集 |

---

## 技術仕様

### arXiv API
```
GET https://export.arxiv.org/api/query?search_query=...
```

### 出力形式
```
forge/Raw/arxiv/{year}/{month}/{arxiv_id}.md
```

---

## 開始コマンド

新しいチャットで以下を実行:
```
/plan AIDB Phase 6: arXiv論文自動収集システムの構築
```

---

```
┌─[Hegemonikon]──────────────────────┐
│ M8 Anamnēsis: Handover Created    │
│ Project: AIDB Phase 6             │
│ Status: Pending                   │
└────────────────────────────────────┘
```
