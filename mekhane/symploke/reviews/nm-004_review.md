# 複数形/単数形の文法官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- List変数が単数形（形容詞）になっている (`_load_projects` 内): `active`, `dormant`, `archived` → `active_projects`, `dormant_projects`, `archived_projects` (Medium)
- List変数が単数形（形容詞）になっている (`generate_boot_template` 内): `active`, `dormant`, `archived` → `active_projects`, `dormant_projects`, `archived_projects` (Medium)
- List変数が単数形（形容詞）になっている (`generate_boot_template` 内): `related` → `related_handoffs` (Medium)

## 重大度
Medium
