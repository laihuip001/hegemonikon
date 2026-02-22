# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Medium**: `status_icons` (line 128, 435) は定数的なマッピングだが、SCREAMING_SNAKE_CASE ではなく snake_case で定義されている。本来は `STATUS_ICONS` とすべきである。
- **Medium**: マジックナンバーの散在
  - `50` (line 133): summary truncation length
  - `5` (line 332): timeout
  - `3` (line 110): alternative count
  - `2` (line 379): theorem suggestion count
  - `24` (line 384): total theorem count
  - `100` (line 384): percentage calculation
  - `10` (line 462): handoff count
  - `25` (line 622): estimated fill count
- **Low**: マジックストリングの散在
  - プロジェクトステータス: `"active"`, `"dormant"`, `"archived"`, `"planned"` が複数回ハードコードされている。
  - ファイルパス: `".agent/projects/registry.yaml"`, `".agent/skills"`, `"/tmp/boot_report_..."`
  - URL: `"http://localhost:5678/webhook/session-start"`

## 重大度
Medium
