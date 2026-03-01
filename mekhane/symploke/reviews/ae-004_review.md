# 関数長の測量士 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context`: 189行（50行超過） [High]
- `postcheck_boot_report`: 145行（50行超過） [High]
- `generate_boot_template`: 134行（50行超過） [High]
- `_load_projects`: 91行（50行超過） [High]
- `_load_skills`: 80行（50行超過） [High]
- `print_boot_summary`: 48行（20行超過） [Medium]
- `main`: 38行（20行超過） [Medium]

## 重大度
High