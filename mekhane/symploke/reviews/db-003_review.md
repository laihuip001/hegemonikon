# SELECT * 反対者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_skills` 関数において、`SKILL.md` の全文 (`body`) を取得し `skills` リストの各要素に格納しているが、これは `formatted` 出力以外では使用されていない不必要なデータ取得である (Medium)
- `_load_projects` 関数において、`registry.yaml` の全フィールドを含むプロジェクト辞書をそのまま返却しており、利用側で必要なフィールドに限定していない (Medium)

## 重大度
Medium
