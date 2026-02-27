<!-- PROOF: [L2/Review] <- mekhane/symploke/reviews/ -->
# 関数長の嘆き手 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context`: 189行 (High) - 50行制限を大幅に超過
- `postcheck_boot_report`: 145行 (High) - 50行制限を大幅に超過
- `generate_boot_template`: 134行 (High) - 50行制限を大幅に超過
- `_load_projects`: 91行 (High) - 50行制限を超過
- `_load_skills`: 80行 (High) - 50行制限を超過
- `print_boot_summary`: 48行 (Medium) - 20行制限を超過
- `main`: 38行 (Medium) - 20行制限を超過

## 重大度
High
