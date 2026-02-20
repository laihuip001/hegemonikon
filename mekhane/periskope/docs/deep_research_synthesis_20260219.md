# Deep Research 統合レポート — Periskopē 検索強化

> **実施日**: 2026-02-19
> **プロンプト数**: 20 件 (R01-R20)
> **完了**: 19/20 (R19 再リサーチ中)
> **エンジン**: Gemini Deep Research (Deep Researcher カスタム Gem)

---

## エグゼクティブサマリー

20 件の Deep Research を並列実行し、Periskopē の検索強化に必要な技術情報を網羅的に収集した。以下の 7 つの戦略的柱が浮かび上がった:

| # | 戦略的柱 | 関連リサーチ | 優先度 |
|:--|:--------|:-----------|:------|
| 1 | **Vertex AI Search 移行** | R13, R14 | 🔴 最優先 |
| 2 | **SearXNG 多言語・カスタムエンジン** | R05, R17 | 🔴 最優先 |
| 3 | **多言語クエリ翻訳パイプライン** | R06, R07 | 🟡 高 |
| 4 | **ニッチドメイン発見・監視** | R01, R02, R04, R08, R09, R10 | 🟡 高 |
| 5 | **検索品質・公平性メトリクス** | R11, R12, R20 | 🟢 中 |
| 6 | **競合分析・OSS 参考** | R03, R15, R16 | 🟢 中 |
| 7 | **Brave API 最適化・法的リスク** | R18, R19 | 🟢 中 |

---

## 1. ニッチプラットフォーム調査 (R01, R02, R04)

### R01: 日本語ニッチプラットフォーム

- **発見**: 技術知識は「表層流」(Qiita, Zenn) と「深層流」(esa, Scrapbox, 企業テックブログ) に二極化
- **10 プラットフォーム**: API 種別、認証、レート制限、コンテンツ品質を構造化
- **★推奨統合**: esa.io 外部ページ, Scrapbox 公開プロジェクト, NotePM, Crieit
- **SearXNG 統合**: JSON API, RSS アグリゲーション, GraphQL パーサーの 3 パターン

### R02: 中国語圏プラットフォーム

- **構造的課題**: WeChat/小紅書の閉鎖的モバイルエコシステム + CNKI の国家規制 → 標準クローリングで 30% 以下の網羅率
- **推奨アーキテクチャ**: CN2 GIA 回線 + 住宅用プロキシ + TLS 指紋偽装
- **新手段**: Tencent 元宝 (Yuanbao) や Kimi が WeChat 内部検索の「窓」として機能
- **実現可能性**: B (条件付き可能) — 法規制リスクが最大変数

### R04: 英語圏ニッチプラットフォーム

- **Tier S**: LessWrong (合理性/AI安全), nLab (圏論), Substack (長文思考)
- **★最ニッチ**: Machine Learning Street Talk (MLST) — 研究者の「生の思考」
- **隠れた宝庫**: Obsidian Publish, Google Colab 公開ノートブック, PhilPapers

---

## 2. SearXNG 最適化 (R05, R17)

### R05: 多言語検索設定

- **課題**: SearXNG はネイティブに並列多言語検索をサポートしない
- **解決策**: **Engine Aliasing** — 同一エンジンの言語別インスタンスを定義
- **エンジン×言語マトリクス**:
  - 中国語: Bing (desktop) + Baidu/Sogou (mobile)
  - 日本語: Google + Yahoo! JAPAN
- **重み付け**: JA=1.2, ZH=1.5 で英語結果の圧倒を防止

### R17: カスタムエンジン追加

- `searx/engines/` に Python スクリプト配置 + `settings.yml` 登録
- Qiita/Zenn: API v2 優先、フォールバックとして CSS/XPath スクレイピング
- Docker Compose のボリュームマウント手順あり
- `searx.enginelib` を使ったデバッグ方法

---

## 3. 多言語パイプライン (R06, R07)

### R06: クエリ翻訳戦略

- **★推奨**: **Gemini 3 Flash** (低レイテンシ翻訳) + **J-GLOBAL API** (専門用語マッピング)
- **コスト**: $1.20/月 (10k クエリ × 3 言語)
- **レイテンシ**: 3 言語合計 500ms 以下達成可能
- **代替**: multilingual embeddings (text-multilingual-embedding-002) — 意味的マッチングに優位

### R07: 結果統合・重複排除

- **★推奨モデル**: **mE5-large-instruct** (560M パラメータ、CPU 効率良好)
- **融合手法**: **RRF** (Reciprocal Rank Fusion, k=60) — 正規化不要でロバスト
- **CPU 最適化**: ONNX Runtime + INT8 量子化 → メモリ 75% 削減
- **多様性制御**: 言語クォータ制 (JA:3, EN:4, ZH:3) を MMR に組込

---

## 4. ドメイン発見・監視 (R08, R09, R10)

### R08: 学術ドメインマッピング

- **50+ 重要ドメイン特定**:
  - 能動的推論: activeinference.institute, verses.ai
  - 計算精神医学: ucl.ac.uk/gatsby, neurophysics.ucsd.edu
  - 圏論/ACT: appliedcategorytheory.org, ncatlab.org
  - 学術検索: doaj.org, core.ac.uk, base-search.net

### R09: 自動ドメイン発見パイプライン

- **スタック**: Crawl4AI (非同期クローリング) + ONNX DeBERTa (CPU ゼロショット分類) + SQLite ブルームフィルタ
- **品質スコア**: Open PageRank API (無料 1 万 req/時)
- **メモリ制約**: Docker `--memory 1g` + cron 再起動でリーク回避

### R10: ドメイン監視

- **死活監視**: Upptime (HTTP/DNS/SSL チェック)
- **更新検知**: Trafilatura (サイトマップ/RSS/コンテンツハッシュ比較)
- **スパム検知**: Perplexity 分析 + RoBERTa による AI 生成コンテンツ判定
- **可視化**: Grafana Cloud Free Tier

---

## 5. 検索品質・公平性 (R11, R12, R20)

### R11: 公平性メトリクス

- **Source Entropy**: Shannon Diversity Index でソース集中度を検出
- **α-nDCG@10**: トピカルカバレッジ評価の de facto 標準
- **Group Exposure**: マイノリティ言語/ドメイン/視点の可視性保証

### R12: Unknown Unknowns 検出

- **情報空白検出**: DIME/RDIME による潜在的情報ニーズモデル
- **死角検出**: Retrieval Probability Scores (RPS) — インデックス前に検索困難エンティティを予測
- **反事実検索**: CF-GDB フレームワークで「what-if」クエリ

### R20: 運用監視システム

- **SearXNG ネイティブ Prometheus メトリクス** + **n8n** オーケストレーション + **Grafana** 可視化
- **品質メトリクス**: NDCG/MRR を Python 3.11 スクリプトで計算
- **自己修復**: サーキットブレーカーパターン + n8n フォールバック自動切替

---

## 6. 競合分析・OSS 参考 (R03, R15, R16)

### R03: X/Twitter 代替

- **結論**: $5/月予算では X 公式 API は事実上不可能
- **★推奨**: **Bluesky** (AT Protocol API) が主軸 — AI/認知科学の専門家が大規模移行
- **補助**: Nitter セルフホスト、SearXNG メタ検索、Altmetric/Scite.ai

### R15: Perplexity AI 分析

- **アーキテクチャ**: Vespa エンジン + L3 Reranker (XGBoost) + DeepSeek-R1 (Deep Research)
- **Periskopē差別化**: 学術/専門 DB (PubMed, IEEE)、証拠抽出透明性、多言語クロスリファレンス

### R16: OSS AI 検索サーベイ

- **注目プロジェクト**: MindSearch (並列エージェント), LazyGraphRAG (低コストグラフ), Khoj (個人データ RAG)
- **Periskopē向け**: DSPy (パイプライン最適化), LazyGraphRAG (知識管理), SudachiPy (日本語正規化)

---

## 7. Brave API・法的リスク (R18, R19)

### R18: Brave Search API

- **独自インデックス**: 35B+ ページ
- **★Goggles API**: カスタムランキング DSL — 学術ソースのブースト + コンテンツファーム排除
- **LLM Context API**: RAG 向け最適化チャンク
- **推奨プラン**: Pro AI ($9/1k req), 50 RPS

### R19: 法的リスク管理

- ⏳ **リサーチ再開済み、完了待ち**
- 日本法/米国法/EU法/中国法のスクレイピング規制を包括調査中

---

## アクションアイテム（優先順）

| # | アクション | 根拠 | 見積り |
|:--|:---------|:-----|:------|
| 1 | Vertex AI Search Standard Edition 導入 | R14: PSE 2027年1月終了、$60/月で$100クレジット内 | 2日 |
| 2 | SearXNG Engine Aliasing で多言語検索 | R05: 設定例あり、即実装可能 | 1日 |
| 3 | Qiita/Zenn カスタムエンジン追加 | R17: テンプレートコードあり | 1日 |
| 4 | Gemini Flash ベースのクエリ翻訳 | R06: $1.20/月、500ms以下 | 2日 |
| 5 | mE5-large + RRF で結果統合 | R07: CPU対応、ONNX量子化済み | 3日 |
| 6 | Brave Goggles カスタムランキング | R18: DSL で学術ソースブースト | 1日 |
| 7 | 学術ドメインシードリスト作成 | R08: 50+ドメイン特定済み | 0.5日 |
| 8 | Shannon Diversity Index 実装 | R11: ソースバランス定量化 | 1日 |
| 9 | Upptime + n8n 監視パイプライン | R10, R20: 予算$0で500ドメイン監視 | 2日 |
| 10 | Bluesky AT Protocol 統合 | R03: X代替として最有力 | 1日 |

---

*Deep Research Synthesis v1.0 — 2026-02-19 Periskopē Search Enhancement Project*
