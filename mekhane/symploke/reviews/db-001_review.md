# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_skills` 関数内で `skills_dir` をループ処理する際、各イテレーションで `SKILL.md` を読み込んでいます (`skill_md.read_text`)。これはファイルシステムに対するN+1クエリ（Read）であり、スキル数に比例してI/O遅延が増加します。

## 重大度
Critical
