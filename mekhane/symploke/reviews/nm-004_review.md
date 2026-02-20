# 複数形/単数形の文法官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 内の変数 `active`, `dormant`, `archived` はリストを格納しているが単数形（形容詞）である (Medium)
- `generate_boot_template` 内の変数 `active`, `dormant`, `archived` はリストを格納しているが単数形（形容詞）である (Medium)

## 重大度
Medium
