# キャンセレーション処理評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **リモートセッションのクリーンアップ欠如**: `create_and_poll` や `batch_execute` の実行中に `asyncio.CancelledError` が発生した際、ローカルの処理は中断されますが、Jules API 上で既に作成されたセッションに対してキャンセル要求が送信されません。これにより、ユーザーが処理を中断してもリモートで処理が継続し、リソースリーク（Zombie Session）や不要なコストが発生するリスクがあります。
- **`bounded_execute` の例外ハンドリング**: `bounded_execute` 内で `except Exception` を使用しており、`CancelledError` (BaseException) は正しく伝播されますが、`finally` ブロック等によるクリーンアップ処理（上記のリモートキャンセルなど）が実装されていません。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
