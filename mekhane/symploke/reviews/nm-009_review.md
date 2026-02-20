# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 内の変数 `status_icons` (L132) は定数として扱われているが、snake_case である。`STATUS_ICONS` にすべきである。(Medium)
- `extract_dispatch_info` 内のスライス `[:3]` (L89) はマジックナンバーである。(Medium)
- `_load_projects` 内のパス `".agent/projects/registry.yaml"` (L105) はマジックストリングである。(Medium)
- `_load_projects` 内の要約長 `50` (L140) はマジックナンバーである。(Medium)
- `_load_skills` 内のパス `".agent/skills"` (L169) はマジックストリングである。(Medium)
- `get_boot_context` 内の URL `"http://localhost:5678/webhook/session-start"` (L318) はマジックストリングである。(Medium)

## 重大度
Medium
