# Logic ハルシネーション検出者 レビュー
## 対象ファイル: mekhane/symploke/jules_client.py
## 発見事項:
1. **docstringと実装の矛盾 (parse_state)**:
   - docstringには「returning UNKNOWN for unrecognized states」とあるが、実装では `SessionState.IN_PROGRESS` を返している。未知の状態を `IN_PROGRESS` とみなすのは、エラーや承認待ちなどの停止状態を見逃すリスクがある。

2. **承認待ちフローの欠陥 (create_session / poll_session)**:
   - `create_session` は `auto_approve=False` (承認フロー) をサポートしているが、`poll_session` は `COMPLETED` または `FAILED` しか終了条件としていない。
   - 承認待ち状態（例: APIが `WAITING_FOR_APPROVAL` などを返した場合）でセッションが停止しても、クライアントはそれを検知できず、タイムアウトまでポーリングし続けることになる。また、承認を行うメソッドも存在しない。

3. **非効率なセッション管理 (aiohttp.ClientSession)**:
   - `create_session` や `get_session` のたびに `aiohttp.ClientSession()` を作成・破棄している。これではTCPコネクションの再利用（Keep-Alive）ができず、特にポーリング処理においてパフォーマンスが著しく低下する。クラスレベルでセッションを保持すべきである。

## 重大度: High
## 沈黙判定: 発言（要改善）
