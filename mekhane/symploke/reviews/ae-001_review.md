# 空白の調律者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- インデント混在: モジュール docstring 内のリスト（行 7-10, 13）で 2 spaces インデントが使用されている（他は 4 spaces で統一）。 (High)
- 論理ブロック間の呼吸（空行の過不足）:
    - 過多: `extract_dispatch_info` 直前（行 77-79, 3行）、`print_boot_summary` 直前（行 467-470, 4行）。通常は 2 行が適切。 (Low)
    - 不足: `generate_boot_template` 直前（行 449, 1行）、`postcheck_boot_report` 直前（行 704, 1行）。トップレベル関数定義の前には 2 行の空行が必要。 (Low)

## 重大度
High
