# 境界値テスター レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry` デコレータにおいて、`max_attempts=0` を指定すると `last_exception` が `None` のまま `raise` され、`TypeError` が発生します（0回の試行という境界値のハンドリング不備）。
- `poll_session` メソッドにおいて、`timeout=0` を指定すると、ループ条件 `time.time() - start_time < timeout` が最初から False となり、APIリクエストを一度も行わずに `TimeoutError` が発生します（0秒という境界値の挙動）。
- `batch_execute` メソッドにおいて、`max_concurrent=0` を指定すると `asyncio.Semaphore(0)` が作成され、タスクが永遠に待機（デッドロック）します（同時実行数0という境界値のハンドリング不備）。
- `_request` メソッドにおいて、`Retry-After` ヘッダーが整数以外の数値文字列（例: "1.5"）の場合、`int()` 変換で `ValueError` が発生する可能性があります（型変換の境界値）。

## 重大度
Medium
