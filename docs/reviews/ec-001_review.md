# 空入力恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `get_session` において `session_id` が空文字列の場合、URLが `sessions/` となり、意図せずリスト取得エンドポイントを叩く可能性がある。結果としてレスポンス解析でクラッシュする。(High)
- `create_session` において `prompt` や `source` が空文字列の場合のチェックがない。APIエラーになる前にクライアント側で検証すべき。(Medium)
- `poll_session` において `session_id` が空文字列の場合のチェックがない。(Medium)
- `batch_execute` において `tasks` が空リストの場合、`asyncio.gather(*[])` に依存している。明示的に空リストをチェックして即時リターンすべき。(Low)

## 重大度
High
