# 古いAPI検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- 内部で非推奨関数 `parse_state` を使用しています (Medium) - `create_session` および `get_session` 内で `SessionState.from_string` の代わりに使用されています。
- 古いAPIバージョン `v1alpha` を使用しています (Medium) - `BASE_URL` が `https://jules.googleapis.com/v1alpha` に設定されています。
- 非推奨の型ヒント `Optional[callable]` を使用しています (Low) - `progress_callback` の型定義で `typing.Callable` または `collections.abc.Callable` ではなく組み込み関数 `callable` が使用されています。

## 重大度
Medium
