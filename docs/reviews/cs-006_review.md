# プロパティ審判 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesClient._session` (@property)
    - **問題**: 副作用あり（セッション作成）。
    - **詳細**: `self._shared_session` および `self._owned_session` が None の場合、アクセスするたびに新しい `aiohttp.ClientSession` インスタンスを作成して返します。作成されたセッションは保持されないため、呼び出し側で適切に閉じないとリソースリーク（TCPコネクション等）の原因となります。また、アクセスごとに異なるオブジェクトを返すため、プロパティの冪等性も欠いています。
    - **重大度**: Medium
- `JulesResult.is_success` / `JulesResult.is_failed`
    - **良好**: 純粋な計算値であり、副作用のない適切な @property の使用例です。

## 重大度
Medium
