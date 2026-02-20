# 変数距離分析者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` 内の `handoffs_result` (定義: 246行, 使用: 313行, 距離: 67行) - Low
- `get_boot_context` 内の `ki_result` (定義: 255行, 使用: 323行, 距離: 68行) - Low
- `get_boot_context` 内の `persona_result` (定義: 256行, 使用: 309行, 距離: 53行) - Low
- `get_boot_context` 内の `pks_result` 等の軸結果変数群 (定義: 257-271行, 使用: 328行, 距離: >57行) - Low
- `MODE_REQUIREMENTS` (定義: 441行, 使用: 598行, 距離: 157行) - Low

## 重大度
Low
