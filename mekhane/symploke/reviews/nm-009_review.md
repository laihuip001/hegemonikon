# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- (Medium) `_load_projects` 内の `status_icons` は定数として扱われていますが、小文字 (snake_case) です。`STATUS_ICONS` (SCREAMING_SNAKE_CASE) にリネームし、可能であればモジュールレベルに移動すべきです。
- (Medium) `postcheck_boot_report` 内の `adjunction_indicators` は定数定義ですが、小文字 (snake_case) です。`ADJUNCTION_INDICATORS` とすべきです。
- (Medium) 多数のマジックナンバーが放置されています。
    - `_load_projects`: `50` (要約文字数)
    - `_load_skills`: `60` (区切り線長)
    - `get_boot_context`: `200` (コンテキスト長), `5` (表示件数), `timeout=5`
    - `print_boot_summary`: `50` (区切り線長)
    - `generate_boot_template`: `10` (Handoff数), `5` (KI数), `7` (Phase数)
    - `postcheck_boot_report`: `25` (推定Fill数)
- (Medium) マジックストリングの放置: `get_boot_context` 内の `http://localhost:5678/webhook/session-start` は定数化すべきです。

## 重大度
Medium
