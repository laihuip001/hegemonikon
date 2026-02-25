# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Critical: `_load_skills` 関数内 (L180-L186) で `skills_dir.iterdir()` のループ毎に `skill_md.read_text()` を実行しており、スキル数に比例したファイルI/Oが発生している（File System N+1）。`registry.yaml` のような一括管理、あるいは並列読み込みを検討すべき。

## 重大度
Critical
