# 再試行ロジック評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`create_session` の再試行欠如**: `create_session` メソッドには再試行ロジックが実装されておらず、429 (Rate Limit) や 5xx サーバーエラー、ネットワークエラーが発生した場合に即座に例外を送出します。
- **`get_session` の再試行欠如**: `get_session` 単体では再試行を行いません。
- **`poll_session` のエラーハンドリング不足**: `poll_session` は `RateLimitError` (429) のみを捕捉してバックオフを行いますが、`aiohttp.ClientError` やその他の HTTP エラー (5xx等) は捕捉されず、ポーリングが中断してしまいます。
- **`aiohttp.ClientSession` の非効率な使用**: メソッド呼び出しごとに `ClientSession` を作成・破棄しています。特に `poll_session` ではリクエスト毎にセッションを再作成するためオーバーヘッドがあります。
- **バックオフロジックの改善余地**: `poll_session` 内で `RateLimitError` 発生後の成功時も、増加した `backoff` 時間だけ待機してからリセットが行われる挙動になっています。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
