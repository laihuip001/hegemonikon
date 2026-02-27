# 複数形/単数形の文法官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Line 118: `active` (list) -> 複数形であるべき (e.g., `active_projects`)
- Line 119: `dormant` (list) -> 複数形であるべき (e.g., `dormant_projects`)
- Line 120: `archived` (list) -> 複数形であるべき (e.g., `archived_projects`)
- Line 304: `incomplete` (list) -> 複数形であるべき (e.g., `incomplete_entries`)
- Line 459: `related` (list) -> 複数形であるべき (e.g., `related_handoffs`)
- Line 516: `active` (list) -> 複数形であるべき (e.g., `active_projects`)
- Line 517: `dormant` (list) -> 複数形であるべき (e.g., `dormant_projects`)
- Line 518: `archived` (list) -> 複数形であるべき (e.g., `archived_projects`)
- Line 568: `handoff_refs` (int) -> 単数形であるべき (e.g., `handoff_ref_count`)

## 重大度
Medium
