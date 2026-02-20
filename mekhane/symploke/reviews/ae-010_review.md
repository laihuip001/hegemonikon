# 空行の呼吸師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 関数 `_load_skills` の直前に空行が1行しかありません（基準: 2行） (Low)
- 関数 `get_boot_context` の直前に空行が1行しかありません（基準: 2行） (Low)
- `get_boot_context` 内の論理ブロック間（Blockers処理後と未完了タスク処理前）に空行がありません（基準: 1行） (Low)
- 関数 `print_boot_summary` の直前に過剰な空行（3行以上）があります (Low)
- `postcheck_boot_report` 内の論理ブロック間（Check 5 終了後と Check 6 開始前）に空行がありません（基準: 1行） (Low)

## 重大度
Low
