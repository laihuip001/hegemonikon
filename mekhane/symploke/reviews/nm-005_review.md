# 意味なき名の追放者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `data` の使用 (`_load_projects` 内など)
- `info` の使用 (`SERIES_INFO`, `dispatch_info` など)
- `result` の使用 (`result`, `handoffs_result`, `ki_result` など各軸のロード結果や関数の戻り値として多用されている)

## 重大度
Medium