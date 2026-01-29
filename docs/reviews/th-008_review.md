# 変分自由エネルギー評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **構造化並行処理の欠如**: Python 3.11+推奨の `asyncio.TaskGroup` ではなく `asyncio.gather` が使用されています。これにより、タスクのライフサイクル管理が緩くなり、例外処理やキャンセル時の挙動において「驚き（Surprise）」= 自由エネルギーが増大するリスクがあります。
- **設定のエントロピー増大**: `BASE_URL` や `MAX_CONCURRENT` などの定数がハードコードされており、`SymplokeConfig` などの統合設定から分離しています。これはシステムの予測可能性を下げ、複雑性を増大させています。
- **キャンセル処理の死角**: `batch_execute` 内の `bounded_execute` は `Exception` のみを捕捉しており、Python 3.8+ で `BaseException` となった `asyncio.CancelledError` を捕捉しません。これにより、キャンセル時にバッチ処理全体が不整合な状態（高い自由エネルギー状態）に陥る可能性があります。
- **観測精度の低下**: `poll_session` メソッドが `PLANNING` や `IMPLEMENTING` といった中間状態をマスクし、完了か失敗のみを返しています。これは外部からの状態推定の精度（Accuracy）を低下させています。
- **不要な複雑性**: ライブラリファイル内に `if __name__ == "__main__":` によるCLIコードが含まれています。責務の分離が不十分です。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
