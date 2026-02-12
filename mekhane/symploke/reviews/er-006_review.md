# tryブロック最小化者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `_request`メソッド (L285-307): tryブロックが約20行と長く、ヘッダー準備、トレース注入、リクエスト、レスポンス処理と複数の例外発生源を含んでいます。 (Medium)
- `poll_session`メソッド (L397-434): tryブロックが約30行と長く、`get_session`呼び出し以外のロジック（状態確認、ログ出力、例外送出）も含まれています。 (Medium)
- `bounded_execute`内部関数 (L496-508): tryブロックが10行を超えており、`create_session`と`poll_session`という複数の例外発生源を含んでいます。 (Medium)

## 重大度
Medium
