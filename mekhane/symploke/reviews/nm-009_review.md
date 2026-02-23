# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `status_icons` (L135) は辞書リテラルとして定義されていますが、本来は `STATUS_ICONS` としてモジュールレベルの定数にすべきです (Medium)。
- マジックナンバーが多数存在します (Medium):
  - L140: `50` (サマリーの最大長)
  - L219: `200` (KIコンテキストのフォールバック長)
  - L257, L285, L287, L303, L325, L424, L435, L446: `5`, `2`, `10`, `6` などのハードコードされた数値制限
  - L332: `24` (定理総数)
  - L459: `7` (フェーズ数)
  - L551: `25` (推定FILL数)
- マジックストリングの多用 (Medium):
  - `mode` の値 (`"fast"`, `"standard"`, `"detailed"`) が複数箇所でリテラルとして使用されています。
  - プロジェクトステータス (`"active"`, `"dormant"`, `"archived"`) が複数箇所でリテラルとして使用されています。
  - URL `"http://localhost:5678/webhook/session-start"` (L297)
  - パス `".agent/projects/registry.yaml"`, `".agent/skills"`, `"/tmp/boot_report..."`

## 重大度
Medium
