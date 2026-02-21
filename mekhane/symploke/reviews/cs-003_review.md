# メソッド順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- protected関数 (`_load_projects`, `_load_skills`) が public関数 (`get_boot_context`, `print_boot_summary`) よりも先に定義されています (Low)
- public関数 (`extract_dispatch_info`) の直後に protected関数が配置され、その後に再び public関数が続くため、順序が混在しています (Low)

## 重大度
Low
