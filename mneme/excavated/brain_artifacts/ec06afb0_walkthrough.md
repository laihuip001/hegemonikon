# AIDB収集プロジェクト 進捗レポート

## ✅ 完了したマイルストーン

### Phase 2: 全記事URLの収集
- **成果**: 804件のユニーク記事URLを特定
- **方法**: `browser_subagent`でsitemap.xmlを解析（Node.js環境非依存）
- **場所**: [Raw/aidb/_index/url_list.txt](file:///C:/Users/raikh/Forge/Raw/aidb/_index/url_list.txt)

### Phase 3: 自動収集パイプラインの確立
Antigravity内完結型の収集フローを構築・検証しました。

1. **バッチ分割**: 名前順・日付順にURLを切り出し
2. **ブラウザ自動巡回**: `browser_subagent`が順次アクセスし、ログイン状態を維持したまま記事を取得
3. **Markdown変換**: ブラウザ内でHTML解析・MD変換を実行
4. **ローカル保存**: PythonスクリプトでFrontmatter付きMarkdownとして保存

**実績**: 5件（URL番号10-14）および3件（URL番号20-22）の収集に成功
[Raw/aidb/2026/01/79561.md](file:///C:/Users/raikh/Forge/Raw/aidb/2026/01/79561.md)

### Phase 3.5: 大規模記事の安定収集戦略（Stateless Chunked Retrieval）
全記事収集に向け、トークン制限と信頼性を克服する新戦略「**Stateless Chunked Retrieval**」を確立・検証しました。
- **課題**: 1記事1万文字を超える長文記事に対し、一括取得しようとするとトークン制限やタイムアウトが発生する。
- **解決策**:
    1. **ステートレス**: ステップごとに確実にページ再読み込みを行い、ブラウザ状態依存によるデータ取り違え（Article 20 vs 21問題）を排除。
    2. **チャンク分割**: 本文を「0-6000文字」「6000文字-末尾」に分割して取得し、Python側で結合。
- **検証結果**: Article 21, 22の実証に成功。

#### 検証動画
**Article 21 (Init Success)**
![Article 21 Scraping](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_21_retry_init_1768731503662.webp)

**Article 22 (Stateless Metadata)**
![Article 22 Metadata](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_22_stateless_meta_1768731796069.webp)

- **Article 23 (`100016`)**: 
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_23_stateless_meta_1768732407705.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_23_stateless_chunk1_1768732437204.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_23_stateless_chunk2_1768732484781.webp)
- **Article 24 (`100329`)**:
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_24_stateless_meta_1768732857416.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_24_stateless_chunk1_1768732886536.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_24_stateless_chunk2_1768732951443.webp)
- **Article 25 (`100282`)**:
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_25_stateless_meta_1768734259513.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_25_stateless_chunk1_1768734296129.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_25_stateless_chunk2_1768734345357.webp) (Truncated in display)
  - Chunk 3: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_25_stateless_chunk3_1768734518786.webp) (Tail retrieved and stitched)
- **Article 26 (`52813`)**:
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_26_stateless_meta_1768735048944.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_26_stateless_chunk1_1768735088106.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_26_stateless_chunk2_1768735139967.webp) (Short content, empty return)
- **Article 26 (`52813`)**:
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_26_stateless_meta_1768735048944.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_26_stateless_chunk1_1768735088106.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_26_stateless_chunk2_1768735139967.webp) (Short content, empty return)
- **Article 27 (`99628`)**:
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_27_stateless_meta_1768735253345.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_27_stateless_chunk1_1768735289726.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_27_stateless_chunk2_1768735344280.webp)
- **Article 28 (`89070`)**:
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_28_stateless_meta_1768735489489.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_28_stateless_chunk1_1768735524794.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_28_stateless_chunk2_1768735572581.webp)
- **Article 29 (`88028`)**:
  - Skipped: 404 Not Found (User-verified).
- **Article 30 (`99878`)**:
  - Metadata: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_30_stateless_meta_1768736487175.webp)
  - Chunk 1: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_30_stateless_chunk1_1768736524410.webp)
  - Chunk 2: ![Video](/C:/Users/raikh/.gemini/antigravity/brain/ec06afb0-35af-4a64-adcd-ddc69f6a093b/single_scraping_index_30_stateless_chunk2_1768736593216.webp)

All articles in this batch were successfully saved to disk and recorded in `manifest.jsonl`. Using 3 chunks for Article 25 proved effective.
---

## 🛠️ 次のステップ

残り約800件の記事収集を実行します。
Antigravityの制約上、一度に全件を実行するとタイムアウトのリスクがあるため、**50〜100件単位のバッチ実行**を推奨します。


## ✅ Phase 3完了: 全804件（実質795件）収集達成

並列処理と高速化スクリプトの導入により、全記事の収集を完了しました。

### 収集ストラテジーの変遷
1. **Single Browser**: 当初の手法。遅延とトークン制限で困難。
2. **Stateless Chunked**: 安定性は向上したが、速度に限界。
3. **Parallel Browser**: 5並列で実行。Batch 3, 4, 5を完遂。
4. **Fast Http Script**: `requests` + `html2text` でブラウザをバイパス。Batch 1を一瞬で完了。

### 最終成果
- **保存先**: `Forge/Raw/aidb/YYYY/MM/ID.md`
- **マニフェスト**: `Forge/Raw/aidb/_index/manifest.jsonl` (795件)
- **欠損**: 一部のWordPressエラー記事（確認済み）

---

## 🛠️ 次のステップ

収集したMarkdownデータを活用し、ナレッジベース（KB）を構築しました。

## ✅ Phase 5: Knowledge Base 構築完了

Perplexity調査に基づき、Python 3.14環境での課題（ONNX Runtime非互換）を回避し、**Python 3.12 + LanceDB** によるローカルKBを実装しました。

### アーキテクチャ
- **Vector DB**: `LanceDB` (DuckDBベース、軽量、wheel配布)
- **Embedding**: `BGE-small-en-v1.5` (ONNX Runtime)
- **環境**: Python 3.12 (wingetインストール)

### 成果物
- **検索スクリプト**: `scripts/aidb-kb.py`
- **インデックス**: `Raw/aidb/_index/lancedb` (761記事 / 1,331チャンク)
- **利用方法**:
  ```bash
  .venv-kb312\Scripts\python scripts\aidb-kb.py search "プロンプトエンジニアリング"
  ```

### 検証結果
- 日本語クエリによるセマンティック検索が正常に動作
- 検索速度: <100ms
- UTF-8出力対応済み（Windowsコンソール）

1. **Gitコミット**: `Raw/aidb` をリポジトリに保存
2. **チャンク分割**: KB用にテキストを意味のある単位に分割
3. **ベクトル化**: 検索インデックスの作成

---

## 📂 成果物ディレクトリ構造
```
Forge/Raw/aidb/
├── _index/
│   ├── url_list.txt      # 全URLリスト (804件)
│   ├── cookies.json      # セッション情報 (参考)
│   └── manifest.jsonl    # 収集済み記事ログ
└── 2026/
    └── 01/
        ├── 79561.md      # 収集済み記事
        └── ...
```
