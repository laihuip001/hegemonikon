# 複数形/単数形の文法官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数:
    - リスト変数 `active` は形容詞であり、単数・複数の区別が曖昧です。`active_projects` とすべきです (Medium)。
    - リスト変数 `dormant` は形容詞であり、単数・複数の区別が曖昧です。`dormant_projects` とすべきです (Medium)。
    - リスト変数 `archived` は形容詞であり、単数・複数の区別が曖昧です。`archived_projects` とすべきです (Medium)。
- `get_boot_context` 関数:
    - リスト変数 `incomplete` は形容詞であり、単数・複数の区別が曖昧です。`incomplete_tasks` または `incomplete_entries` とすべきです (Medium)。
- `generate_boot_template` 関数:
    - リスト変数 `related` は形容詞であり、単数・複数の区別が曖昧です。`related_handoffs` とすべきです (Medium)。
    - リスト変数 `active` は形容詞であり、単数・複数の区別が曖昧です。`active_projects` とすべきです (Medium)。
    - リスト変数 `dormant` は形容詞であり、単数・複数の区別が曖昧です。`dormant_projects` とすべきです (Medium)。
    - リスト変数 `archived` は形容詞であり、単数・複数の区別が曖昧です。`archived_projects` とすべきです (Medium)。

## 重大度
Medium
