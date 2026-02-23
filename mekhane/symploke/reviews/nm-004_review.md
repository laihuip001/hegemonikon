# 複数形/単数形の文法官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **形容詞の単数形変数がリストとして使用されている (Medium)**:
  - `active` (L125, L674): プロジェクトのリスト -> `active_projects` などを推奨
  - `dormant` (L126, L675): プロジェクトのリスト -> `dormant_projects` などを推奨
  - `archived` (L127, L676): プロジェクトのリスト -> `archived_projects` などを推奨
  - `incomplete` (L347): 未完了タスクのリスト -> `incomplete_tasks` などを推奨
  - `related` (L593): 関連Handoffのリスト -> `related_handoffs` などを推奨

## 重大度
Medium
