# private接頭辞の監視者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `generate_boot_template` メソッドはモジュール内およびテストからのみ使用されており、外部公開APIではないため `_generate_boot_template` とすべきです (Medium)
- `extract_dispatch_info` メソッドは `boot_axes.py` から使用されていますが、同様に使用されている `_load_projects` が private であることと整合性が取れていません。テスト用であれば `_extract_dispatch_info` とし、公開APIであればドキュメントに明記すべきです (Low)

## 重大度
Medium
