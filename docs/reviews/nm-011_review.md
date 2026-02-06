# private接頭辞の監視者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry` はモジュール内部でのみ使用されるデコレータですが、private接頭辞（`_`）が不足しています。(Medium)
- `mask_api_key` はモジュール内部（`main`関数内）でのみ使用されるユーティリティ関数ですが、private接頭辞（`_`）が不足しています。(Medium)

## 重大度
Medium
