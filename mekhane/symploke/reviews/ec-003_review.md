# 境界値テスター レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `mask_api_key` に `visible_chars=0` を渡すと、キー全体が露出する (High)
  - Pythonのスライス仕様により `key[-0:]` は `key[0:]` と同義となり、全文字列が返される。
- `with_retry` に `max_attempts <= 0` を渡すと `TypeError` または `UnboundLocalError` (Medium)
  - ループが一度も回らず、`raise last_exception` で `None` を raise しようとするか、未定義変数参照となる。
- `batch_execute` に `max_concurrent=0` を渡すとデッドロック (Medium)
  - `asyncio.Semaphore(0)` で初期化され、一度も `acquire` できずに永遠に待機する。
- `synedrion_review` で `MAX_CONCURRENT` が 0 の場合 `ZeroDivisionError` (Medium)
  - バッチ数計算 `(len(tasks) + batch_size - 1) // batch_size` で除算エラーが発生する。
- `RateLimitError` の `retry_after` が数値以外のヘッダー値を考慮していない (Low)
  - HTTP仕様では日付形式も許可されているが、`int()` キャストで `ValueError` の可能性がある。

## 重大度
High
