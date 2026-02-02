# 🚀 AIDB全記事収集→Forge KB化プロジェクト

## アーキテクチャ修正
- [x] browser_subagent動作確認（AIDB 5件のURL取得成功）
- [x] 正しい設計: Antigravity内完結（外部Node.js不要）

## Phase 1: 環境準備 ✅
- [x] 1.1 ディレクトリ作成
- [x] 1.2 .gitignore修正（AIDB除外ルール）
- [x] 1.3 README, capture_log.csv作成
- [ ] 1.2 README作成（`Raw/aidb/README.md`）
- [ ] 1.3 依存ライブラリインストール
- [ ] 1.4 Gitコミット

## Phase 2: URL収集 ✅
- [x] 2.1 `node scripts/phase2-collect-urls.js` 実行
- [x] 2.2 `url_list.txt` 確認（804件取得完了）

## Phase 3: Markdown収集 🚧
- [x] 3.1 Cookie取得（ブラウザセッション利用）
- [x] 3.2 パイプライン構築（`browser_subagent` + `phase3-save-batch.py`）
- [/] 3.3 バッチ処理実行
    - [x] Test Batch (0-5)
    - [x] Article 23 (Index 23, `100016`) - Processed (Stateless)
    - [x] Article 24 (Index 24, `100329`) - Processed (Stateless)
    - [x] Article 25 (Index 25, `100282`) - Processed (Stateless - 3 chunks)
    - [x] Article 26 (Index 26, `52813`) - Processed (Stateless)
    - [x] Article 27 (Index 27, `99628`) - Processed (Stateless - 2 chunks)
    - [x] Article 28 (Index 28, `89070`) - Processed (Stateless - 2 chunks)
    - [-] Article 29 (Index 29, `88028`) - Skipped (404 Not Found)
    - [x] Article 30 (Index 30, `99878`) - Processed (Stateless - 2 chunks)
- [x] 3.4 全件完了（並列実行中 + 高速収集中）
    - [x] Batch 1 (31-150): 120/120 (Browser + FastScript)
    - [x] Batch 2 (151-270): 114/120 (6 Error Skip)
    - [x] Batch 3 (271-390): 120/120 (完了)
    - [x] Batch 4 (391-510): 120/120 (完了)
    - [x] Batch 5 (511-594): 94/84 (完了 - 超過確認)

## Phase 4: Gitコミット
- [/] 4.1 `Raw/aidb/_index/`をステージング (User Action)
- [ ] 4.2 コミット: "docs: AIDB collection complete (795 articles)"
- [ ] 4.2 コミット＆プッシュ

## Phase 5: KB化
- [x] 5.1 環境構築 (Python 3.12 + LanceDB + ONNX Runtime)
- [x] 5.2 インデックス生成 (1,331 chunks)
- [x] 5.3 検索ツール (`aidb-kb.py`) 実装

## Phase 6: arXiv論文自動収集
- [/] 6.1 M5 Peira調査（arXiv API仕様）
- [ ] 6.2 `arxiv-collector.py` スクリプト作成
- [ ] 6.3 AIDB週次まとめ記事からリンク抽出
- [ ] 6.4 LanceDB統合（論文KB拡張）
- [ ] 6.5 GitHub Actions自動化（オプション）
