# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`batch_execute` メソッドの `tasks` 辞書の検証欠落**:
  `tasks` リスト内の辞書に必須キー（`prompt`, `source`）が含まれているかどうかの事前検証がありません。
  `bounded_execute` 内の `try` ブロックで `task["prompt"]` にアクセスしており、キーが存在しない場合は `KeyError` が発生します。
  さらに、`except` ブロック内でもエラー情報の構築のために再度 `task["prompt"]` や `task["source"]` にアクセスしているため、ここで再度 `KeyError` が発生し、例外処理自体が失敗してバッチ処理全体がクラッシュする可能性があります。

- **`create_session` メソッドの引数検証欠落**:
  `prompt` や `source` が空文字列でないか、適切な形式であるかの検証が行われていません。API側でエラーになる可能性がありますが、クライアント側で早期に検出すべきです。

- **`JulesClient` 初期化時の `max_concurrent` 検証欠落**:
  `max_concurrent` に負の値や 0 が渡された場合の検証がありません。`asyncio.Semaphore` に不正な値が渡される可能性があります。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
