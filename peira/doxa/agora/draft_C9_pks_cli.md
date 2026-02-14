# 34,085 ドキュメントを統合検索する CLI

> **ID**: C9
> **想定媒体**: Zenn（技術記事）
> **想定読者**: Agent 開発者、DevOps
> **フック**: 1つのコマンドで論文・KI・Handoff・チャットログを横断検索

---

## リード文（案）

知識は分散する。論文、メモ、チャットログ、引き継ぎ書。
それぞれ別のフォーマット、別の場所、別のツール。

PKS (Polis Knowledge System) は、これらを **1 つの CLI** で統合検索する。

```bash
pks search "active inference"
```

34,085 ドキュメントから、関連度順に結果が返る。

---

## 本文構成（案）

### 1. 4つの知識ソース

| ソース | 内容 | ドキュメント数 |
|:-------|:-----|:-------------|
| Gnōsis | 論文 | 596 |
| Sophia (KI) | 永久知識 | ~200 |
| Kairos (Handoff) | セッション引き継ぎ | ~100 |
| Chronos | 時系列ログ | ~33,000 |

### 2. PKS CLI

```bash
pks stats          # 統計情報
pks health         # 9項目ヘルスチェック
pks search "query" # 統合検索
pks rebuild        # インデックス再構築
```

### 3. 統合検索のアーキテクチャ

```
クエリ → BGE-small で埋め込み
  → Gnōsis インデックス検索 (k=5)
  → Sophia インデックス検索 (k=5)
  → Kairos インデックス検索 (k=5)
  → スコアでマージ+ランキング
  → Top-K 結果を返す
```

### 4. ヘルスチェック

```
pks health
✅ Gnōsis: 596 papers, index OK
✅ Sophia: 200 KIs, index OK
⚠️ Kairos: 100 handoffs, 3 corrupted
✅ Chronos: 33,000 docs, index OK
...
```

### 5. 読者が試せること

- 複数の Markdown フォルダを BGE-small で埋め込み
- それぞれの検索結果をスコアでマージ
- CLI ラッパーを argparse で作成

---

*ステータス: たたき台*
*関連: C1 (4層メモリ), C6 (ローカル検索), C7 (論文消化)*
