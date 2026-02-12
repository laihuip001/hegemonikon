# private接頭辞の監視者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `mask_api_key` (Medium): モジュールレベルの関数であるが、`main`関数（テスト用CLI）でのみ使用されており、外部公開APIの一部ではないと思われる。`_mask_api_key` とすべき。
- `with_retry` (Medium): モジュールレベルのデコレータであるが、`JulesClient` クラス内部でのみ使用されている（およびテスト）。汎用ユーティリティとして公開する意図がなければ `_with_retry` とすべき。
- `parse_state` (Low): レガシーエイリアスとして残されているが、実質的に内部利用のみであれば可視性を下げることを検討すべき（非推奨の旨が記載されているためLow）。

## 重大度
Medium
