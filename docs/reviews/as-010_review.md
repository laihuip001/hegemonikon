# シグナルハンドリング評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `batch_execute` メソッドで `asyncio.gather` が使用されています。
  - プロジェクトの推奨事項（Python 3.11+ `asyncio.TaskGroup` の使用）に反しています。
  - `asyncio.gather` は `CancelledError` を即座に伝播させるため、シャットダウン時に完了済みのタスクの結果を取得したり、実行中のタスクに対して適切なクリーンアップ処理を行うことが困難です。
- `bounded_execute` 内で `Exception` のみを捕捉しており、`asyncio.CancelledError` に対するハンドリングがありません。
  - キャンセル時にログ出力や、必要に応じたサーバーサイドセッションのキャンセル処理が行われません。
- クライアント側で中断が発生した場合でも、サーバー側（Google Jules API）のセッションは継続します。これを制御（キャンセル送信など）するオプションやロジックが含まれていません。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
