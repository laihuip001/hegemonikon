# 複数形/単数形の文法官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `active` (121行, 484行): プロジェクトのリストを格納しているが、変数名が形容詞（単数形扱い）になっている。`active_projects` などの複数形名詞が望ましい。 (Medium)
- `dormant` (122行, 485行): プロジェクトのリストを格納しているが、変数名が形容詞（単数形扱い）になっている。`dormant_projects` などの複数形名詞が望ましい。 (Medium)
- `archived` (123行, 486行): プロジェクトのリストを格納しているが、変数名が形容詞（単数形扱い）になっている。`archived_projects` などの複数形名詞が望ましい。 (Medium)
- `related` (429行): Handoff のリストを格納しているが、変数名が形容詞（単数形扱い）になっている。`related_handoffs` などの複数形名詞が望ましい。 (Medium)

## 重大度
Medium
