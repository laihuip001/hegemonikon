# スタイル不整合検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **言語の不整合**: `mekhane/symploke/` 以下の既存ファイル（`config.py`, `factory.py`など）はdocstringやコメントが日本語で記述されているのに対し、本ファイルは全て英語で記述されている。
- **アーキテクチャ/パフォーマンス**: `aiohttp.ClientSession` が `create_session` および `get_session` メソッド呼び出しごとに生成・破棄されている。これは "Async client" や "Batch execution" を謳うクライアントとしては非効率（コネクションプールが効かない）であり、ベストプラクティスに反する。
- **ハードコード**: APIのBase URL (`https://jules.googleapis.com/v1alpha`) がハードコードされており、`config.py` などの設定システムと統合されていない。
- **ロジック**: `poll_session` 内のバックオフ制御において、レート制限時のバックオフ変数が通常のポール間隔スリープにも影響し、成功後のリセットロジックもスリープ後に行われるため、挙動が直感的でない可能性がある。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
