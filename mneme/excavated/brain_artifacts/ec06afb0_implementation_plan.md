# arXiv論文自動収集システム 実装計画

## 目標

AIDBの「今週の注目AI論文」記事からarXivリンクを抽出し、論文メタデータをLanceDBに追加する。

---

## 提案変更

### [NEW] [arxiv-collector.py](file:///C:/Users/raikh/Hegemonikon/forge/scripts/arxiv-collector.py)

論文収集CLIツール:
- `extract` - AIDB記事からarXivリンク抽出
- `fetch` - arXiv APIでメタデータ取得
- `index` - LanceDBへ追加
- `search` - 論文検索

### [MODIFY] [aidb-kb.py](file:///C:/Users/raikh/Hegemonikon/forge/scripts/aidb-kb.py)

論文検索機能の追加（オプション）

---

## 技術仕様

| 項目 | 値 |
|------|-----|
| **API** | `https://export.arxiv.org/api/query` |
| **認証** | 不要（パブリック） |
| **レート制限** | 3秒/リクエスト |
| **ライブラリ** | `arxiv` (lukasschwab) |
| **Python** | 3.12 (.venv-kb312) |

---

## 実装フェーズ

### Phase 1: リンク抽出
```
AIDB記事 → 正規表現でarXivリンク抽出 → arxiv_links.json
```

### Phase 2: メタデータ収集
```
arxiv_links.json → arxiv API → papers_metadata.jsonl
```

### Phase 3: LanceDB統合
```
papers_metadata.jsonl → Embedding生成 → LanceDB追加
```

### Phase 4: 自動化 (オプション)
```
GitHub Actions → 週次実行 → 自動DB更新
```

---

## 検証計画

1. AIDB記事 `100549` からリンク抽出テスト
2. 論文 `2601.00770` のメタデータ取得確認
3. LanceDBへの追加・検索テスト
