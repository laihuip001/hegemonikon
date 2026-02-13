# private接頭辞の監視者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `mask_api_key` はモジュール内部で使用されるユーティリティ関数ですが、公開関数として定義されています。`_mask_api_key` とすべきです。 (Medium)
- `with_retry` は `JulesClient` のメソッドに使用される内部デコレータですが、公開されています。外部APIとして意図されていない場合は `_with_retry` とすべきです。 (Medium)

## 重大度
Medium
