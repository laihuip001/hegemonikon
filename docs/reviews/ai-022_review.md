# 競合状態検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `batch_execute` メソッドにおいて、多数のタスクを並行実行する際、`create_session` 呼び出しが短期間に集中し、APIのレート制限（Rate Limit）を超過するリスクがあります。
- `create_session` メソッドは 429 エラー発生時に `RateLimitError` を送出しますが、リトライロジックが実装されていません。
- `poll_session` にはバックオフ（リトライ）ロジックがありますが、セッション作成段階（`create_session`）で失敗した場合はこれに到達しません。
- 結果として、`batch_execute` 内の並行タスクが「リソース（API割り当て）」を奪い合い、制限に達した時点で残りのタスクが即座に `FAILED` として処理され、本来実行可能なタスクが失われる競合状態（リソース競合）が発生しています。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
