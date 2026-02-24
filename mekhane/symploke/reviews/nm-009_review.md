# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Medium: `_load_projects` 内の `status_icons` (L144) が小文字です。静的なマッピングのため `STATUS_ICONS` とすべきです。
- Medium: `_load_projects` 内の `50` (L149) がマジックナンバーです。プロジェクトサマリーの切り詰め長さを定数化すべきです。
- Medium: `get_boot_context` 内の `200` (L253) がマジックナンバーです。コンテキストプレビュー長を定数化すべきです。
- Medium: 複数の箇所で使用される `5` (L301, L347, L349) がマジックナンバーです。リスト表示件数を定数化すべきです。
- Medium: `get_boot_context` 内の `http://localhost:5678/webhook/session-start` (L359) がハードコードされています。`N8N_WEBHOOK_URL` 等の定数にすべきです。
- Medium: `postcheck_boot_report` 内の `adjunction_indicators` (L580) が小文字です。判定ロジックの定義であり定数化が望ましいです。

## 重大度
Medium
