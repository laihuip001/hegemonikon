# Logic ハルシネーション検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **Batch ExecutionにおけるSession IDの喪失**: `batch_execute` メソッド内で、`create_and_poll` が失敗（例: タイムアウト）した際、例外が捕捉され `JulesSession` が返されるが、その `id` フィールドは空文字列となる。セッション自体はサーバー上で作成されている可能性があるため、呼び出し元がそのセッションを追跡・調査・クリーンアップする手段を失うことになる。
- **未知のセッション状態による無限ポーリング**: `parse_state` 関数は未知の状態文字列を `SessionState.IN_PROGRESS` にマッピングする。もしAPIが新しい終端状態（例: "CANCELLED", "REJECTED"）を返した場合、`poll_session` はそれをアクティブな状態と誤認し、タイムアウトまで無駄にポーリングを継続してしまう。
- **非効率なバックオフ復帰ロジック**: `poll_session` において、エラー発生時に `backoff` が増加（例: 60秒）した後、次のポーリングが成功しても、その成功した回の待機時間として増加した `backoff`（60秒）が使用されてしまう。成功時は即座に、あるいは通常の `poll_interval` で待機すべきである。
- **接続管理の非効率性**: 各リクエスト（`create_session`, `get_session`）ごとに新しい `aiohttp.ClientSession` を作成しており、コネクションプーリングの利点を活かせていない。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
