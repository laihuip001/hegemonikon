# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `poll_session` メソッド: `while` ループ内で `get_session` を繰り返し実行しており、ループ内クエリ（ポーリング）が発生しています。(Critical)
- `synedrion_review` メソッド: バッチ処理の `for` ループ内で `batch_execute` (HTTPリクエスト群) を実行しており、ループ内クエリが発生しています。(Critical)

## 重大度
Critical
