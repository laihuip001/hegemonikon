# シグナルハンドリング評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `batch_execute` メソッドにおいて `asyncio.gather` が使用されており、Python 3.11+ で推奨される `asyncio.TaskGroup`（構造化された並行性）が採用されていません。`gather` は例外発生時のタスクライフサイクル管理が `TaskGroup` に比べて脆弱です。
- `poll_session` および `batch_execute` 内で `asyncio.CancelledError` に対する明示的なハンドリングやクリーンアップ処理（例：サーバー側セッションのキャンセル要求、ログ出力）が存在しません。クライアントが中断（SIGINT等）された場合、サーバー上に「ゾンビセッション」が残る可能性があります。
- クライアントが `create_session` リクエスト中に中断された場合、サーバー側ではセッションが作成されてもクライアント側では ID を把握できず、追跡不能な状態になるリスクがあります。
- `__main__` ブロックやクライアントのライフサイクルにおいて、OSシグナル（SIGINT, SIGTERM）をフックして `aiohttp.ClientSession` を安全に閉じる等のグレースフルシャットダウン機構が実装されていません。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
