# プロパティ審判 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesClient._session` (Medium): このプロパティはアクセスされるたびに新しい `aiohttp.ClientSession` インスタンスを作成する可能性があります（副作用）。`_shared_session` と `_owned_session` が共に `None` の場合、戻り値のセッションは管理されず、リソースリーク（未クローズのセッション）の原因となります。プロパティは冪等であるべきですが、この実装は副作用を持ち、かつ危険です。

## 重大度
Medium
