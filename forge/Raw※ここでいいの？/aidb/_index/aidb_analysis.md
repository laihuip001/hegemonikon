# AIDB アーキテクチャ分析レポート

## 調査日: 2026-01-18
## 目的: Forge KB化エコシステムのロールモデルとして分析
## ソース: browser_subagent分析 + Perplexityリサーチ統合

---

## Phase配置マトリクス（最適解）

| Phase | タスク | Antigravity | 手動 |
|-------|--------|-------------|------|
| 1 | 環境準備 | ✅ | - |
| 2 | URL収集（sitemap解析） | ✅ | - |
| 3 | MD保存 | ✅ | Cookie初回 |
| 4 | メタコミット | ✅ | - |
| 5 | KB抽出 | ✅ | CEO判断 |
| 6 | 論文監視 | ✅ | - |

---

## 1. サイト基本情報

| 項目 | 内容 |
|------|------|
| URL | https://ai-data-base.com |
| CMS | WordPress |
| SEOプラグイン | All in One SEO v4.9.3 |
| 運営 | Parks, Inc. |
| ビジネスモデル | Freemium（🔒プレミアム記事は有料会員限定） |

---

## 2. コンテンツ構造

### カテゴリ（大分類）
| カテゴリ | パス | 内容 |
|----------|------|------|
| 深堀り解説 | `/archives/category/deep-dive` | 個別論文の詳細解説 |
| 注目論文まとめ | `/archives/category/weekly-papers` | 週次の論文リスト |
| その他 | `/archives/category/uncategorized` | 未分類 |

### タクソノミー（3層タグシステム）※模倣推奨

#### tech_tag（技術タグ）
- llm, prompt, llm-agent, rag, coding, persona-simulation
- safety-2, オープンソース, multimodal, 画像認識
- finetuning, hallucination, セキュリティ, 画像生成, 音声

#### type_tag（論文種別タグ）
- method（手法）
- survey（サーベイ）
- analysis（分析）
- empirical（実証）
- position（ポジションペーパー）
- resource（ベンチマーク・リソース）
- technical-report（テクニカルレポート）

#### app_tag（応用分野タグ）
- healthcare-2, society, entertainment-art
- manufacturing-technology, finance, education
- ロボット, se（ソフトウェアエンジニアリング）

---

## 3. 技術インフラ

### データ取得方法
| 方法 | URL/パス | 用途 |
|------|----------|------|
| RSS Feed | `/feed` | 最新記事の自動取得 |
| Sitemap | `/sitemap.xml` | 全URL一覧 |
| Post Sitemap | `/post-sitemap.xml` | 記事URL一覧（254チャンク = 推定700-1000件） |
| robots.txt | `/robots.txt` | クローラー許可範囲 |

### robots.txt内容
```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

Sitemap: https://ai-data-base.com/sitemap.xml
Sitemap: https://ai-data-base.com/sitemap.rss
```
※ `/archives/`へのアクセスは明示的に禁止されていない

---

## 4. 記事メタデータ構造

### HTML要素（browser_subagent分析より）
| 要素 | 抽出方法 |
|------|----------|
| タイトル | `<h1>` または `og:title` |
| 日付 | `YYYY.MM.DD` 形式、`<time>` タグ |
| カテゴリ | クラス `.category` |
| プレミアム判定 | タイトル先頭の `🔒` または `.premium-badge` |
| 著者 | RSS: `AIDB Research` |

### Frontmatter設計（Forge用）
```yaml
source_url: https://ai-data-base.com/archives/XXXXX
captured_at: 2026-01-18T12:00:00+09:00
title: "記事タイトル"
category: "deep-dive" | "weekly-papers"
is_premium: true | false
publish_date: 2026-01-17
tech_tags: [llm, prompt, rag]
type_tag: method | survey | analysis
app_tags: [education, se]
```

---

## 5. 模倣すべき機構

### 5.1 3層タクソノミー
**AIDBの強み**: tech_tag（技術）× type_tag（論文種別）× app_tag（応用）の組み合わせで多角的な検索が可能

**Forge適用案**:
```yaml
# taxonomy.yaml
tech_tags: [llm, prompt, rag, agent, safety, reasoning, eval]
type_tags: [technique, framework, case_study, benchmark]
task_tags: [critical_review, summarize, extract, generate]
```

### 5.2 週次まとめ形式
**AIDBの強み**: 「今週の注目AI論文リスト」として週次で論文をキュレーション

**Forge適用案**:
- `Raw/aidb/_index/weekly_digest.jsonl` で週次の新着を記録
- 将来的にarXivからの自動収集でも同形式を採用

### 5.3 プレミアム/無料の二層構造
**AIDBの強み**: 無料でイントロ・キーポイントを公開、深堀りは有料

**Forge適用案**:
- `Refined/`（公開）: 要約・Indexカード
- `Raw/`（非公開）: 全文

### 5.4 RSSベースの更新監視
**AIDBの強み**: `/feed` でRSS 2.0形式での購読が可能

**Forge適用案（将来）**:
- arXiv/OpenReview等のRSSを監視
- 差分検知して自動取得

---

## 6. URL収集の最適解

### 方法比較
| 方法 | 精度 | 速度 | 推奨 |
|------|------|------|------|
| アーカイブページ巡回 | 高 | 遅い | △ |
| `/post-sitemap.xml` 解析 | 高 | 速い | ✅ |
| RSS `/feed` | 低（最新のみ） | 最速 | ×（全件取得不可） |

**結論**: `/post-sitemap.xml` を解析して全記事URLを取得するのが最速・最確実

---

## 7. 私の見解

### プロジェクトの妥当性
AIDBをロールモデルとする判断は**正しい**。彼らが解決している問題（論文→構造化DB→検索可能なKB）は、まさにあなたが目指すエコシステムと同一。

### 差分ポイント
| AIDB | あなたのエコシステム |
|------|----------------------|
| 人間向け | AI向け |
| 公開メディア | 私用KB |
| 人間編集 | 自動抽出（LLM） |
| 検索は人間操作 | ルーティングは自動 |

### 技術的に模倣すべき点
1. **3層タクソノミー** - そのまま採用
2. **週次ダイジェスト形式** - 論文移行時に採用
3. **sitemap.xmlベースの全件取得** - 今すぐ採用可能

### 実装優先順位
1. `/post-sitemap.xml`から全URL取得（browser_subagentで）
2. 各記事ページをスクレイピング
3. タクソノミーをFrontmatterに反映
4. KB抽出時に3層タグを付与
