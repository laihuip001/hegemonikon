# 多様性包摂性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **技術的排除 (Technical Exclusion):** `sourceContext` 内で `githubRepoContext` がハードコードされており、GitHub 以外のバージョン管理システム（GitLab, Bitbucket 等）を使用するユーザーを排除している。また、ディレクトリ構造 (`sources/github/...`) も特定の環境を仮定している。
- **社会的排除 (Social Exclusion):** "Hegemonikón", "Symplokē", "Synedrion", "Ergasterion" といった説明のないギリシャ語由来の専門用語や、`cl-003`, `th-003` といったコンテキスト不明なレビューIDが多用されており、新規参入者や外部の貢献者に対して高い心理的障壁（部族的な知識の要求）を作り出している。
- **経済的仮定 (Economic Assumptions):** `MAX_CONCURRENT = 60` のコメントに "Ultra plan limit" とあり、ユーザーが高額なプランを利用していることを暗黙の前提としている。低価格プランや無料プランのユーザーに対する配慮（自動調整や警告）がなく、意図しないレート制限違反やアカウント停止のリスクを負わせている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
